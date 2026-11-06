import sys
from animlib import Anim

a = Anim("pb-mvc", "One request through Spring MVC — filters, <code>DispatcherServlet</code>, and where errors go",
         "Spring MVC request flow",
         "A request passes servlet filters, then DispatcherServlet: HandlerMapping picks the controller method, "
         "interceptors run preHandle, the HandlerAdapter resolves and validates arguments, invokes the controller and "
         "writes the return value as JSON. A validation failure goes to the exception resolvers and @ControllerAdvice. "
         "A filter can reject a request before Spring MVC runs.", 800, 404)

a.box("client", 16, 146, 96, 72, "Client", ["POST", "/api/orders"], sub_mono=True)
a.box("filters", 128, 56, 96, 262, "Filters", ["Security", "correlation id", "logging"], kind="band")
a.box("ds", 240, 22, 544, 304, "DispatcherServlet", kind="shell")
a.box("hm", 256, 50, 150, 58, "HandlerMapping", ["picks the method"])
a.box("ic", 256, 128, 150, 96, "Interceptors", ["preHandle", "postHandle", "afterCompletion"], kind="band", sub_mono=True)
a.box("er", 256, 246, 150, 62, "Exception", ["resolvers →", "@ControllerAdvice"], extra=None)
a.box("ha", 424, 50, 344, 258, kind="target")
a.text(440, 72, "HandlerAdapter", "t-b")
a.box("ar", 440, 88, 150, 64, "Arguments", ["@RequestBody → JSON", "@Valid"], sub_mono=True)
a.box("ctl", 604, 88, 150, 64, "OrderController", ["create(request)"], sub_mono=True)
a.box("rv", 604, 176, 150, 64, "Return value", ["@ResponseBody", "→ JSON write"], sub_mono=True)

a.route("c2f", [(112, 176), (128, 176)])
a.route("f2ds", [(224, 79), (256, 79)])
a.route("hm2ic", [(331, 108), (331, 128)])
a.route("ic2ar", d="M406 150 C 426 150 420 120 440 120")
a.route("ar2ctl", [(590, 120), (604, 120)])
a.route("ctl2rv", [(679, 152), (679, 176)])
a.route("rv2ic", [(604, 208), (406, 208)])
a.open("invalid")
a.route("err", [(515, 152), (515, 277), (406, 277)])
a.route("er2ic", [(331, 246), (331, 224)])
a.close()
a.route("out1", [(256, 200), (224, 200)])
a.route("out2", [(128, 196), (112, 196)])

a.panel(16, 338, 768, 56)
a.text(32, 371, "Response", "t-b")
a.chip("handler", 140, 350, 200, "Handler", {"create": ("create()", "committed")})
a.chip("status", 356, 350, 206, "Status", {"c201": ("201 CREATED", "committed"), "c400": ("400 BAD REQUEST", "rolledback"),
                                           "c401": ("401 UNAUTHORIZED", "rolledback")})
a.chip("body", 578, 350, 196, "Body", {"json": ("OrderResponse", "committed"), "problem": ("problem+json", "rolledback"),
                                       "empty": ("no body", "suspended")})

a.scene("ok", "1 · Happy path", [
    {"path": "c2f", "hl": "client filters", "text": "<code>POST /api/orders</code> arrives. <strong>Servlet filters</strong> run first, outside Spring MVC: Spring Security, correlation id / MDC, request logging. Any of them can end the request here."},
    {"path": "f2ds", "hl": "hm", "tx": {"handler": "create"}, "text": "<code>DispatcherServlet</code> asks <code>RequestMappingHandlerMapping</code> for a handler. It matches path, method, <code>consumes</code> and <code>produces</code> and returns the controller method plus its interceptors."},
    {"path": "hm2ic", "hl": "ic", "text": "Each <code>HandlerInterceptor</code>'s <code>preHandle()</code> runs. Unlike a filter it already knows the chosen handler method, and returning <code>false</code> stops the request (Interview Problem 6's rate limiter works this way)."},
    {"path": "ic2ar", "hl": "ar", "text": "The <code>HandlerAdapter</code> resolves each parameter. <code>@RequestBody</code> reads the JSON with an <code>HttpMessageConverter</code> (Jackson), then <code>@Valid</code> runs Bean Validation."},
    {"path": "ar2ctl", "hl": "ctl", "text": "Your controller method runs with fully built, validated arguments. There's no HTTP parsing in your code."},
    {"path": "ctl2rv", "hl": "rv", "tx": {"status": "c201", "body": "json"}, "text": "The returned <code>ResponseEntity&lt;OrderResponse&gt;</code> is written as JSON by a message converter, chosen by content negotiation against <code>Accept</code>. <code>ResponseBodyAdvice</code> can adjust the body here."},
    {"path": "rv2ic", "hl": "ic", "text": "<code>postHandle()</code> then <code>afterCompletion()</code> run on the way out. With <code>@ResponseBody</code> the body is already written, so <code>postHandle()</code> can't change it; use <code>afterCompletion()</code> for timing and cleanup."},
    {"path": "out1,out2", "hl": "filters client", "text": "The response passes back out through the filters, in reverse order, to the client: <strong>201 Created</strong>."},
])

a.scene("invalid", "2 · Validation fails", [
    {"path": "c2f,f2ds,hm2ic", "hl": "ic", "tx": {"handler": "create"}, "text": "Same request, but the body has <code>\"quantity\": 0</code>. Filters, handler mapping and <code>preHandle()</code> run exactly as before."},
    {"path": "ic2ar", "hl": "ar", "warn": "ar", "text": "<code>@Valid</code> fails while the argument is being resolved, so Spring throws <code>MethodArgumentNotValidException</code>. Your controller method <strong>never runs</strong>."},
    {"path": "err", "token": "error", "hl": "er", "dim": "ctl rv", "text": "The exception goes to the <code>HandlerExceptionResolver</code>s. <code>ExceptionHandlerExceptionResolver</code> finds the matching <code>@ExceptionHandler</code> in your <code>@ControllerAdvice</code> (Chapter 10)."},
    {"hl": "er", "dim": "ctl rv", "tx": {"status": "c400", "body": "problem"}, "text": "The handler returns a <code>ProblemDetail</code>, written as <code>application/problem+json</code> with status 400 and the field errors."},
    {"path": "er2ic,out1,out2", "hl": "ic filters client", "dim": "ctl rv", "text": "<code>postHandle()</code> is skipped, but <code>afterCompletion()</code> still runs. The 400 travels back out through the filters."},
])

a.scene("filter", "3 · Rejected by a filter", [
    {"path": "c2f", "hl": "filters", "warn": "filters", "tx": {"status": "c401", "body": "empty"}, "text": "No valid token. Spring Security's filter answers <strong>401</strong> on its own; <code>DispatcherServlet</code> is never called."},
    {"path": "out2", "hl": "client", "warn": "filters", "dim": "ds hm ic er ha ar ctl rv", "tx": {"status": "c401", "body": "empty"}, "text": "So no interceptor, <code>@ControllerAdvice</code> or controller code runs, and your <code>ProblemDetail</code> handler can't shape this error. Filter-level errors need their own handling (Chapter 17's <code>AuthenticationEntryPoint</code>)."},
])

a.write(sys.argv[1])
