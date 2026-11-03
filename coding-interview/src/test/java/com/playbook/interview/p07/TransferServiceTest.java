package com.playbook.interview.p07;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;

import static org.assertj.core.api.Assertions.*;

@SpringBootTest
class TransferServiceTest {

    @Autowired TransferService service;
    @Autowired JdbcTemplate jdbc;

    @BeforeEach
    void reset() {
        jdbc.update("DELETE FROM account");
        jdbc.update("DELETE FROM audit_log");
        jdbc.update("INSERT INTO account VALUES ('ana', 1000), ('bob', 0)");
    }

    long balance(String id) { return jdbc.queryForObject("SELECT balance FROM account WHERE id = ?", Long.class, id); }

    @Test
    void trap1_checkedException_commitsTheDebit_byDefault() {
        assertThatThrownBy(() -> service.transferDefaultRollback("ana", "bob", 5_000)).isInstanceOf(TransferService.InsufficientFundsException.class);
        assertThat(balance("ana")).isEqualTo(-4_000);           // money destroyed: the debit was COMMITTED
    }

    @Test
    void fix1_rollbackFor_rollsBackOnCheckedException() {
        assertThatThrownBy(() -> service.transferWithRollbackFor("ana", "bob", 5_000)).isInstanceOf(TransferService.InsufficientFundsException.class);
        assertThat(balance("ana")).isEqualTo(1_000);
    }

    @Test
    void trap2_selfInvocation_bypassesTheProxy() {
        assertThat(service.insideTransactional()).isTrue();      // called through the proxy
        assertThat(service.selfInvocationHasTransaction()).isFalse();  // called via `this`: no transaction
    }

    @Test
    void requiresNew_auditSurvivesOuterRollback() {
        assertThatThrownBy(() -> service.transferWithAudit("ana", "bob", 300)).isInstanceOf(IllegalStateException.class);
        assertThat(balance("ana")).isEqualTo(1_000);             // outer tx rolled back
        assertThat(jdbc.queryForObject("SELECT COUNT(*) FROM audit_log", Integer.class)).isEqualTo(1);   // inner tx committed
    }

    @Test
    void happyPath_movesMoney() throws Exception {
        service.transferWithRollbackFor("ana", "bob", 400);
        assertThat(balance("ana")).isEqualTo(600);
        assertThat(balance("bob")).isEqualTo(400);
    }
}
