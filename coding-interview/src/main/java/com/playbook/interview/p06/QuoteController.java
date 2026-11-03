package com.playbook.interview.p06;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
class QuoteController {
    @GetMapping("/p06/quote")
    Map<String, String> quote() { return Map.of("symbol", "ACME", "price", "101.25"); }
}
