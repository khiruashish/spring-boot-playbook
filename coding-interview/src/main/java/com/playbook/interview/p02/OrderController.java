package com.playbook.interview.p02;

import org.springframework.web.bind.annotation.*;

import java.util.Map;

/** Problem 2: the controller only throws domain exceptions; ApiExceptionHandler turns them into RFC 9457 responses. */
@RestController
@RequestMapping("/p02/orders")
class OrderController {

    private final Map<String, String> orders = Map.of("A-1", "PLACED", "A-2", "SHIPPED");

    @GetMapping("/{id}")
    Map<String, String> get(@PathVariable String id) {
        String status = orders.get(id);
        if (status == null) throw new OrderNotFoundException(id);
        return Map.of("id", id, "status", status);
    }

    @PostMapping("/{id}/cancel")
    Map<String, String> cancel(@PathVariable String id) {
        String status = orders.get(id);
        if (status == null) throw new OrderNotFoundException(id);
        if (status.equals("SHIPPED")) throw new InvalidStateException(id, status, "cancel");
        return Map.of("id", id, "status", "CANCELLED");
    }

    @GetMapping("/boom")
    String boom() { throw new IllegalStateException("database password is hunter2"); }   // must NOT leak to clients
}
