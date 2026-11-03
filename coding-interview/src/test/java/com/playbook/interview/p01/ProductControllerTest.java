package com.playbook.interview.p01;

import com.playbook.interview.support.WebTestBase;
import org.junit.jupiter.api.Test;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class ProductControllerTest extends WebTestBase {

    private static final String VALID = """
            {"name":"Keyboard","priceCents":4500,"sku":"KBD-0001"}""";

    @Test
    void create_returns201_withLocationHeader() throws Exception {
        mvc.perform(post("/p01/products").contentType("application/json").content(VALID))
           .andExpect(status().isCreated())
           .andExpect(header().string("Location", matchesPattern("http://localhost/p01/products/\\d+")))
           .andExpect(jsonPath("$.name").value("Keyboard"));
    }

    @Test
    void create_invalidBody_returns400_problemDetail_listingEveryField() throws Exception {
        mvc.perform(post("/p01/products").contentType("application/json").content("""
                {"name":"","priceCents":-5,"sku":"bad"}"""))
           .andExpect(status().isBadRequest())
           .andExpect(content().contentTypeCompatibleWith("application/problem+json"))
           .andExpect(jsonPath("$.status").value(400));
    }

    @Test
    void get_unknownId_returns404() throws Exception {
        mvc.perform(get("/p01/products/999999")).andExpect(status().isNotFound())
           .andExpect(jsonPath("$.detail").value("product 999999 not found"));
    }

    @Test
    void put_replaces_and_delete_isIdempotent() throws Exception {
        String location = mvc.perform(post("/p01/products").contentType("application/json").content(VALID))
                .andReturn().getResponse().getHeader("Location");
        mvc.perform(put(location).contentType("application/json").content("""
                {"name":"Keyboard v2","priceCents":4900,"sku":"KBD-0002"}"""))
           .andExpect(status().isOk()).andExpect(jsonPath("$.priceCents").value(4900));
        mvc.perform(delete(location)).andExpect(status().isNoContent());
        mvc.perform(delete(location)).andExpect(status().isNoContent());
        mvc.perform(get(location)).andExpect(status().isNotFound());
    }

    @Test
    void malformedJson_returns400_notA500() throws Exception {
        mvc.perform(post("/p01/products").contentType("application/json").content("{not json"))
           .andExpect(status().isBadRequest());
    }
}
