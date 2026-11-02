package com.playbook.interview.p06;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.web.servlet.HandlerInterceptor;

import java.time.Clock;
import java.util.concurrent.ConcurrentHashMap;

/** Problem 6: per-client token bucket in a HandlerInterceptor; 429 + Retry-After + RateLimit headers. */
@Component
class RateLimitInterceptor implements HandlerInterceptor {

    private static final class Bucket { double tokens; long lastRefillMillis; }

    private final ConcurrentHashMap<String, Bucket> buckets = new ConcurrentHashMap<>();
    private final int capacity;
    private final double refillPerMilli;
    private final Clock clock;

    RateLimitInterceptor(@Value("${interview.rate-limit.requests-per-minute}") int perMinute, Clock clock) {
        this.capacity = perMinute;
        this.refillPerMilli = perMinute / 60_000.0;
        this.clock = clock;
    }

    @Override
    public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object handler) throws Exception {
        String client = req.getHeader("X-Api-Key") != null ? req.getHeader("X-Api-Key") : req.getRemoteAddr();
        Bucket b = buckets.computeIfAbsent(client, c -> { Bucket nb = new Bucket(); nb.tokens = capacity; nb.lastRefillMillis = clock.millis(); return nb; });
        synchronized (b) {                                                   // per-client lock: clients don't contend
            long now = clock.millis();
            b.tokens = Math.min(capacity, b.tokens + (now - b.lastRefillMillis) * refillPerMilli);
            b.lastRefillMillis = now;
            res.setHeader("RateLimit-Limit", String.valueOf(capacity));
            if (b.tokens >= 1) {
                b.tokens -= 1;
                res.setHeader("RateLimit-Remaining", String.valueOf((int) b.tokens));
                return true;
            }
            long retryAfterSeconds = (long) Math.ceil((1 - b.tokens) / refillPerMilli / 1000);
            res.setHeader("RateLimit-Remaining", "0");
            res.setHeader("Retry-After", String.valueOf(retryAfterSeconds));
            res.sendError(429, "rate limit exceeded");
            return false;                                                    // stop: the controller is never called
        }
    }
}
