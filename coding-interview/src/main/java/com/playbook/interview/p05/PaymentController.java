package com.playbook.interview.p05;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.concurrent.atomic.AtomicInteger;

@RestController
@RequestMapping("/p05/payments")
class PaymentController {
    final AtomicInteger charges = new AtomicInteger();

    record ChargeRequest(String orderId, long amountCents) { }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    Map<String, Object> charge(@RequestBody ChargeRequest req) {
        int n = charges.incrementAndGet();                                     // the side effect we must not repeat
        return Map.of("paymentId", "pay_" + n, "orderId", req.orderId(), "amountCents", req.amountCents());
    }
}
