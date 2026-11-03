package com.playbook.interview.p10;

import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.CachePut;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/** Problem 10: read-through caching with @Cacheable, updates with @CachePut, invalidation with @CacheEvict. */
@Service
public class PriceService {

    private final AtomicInteger slowLookups = new AtomicInteger();

    /** Expose state through METHODS: callers hold a CGLIB proxy, and a field read on the proxy sees its own null field. */
    public int slowLookups() { return slowLookups.get(); }
    public void resetCounter() { slowLookups.set(0); }
    private final Map<String, Long> database = new ConcurrentHashMap<>(Map.of("apple", 120L, "pear", 90L));

    @Cacheable(cacheNames = "prices", key = "#sku", unless = "#result == null")   // don't cache misses (or do, deliberately)
    public Long price(String sku) {
        slowLookups.incrementAndGet();                                         // pretend this is a slow DB/HTTP call
        return database.get(sku);
    }

    @CachePut(cacheNames = "prices", key = "#sku")                             // write-through: cache holds the new value
    public Long updatePrice(String sku, long cents) { database.put(sku, cents); return cents; }

    @CacheEvict(cacheNames = "prices", key = "#sku")
    public void delete(String sku) { database.remove(sku); }

    @CacheEvict(cacheNames = "prices", allEntries = true)
    public void clearAll() { }
}
