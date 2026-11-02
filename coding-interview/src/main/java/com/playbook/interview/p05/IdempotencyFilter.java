package com.playbook.interview.p05;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.stereotype.Component;
import org.springframework.util.DigestUtils;
import org.springframework.web.filter.OncePerRequestFilter;
import org.springframework.web.util.ContentCachingRequestWrapper;
import org.springframework.web.util.ContentCachingResponseWrapper;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.ConcurrentHashMap;

/** Problem 5: replay the stored response for a repeated Idempotency-Key; reject key reuse with a different body. */
@Component
class IdempotencyFilter extends OncePerRequestFilter {

    record StoredResponse(String bodyHash, int status, String contentType, byte[] body) { }

    private static final StoredResponse IN_PROGRESS = new StoredResponse("", 0, null, new byte[0]);
    private final ConcurrentHashMap<String, StoredResponse> store = new ConcurrentHashMap<>();   // production: Redis/DB with TTL

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        return !(request.getMethod().equals("POST") && request.getRequestURI().startsWith("/p05/"));
    }

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain) throws ServletException, IOException {
        String key = req.getHeader("Idempotency-Key");
        if (key == null || key.isBlank()) { res.sendError(400, "Idempotency-Key header is required"); return; }

        byte[] requestBody = req.getInputStream().readAllBytes();
        String hash = DigestUtils.md5DigestAsHex(requestBody);
        StoredResponse previous = store.putIfAbsent(key, IN_PROGRESS);           // atomic claim
        if (previous == IN_PROGRESS) { res.sendError(409, "a request with this Idempotency-Key is in progress"); return; }
        if (previous != null) {
            if (!previous.bodyHash().equals(hash)) { res.sendError(422, "Idempotency-Key reused with a different body"); return; }
            res.setStatus(previous.status());
            res.setContentType(previous.contentType());
            res.setHeader("Idempotent-Replayed", "true");
            res.getOutputStream().write(previous.body());
            return;
        }

        var cachedRequest = new ReplayableRequest(req, requestBody);
        var cachedResponse = new ContentCachingResponseWrapper(res);
        try {
            chain.doFilter(cachedRequest, cachedResponse);
            if (cachedResponse.getStatus() >= 500) store.remove(key);               // let the client retry transient failures
            else store.put(key, new StoredResponse(hash, cachedResponse.getStatus(), cachedResponse.getContentType(), cachedResponse.getContentAsByteArray()));
            cachedResponse.copyBodyToResponse();
        } catch (RuntimeException | ServletException | IOException e) {
            store.remove(key);
            throw e;
        }
    }

    /** The body was already read for hashing, so give the controller a fresh stream over the same bytes. */
    static final class ReplayableRequest extends jakarta.servlet.http.HttpServletRequestWrapper {
        private final byte[] body;
        ReplayableRequest(HttpServletRequest req, byte[] body) { super(req); this.body = body; }
        @Override public jakarta.servlet.ServletInputStream getInputStream() {
            var in = new java.io.ByteArrayInputStream(body);
            return new jakarta.servlet.ServletInputStream() {
                public int read() { return in.read(); }
                public boolean isFinished() { return in.available() == 0; }
                public boolean isReady() { return true; }
                public void setReadListener(jakarta.servlet.ReadListener l) { throw new UnsupportedOperationException(); }
            };
        }
        @Override public java.io.BufferedReader getReader() { return new java.io.BufferedReader(new java.io.InputStreamReader(getInputStream(), StandardCharsets.UTF_8)); }
    }
}
