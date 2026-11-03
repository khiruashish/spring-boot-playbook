package com.playbook.interview.p10;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest
class PriceServiceCachingTest {

    @Autowired PriceService prices;

    @BeforeEach
    void reset() { prices.clearAll(); prices.resetCounter(); }

    @Test
    void secondCall_isServedFromCache() {
        prices.price("apple"); prices.price("apple"); prices.price("apple");
        assertThat(prices.slowLookups()).isEqualTo(1);
    }

    @Test
    void cachePut_updatesWithoutAnotherLookup() {
        prices.price("pear");
        prices.updatePrice("pear", 95);
        assertThat(prices.price("pear")).isEqualTo(95L);
        assertThat(prices.slowLookups()).isEqualTo(1);
    }

    @Test
    void evict_forcesFreshLookup() {
        prices.price("apple");
        prices.delete("apple");
        assertThat(prices.price("apple")).isNull();
        assertThat(prices.slowLookups()).isEqualTo(2);
    }

    @Test
    void nullResults_areNotCached_becauseOfUnless() {
        prices.price("kiwi"); prices.price("kiwi");
        assertThat(prices.slowLookups()).isEqualTo(2);
    }
}
