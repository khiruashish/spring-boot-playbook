package com.playbook.interview.p04;

import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

import java.util.*;
import java.util.stream.IntStream;

/**
 * Problem 4: page + sort with a capped page size and a sort-field whitelist (never pass user input into ORDER BY).
 * @Min/@Max on parameters use Spring MVC's built-in method validation (6.1+): no class-level @Validated needed, and
 * violations become a 400 ProblemDetail (HandlerMethodValidationException).
 */
@RestController
@RequestMapping("/p04/customers")
class CustomerController {

    record Customer(int id, String name, String city) { }
    record Page<T>(List<T> content, int page, int size, long totalElements, int totalPages, boolean last) { }

    private static final Map<String, Comparator<Customer>> SORTABLE = Map.of(
            "id", Comparator.comparingInt(Customer::id),
            "name", Comparator.comparing(Customer::name),
            "city", Comparator.comparing(Customer::city).thenComparing(Customer::name));

    private final List<Customer> all = IntStream.rangeClosed(1, 53)
            .mapToObj(i -> new Customer(i, "customer-" + String.format("%02d", 54 - i), i % 2 == 0 ? "Pune" : "Delhi"))
            .toList();

    @GetMapping
    Page<Customer> list(@RequestParam(defaultValue = "0") @Min(0) int page,
                        @RequestParam(defaultValue = "20") @Min(1) @Max(100) int size,
                        @RequestParam(defaultValue = "id,asc") String sort) {
        String[] parts = sort.split(",");
        Comparator<Customer> cmp = SORTABLE.get(parts[0]);
        if (cmp == null) throw new ResponseStatusException(HttpStatus.BAD_REQUEST, "cannot sort by '" + parts[0] + "'; allowed: " + new TreeSet<>(SORTABLE.keySet()));
        if (parts.length > 1 && parts[1].equalsIgnoreCase("desc")) cmp = cmp.reversed();

        List<Customer> sorted = all.stream().sorted(cmp).toList();
        int from = Math.min(page * size, sorted.size()), to = Math.min(from + size, sorted.size());
        int totalPages = (int) Math.ceil((double) sorted.size() / size);
        return new Page<>(sorted.subList(from, to), page, size, sorted.size(), totalPages, page >= totalPages - 1);
    }
}
