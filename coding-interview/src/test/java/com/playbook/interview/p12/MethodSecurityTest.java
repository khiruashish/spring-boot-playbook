package com.playbook.interview.p12;

import com.playbook.interview.support.WebTestBase;
import org.junit.jupiter.api.Test;
import org.springframework.security.test.context.support.WithMockUser;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class MethodSecurityTest extends WebTestBase {

    @Test
    void anonymous_gets401_fromTheFilterChain() throws Exception {
        mvc.perform(get("/p12/documents/d1")).andExpect(status().isUnauthorized());
    }

    @Test
    @WithMockUser(username = "ana")
    void owner_canReadOwnDocument() throws Exception {
        mvc.perform(get("/p12/documents/d1")).andExpect(status().isOk()).andExpect(jsonPath("$.title").value("Ana's payslip"));
    }

    @Test
    @WithMockUser(username = "ana")
    void otherUser_gets403_fromPostAuthorize() throws Exception {
        mvc.perform(get("/p12/documents/d2")).andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "ana")
    void preAuthorize_checksTheArgument() throws Exception {
        mvc.perform(get("/p12/documents/count").param("owner", "ana")).andExpect(status().isOk());
        mvc.perform(get("/p12/documents/count").param("owner", "bob")).andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "root", roles = "ADMIN")
    void admin_canDoEverything() throws Exception {
        mvc.perform(get("/p12/documents/d2")).andExpect(status().isOk());
        mvc.perform(delete("/p12/documents")).andExpect(status().isOk()).andExpect(jsonPath("$.purged").value(2));
    }

    @Test
    @WithMockUser(username = "ana")
    void nonAdmin_cannotPurge() throws Exception {
        mvc.perform(delete("/p12/documents")).andExpect(status().isForbidden());
    }
}
