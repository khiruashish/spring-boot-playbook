package com.playbook.interview.p06;

import com.playbook.interview.support.WebTestBase;
import org.junit.jupiter.api.Test;

import java.time.Duration;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class RateLimitInterceptorTest extends WebTestBase {

    @Test
    void fourthRequestInAMinute_gets429_withRetryAfter() throws Exception {
        for (int i = 0; i < 3; i++)
            mvc.perform(get("/p06/quote").header("X-Api-Key", "client-a")).andExpect(status().isOk())
               .andExpect(header().string("RateLimit-Remaining", String.valueOf(2 - i)));
        mvc.perform(get("/p06/quote").header("X-Api-Key", "client-a"))
           .andExpect(status().isTooManyRequests())
           .andExpect(header().string("Retry-After", "20"));
    }

    @Test
    void tokensRefillOverTime() throws Exception {
        for (int i = 0; i < 3; i++) mvc.perform(get("/p06/quote").header("X-Api-Key", "client-b")).andExpect(status().isOk());
        mvc.perform(get("/p06/quote").header("X-Api-Key", "client-b")).andExpect(status().isTooManyRequests());
        clock.advance(Duration.ofSeconds(20));                      // 3/min = one token every 20 s
        mvc.perform(get("/p06/quote").header("X-Api-Key", "client-b")).andExpect(status().isOk());
    }

    @Test
    void clientsAreLimitedIndependently() throws Exception {
        for (int i = 0; i < 3; i++) mvc.perform(get("/p06/quote").header("X-Api-Key", "client-c")).andExpect(status().isOk());
        mvc.perform(get("/p06/quote").header("X-Api-Key", "client-d")).andExpect(status().isOk());
    }

    @Test
    void otherEndpoints_areNotLimited() throws Exception {
        for (int i = 0; i < 10; i++) mvc.perform(get("/p02/orders/A-1").header("X-Api-Key", "client-e")).andExpect(status().isOk());
    }
}
