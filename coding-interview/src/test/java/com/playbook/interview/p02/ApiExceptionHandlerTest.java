package com.playbook.interview.p02;

import com.playbook.interview.support.WebTestBase;
import org.junit.jupiter.api.Test;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class ApiExceptionHandlerTest extends WebTestBase {

    @Test
    void domainNotFound_mapsTo404_withTypeTitleAndCustomProperty() throws Exception {
        mvc.perform(get("/p02/orders/X-9"))
           .andExpect(status().isNotFound())
           .andExpect(content().contentTypeCompatibleWith("application/problem+json"))
           .andExpect(jsonPath("$.type").value("https://errors.example.com/order-not-found"))
           .andExpect(jsonPath("$.title").value("Order not found"))
           .andExpect(jsonPath("$.orderId").value("X-9"))
           .andExpect(jsonPath("$.instance").value("/p02/orders/X-9"));
    }

    @Test
    void invalidStateTransition_mapsTo409() throws Exception {
        mvc.perform(post("/p02/orders/A-2/cancel"))
           .andExpect(status().isConflict())
           .andExpect(jsonPath("$.currentState").value("SHIPPED"));
    }

    @Test
    void unexpectedError_returns500_withoutLeakingTheMessage() throws Exception {
        mvc.perform(get("/p02/orders/boom"))
           .andExpect(status().isInternalServerError())
           .andExpect(jsonPath("$.detail", not(containsString("hunter2"))))
           .andExpect(jsonPath("$.errorId").isNotEmpty());
    }

    @Test
    void springsOwnErrors_useTheSameFormat_405() throws Exception {
        mvc.perform(delete("/p02/orders/A-1"))
           .andExpect(status().isMethodNotAllowed())
           .andExpect(content().contentTypeCompatibleWith("application/problem+json"));
    }
}
