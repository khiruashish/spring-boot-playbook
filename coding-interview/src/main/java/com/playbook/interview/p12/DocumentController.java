package com.playbook.interview.p12;

import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/p12/documents")
class DocumentController {
    private final DocumentService service;
    DocumentController(DocumentService service) { this.service = service; }

    @GetMapping("/{id}") DocumentService.Document get(@PathVariable String id) { return service.get(id); }
    @GetMapping("/count") Map<String, Long> count(@RequestParam String owner) { return Map.of(owner, service.countFor(owner)); }
    @DeleteMapping Map<String, Integer> purge() { return Map.of("purged", service.purgeAll()); }
}
