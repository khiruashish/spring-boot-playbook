package com.playbook.interview.p04;

import com.playbook.interview.support.WebTestBase;
import org.junit.jupiter.api.Test;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class PaginationTest extends WebTestBase {

    @Test
    void defaultPage_returnsFirst20_withMetadata() throws Exception {
        mvc.perform(get("/p04/customers"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.content", hasSize(20)))
           .andExpect(jsonPath("$.totalElements").value(53))
           .andExpect(jsonPath("$.totalPages").value(3))
           .andExpect(jsonPath("$.last").value(false));
    }

    @Test
    void lastPage_isPartial_andFlaggedLast() throws Exception {
        mvc.perform(get("/p04/customers").param("page", "2").param("size", "20"))
           .andExpect(jsonPath("$.content", hasSize(13)))
           .andExpect(jsonPath("$.last").value(true));
    }

    @Test
    void sortByNameDesc() throws Exception {
        mvc.perform(get("/p04/customers").param("size", "2").param("sort", "name,desc"))
           .andExpect(jsonPath("$.content[0].name").value("customer-53"))
           .andExpect(jsonPath("$.content[1].name").value("customer-52"));
    }

    @Test
    void sizeAbove100_isRejected() throws Exception {
        mvc.perform(get("/p04/customers").param("size", "5000")).andExpect(status().isBadRequest());
    }

    @Test
    void unknownSortField_isRejected_noInjection() throws Exception {
        mvc.perform(get("/p04/customers").param("sort", "name; DROP TABLE customer"))
           .andExpect(status().isBadRequest())
           .andExpect(jsonPath("$.detail", containsString("allowed: [city, id, name]")));
    }
}
