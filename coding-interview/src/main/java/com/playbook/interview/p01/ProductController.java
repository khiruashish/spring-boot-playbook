package com.playbook.interview.p01;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

/** Problem 1: CRUD REST API with validation, correct status codes and a Location header. */
@RestController
@RequestMapping("/p01/products")
class ProductController {

    /** Request DTO: validated at the edge. Never bind requests straight onto entities. */
    record CreateProduct(
            @NotBlank @Size(max = 80) String name,
            @NotNull @Positive Long priceCents,
            @Pattern(regexp = "[A-Z]{3}-\\d{4}", message = "must look like ABC-1234") String sku) { }

    record Product(long id, String name, long priceCents, String sku) { }

    private final Map<Long, Product> store = new ConcurrentHashMap<>();
    private final AtomicLong ids = new AtomicLong();

    @PostMapping
    ResponseEntity<Product> create(@Valid @RequestBody CreateProduct req) {
        Product p = new Product(ids.incrementAndGet(), req.name(), req.priceCents(), req.sku());
        store.put(p.id(), p);
        var location = ServletUriComponentsBuilder.fromCurrentRequest().path("/{id}").buildAndExpand(p.id()).toUri();
        return ResponseEntity.created(location).body(p);                // 201 + Location
    }

    @GetMapping("/{id}")
    Product get(@PathVariable long id) {
        Product p = store.get(id);
        if (p == null) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "product " + id + " not found");
        return p;
    }

    @GetMapping
    List<Product> list() { return store.values().stream().sorted((a, b) -> Long.compare(a.id(), b.id())).toList(); }

    @PutMapping("/{id}")
    Product replace(@PathVariable long id, @Valid @RequestBody CreateProduct req) {
        if (!store.containsKey(id)) throw new ResponseStatusException(HttpStatus.NOT_FOUND, "product " + id + " not found");
        Product p = new Product(id, req.name(), req.priceCents(), req.sku());
        store.put(id, p);
        return p;
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    void delete(@PathVariable long id) { store.remove(id); }        // idempotent: deleting twice is still 204
}
