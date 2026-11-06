import sys
from animlib import Anim

a = Anim("pb-sec", "Through the security filter chain — 200, 401 and 403",
         "Spring Security filter chain",
         "A request enters DelegatingFilterProxy and FilterChainProxy, which picks the stateless /api/** chain. "
         "BearerTokenAuthenticationFilter validates a JWT with JwtDecoder and stores the authentication in the "
         "SecurityContext. AnonymousAuthenticationFilter covers missing tokens. AuthorizationFilter applies the rules; "
         "ExceptionTranslationFilter turns denials into a 401 from the AuthenticationEntryPoint or a 403 from the "
         "AccessDeniedHandler, before DispatcherServlet runs.", 800, 416, top=46)

B = dict(sub_cls="t-sub")
a.box("client", 16, 60, 90, 60, "Client")
a.box("dfp", 118, 60, 132, 60, "DelegatingFilter", extra=[("Proxy", "t-b")], kind="band")
a.box("fcp", 260, 60, 132, 60, "FilterChainProxy", ["picks the /api/** chain"])
a.box("sch", 402, 60, 132, 60, "SecurityContext", extra=[("HolderFilter", "t-b")])
a.box("hdr", 544, 60, 132, 60, "Headers · CORS", ["CSRF"])
a.box("bearer", 118, 170, 132, 60, "BearerToken", extra=[("AuthenticationFilter", "t-b t-10")])
a.box("anon", 260, 170, 132, 60, "Anonymous", extra=[("AuthenticationFilter", "t-b t-10")])
a.box("etf", 402, 170, 132, 60, "ExceptionTranslation", extra=[("Filter", "t-b")], title_cls="t-11")
a.box("az", 544, 170, 132, 60, "AuthorizationFilter", ["URL rules"], title_cls="t-11")
a.box("ds", 688, 170, 96, 60, "Dispatcher", extra=[("Servlet", "t-b")], kind="band")
a.box("jwt", 118, 286, 132, 56, "JwtDecoder", ["JWK · exp · iss · aud"])
a.box("ctx", 260, 286, 132, 56, "SecurityContext", ["who is calling"])
a.box("entry", 402, 286, 132, 56, "EntryPoint", ["401 Unauthorized"], title_cls="t-mono")
a.box("denied", 544, 286, 132, 56, "AccessDenied", extra=[("Handler · 403", "t-xs t-sub")], title_cls="t-mono")

a.route("c2dfp", [(106, 90), (118, 90)])
a.route("dfp2fcp", [(250, 90), (260, 90)])
a.route("fcp2sch", [(392, 90), (402, 90)])
a.route("sch2hdr", [(534, 90), (544, 90)])
a.route("wrap", [(660, 120), (660, 146), (184, 146), (184, 170)])
a.route("b2anon", [(250, 200), (260, 200)])
a.route("anon2etf", [(392, 200), (402, 200)])
a.route("etf2az", [(534, 200), (544, 200)])
a.route("az2ds", [(676, 200), (688, 200)])
a.route("b2jwt", [(160, 230), (160, 286)])
a.route("b2ctx", [(230, 230), (230, 258), (326, 258), (326, 286)])
a.route("etf2entry", [(440, 230), (440, 286)])
a.route("etf2denied", [(520, 230), (520, 258), (610, 258), (610, 286)])
a.route("out401", [(468, 342), (468, 352), (60, 352), (60, 120)])
a.route("out403", [(610, 342), (610, 352), (60, 352), (60, 120)])

a.panel(16, 360, 768, 48)
a.chip("req", 28, 368, 250, "Request", {"orders": ("GET /api/orders", "none"), "admin": ("GET /api/admin/reports", "none")})
a.chip("auth", 290, 368, 250, "Auth", {"anon": ("ANONYMOUS", "suspended"), "jwt": ("JWT · ROLE_CUSTOMER", "committed")})
a.chip("status", 552, 368, 220, "Status", {"ok": ("200 → CONTROLLER", "committed"), "c401": ("401", "rolledback"),
                                           "c403": ("403", "rolledback")})

FRONT = "c2dfp,dfp2fcp,fcp2sch,sch2hdr,wrap"

a.scene("ok", "1 · Valid JWT", [
    {"path": "c2dfp", "hl": "client dfp", "tx": {"req": "orders"}, "text": "Spring Security is a single servlet filter, <code>DelegatingFilterProxy</code>, which hands the request to <code>FilterChainProxy</code>."},
    {"path": "dfp2fcp", "hl": "fcp", "text": "<code>FilterChainProxy</code> picks the <strong>first</strong> <code>SecurityFilterChain</code> whose matcher fits. <code>/api/orders</code> matches the stateless <code>/api/**</code> chain, and only that chain's filters run."},
    {"path": "fcp2sch,sch2hdr", "hl": "sch hdr", "text": "<code>SecurityContextHolderFilter</code> sets up an empty <code>SecurityContext</code> for this thread. Header, CORS and CSRF filters follow; a stateless token API usually disables CSRF."},
    {"path": "wrap", "hl": "bearer", "text": "<code>BearerTokenAuthenticationFilter</code> finds <code>Authorization: Bearer …</code>. (An invalid or expired token fails right here, with a 401.)"},
    {"path": "b2jwt", "hl": "jwt", "tx": {"auth": "jwt"}, "text": "<code>JwtDecoder</code> checks the signature against the cached JWK set, then <code>exp</code>, issuer and audience. <code>JwtAuthenticationConverter</code> maps claims to authorities such as <code>ROLE_CUSTOMER</code>."},
    {"path": "b2jwt:rev,b2ctx", "hl": "ctx", "text": "The authenticated token is stored in the <strong><code>SecurityContext</code></strong>, so later filters and your code (<code>@AuthenticationPrincipal</code>, <code>@PreAuthorize</code>) can see who is calling."},
    {"path": "b2anon", "hl": "anon", "text": "<code>AnonymousAuthenticationFilter</code> has nothing to do, because a user is already authenticated."},
    {"path": "anon2etf,etf2az", "hl": "etf az", "text": "<code>ExceptionTranslationFilter</code> wraps the rest of the chain to catch security exceptions. <code>AuthorizationFilter</code> checks the rule for <code>/api/orders</code> (<code>authenticated()</code>): <strong>granted</strong>."},
    {"path": "az2ds", "hl": "ds", "tx": {"status": "ok"}, "text": "The request reaches <code>DispatcherServlet</code> and your controller, which is the Spring MVC flow from Chapter 8."},
])

a.scene("none", "2 · No token → 401", [
    {"path": FRONT, "hl": "bearer", "tx": {"req": "orders"}, "text": "<code>GET /api/orders</code> again, but with no <code>Authorization</code> header. <code>BearerTokenAuthenticationFilter</code> finds no token and passes the request on. A missing token isn't an error <em>yet</em>."},
    {"path": "b2anon", "hl": "anon", "tx": {"auth": "anon"}, "text": "<code>AnonymousAuthenticationFilter</code> fills the empty context with an <code>AnonymousAuthenticationToken</code>."},
    {"path": "anon2etf,etf2az", "hl": "az", "warn": "az", "text": "<code>AuthorizationFilter</code>: <code>/api/orders</code> needs an authenticated user, so it throws <code>AccessDeniedException</code>."},
    {"path": "etf2az:rev", "token": "error", "hl": "etf", "text": "<code>ExceptionTranslationFilter</code> catches it. The caller is anonymous, so this is really an <em>authentication</em> problem…"},
    {"path": "etf2entry", "token": "error", "hl": "entry", "tx": {"status": "c401"}, "text": "…so it starts authentication through the <code>AuthenticationEntryPoint</code>: <strong>401</strong> with <code>WWW-Authenticate: Bearer</code>."},
    {"path": "out401", "token": "error", "hl": "client", "dim": "ds", "text": "The 401 goes straight back. <code>DispatcherServlet</code> and <code>@ControllerAdvice</code> never ran, which is why §3.3 configures the entry point to write a <code>ProblemDetail</code>."},
])

a.scene("role", "3 · Wrong role → 403", [
    {"path": FRONT + ",b2jwt", "hl": "jwt", "tx": {"req": "admin", "auth": "jwt"}, "text": "A customer with a valid token calls <code>GET /api/admin/reports</code>. Authentication succeeds exactly as in scene 1: <code>ROLE_CUSTOMER</code>."},
    {"path": "b2jwt:rev,b2anon,anon2etf,etf2az", "hl": "az", "warn": "az", "text": "<code>AuthorizationFilter</code>: <code>/api/admin/**</code> requires <code>hasRole(\"OPS\")</code>, meaning the authority <code>ROLE_OPS</code>. Denied, with <code>AccessDeniedException</code>."},
    {"path": "etf2az:rev", "token": "error", "hl": "etf", "text": "<code>ExceptionTranslationFilter</code> catches it. This time the caller <em>is</em> authenticated, so it's a genuine authorization failure…"},
    {"path": "etf2denied", "token": "error", "hl": "denied", "tx": {"status": "c403"}, "text": "…handled by the <code>AccessDeniedHandler</code>: <strong>403 Forbidden</strong>."},
    {"path": "out403", "token": "error", "hl": "client", "dim": "ds", "text": "Again, nothing in Spring MVC ran. Method-level <code>@PreAuthorize</code> denials are different: they happen inside the controller call, so <code>@ControllerAdvice</code> can handle them."},
])

a.write(sys.argv[1])
