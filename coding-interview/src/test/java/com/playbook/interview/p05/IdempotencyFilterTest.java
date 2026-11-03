package com.playbook.interview.p05;

import com.playbook.interview.support.WebTestBase;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class IdempotencyFilterTest extends WebTestBase {

    @Autowired PaymentController payments;

    private static final String BODY = """
            {"orderId":"A-1","amountCents":500}""";

    @Test
    void retryWithSameKey_replaysResponse_andChargesOnce() throws Exception {
        int before = payments.charges.get();
        String first = mvc.perform(post("/p05/payments").header("Idempotency-Key", "k-1").contentType("application/json").content(BODY))
                .andExpect(status().isCreated()).andReturn().getResponse().getContentAsString();
        mvc.perform(post("/p05/payments").header("Idempotency-Key", "k-1").contentType("application/json").content(BODY))
           .andExpect(status().isCreated())
           .andExpect(header().string("Idempotent-Replayed", "true"))
           .andExpect(content().string(first));
        assertThat(payments.charges.get() - before).isEqualTo(1);
    }

    @Test
    void sameKeyDifferentBody_returns422() throws Exception {
        mvc.perform(post("/p05/payments").header("Idempotency-Key", "k-2").contentType("application/json").content(BODY))
           .andExpect(status().isCreated());
        mvc.perform(post("/p05/payments").header("Idempotency-Key", "k-2").contentType("application/json").content("""
                {"orderId":"A-1","amountCents":999}"""))
           .andExpect(status().isUnprocessableContent());
    }

    @Test
    void missingKey_returns400() throws Exception {
        mvc.perform(post("/p05/payments").contentType("application/json").content(BODY)).andExpect(status().isBadRequest());
    }

    @Test
    void differentKeys_areIndependentPayments() throws Exception {
        int before = payments.charges.get();
        for (String k : new String[]{"k-3", "k-4"})
            mvc.perform(post("/p05/payments").header("Idempotency-Key", k).contentType("application/json").content(BODY)).andExpect(status().isCreated());
        assertThat(payments.charges.get() - before).isEqualTo(2);
    }
}
