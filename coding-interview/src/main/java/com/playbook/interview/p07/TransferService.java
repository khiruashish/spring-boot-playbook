package com.playbook.interview.p07;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.transaction.support.TransactionSynchronizationManager;

/** Problem 7: the three @Transactional traps: checked exceptions, self-invocation, and REQUIRES_NEW for audit logs. */
@Service
public class TransferService {

    public static class InsufficientFundsException extends Exception {          // CHECKED on purpose
        public InsufficientFundsException(String m) { super(m); }
    }

    private final JdbcTemplate jdbc;
    private final AuditService audit;

    TransferService(JdbcTemplate jdbc, AuditService audit) { this.jdbc = jdbc; this.audit = audit; }

    /** TRAP 1: by default only RuntimeException/Error roll back. A checked exception COMMITS the debit. */
    @Transactional
    public void transferDefaultRollback(String from, String to, long cents) throws InsufficientFundsException {
        debitThenCredit(from, to, cents);
    }

    /** FIX 1: declare rollbackFor (or throw unchecked domain exceptions). */
    @Transactional(rollbackFor = InsufficientFundsException.class)
    public void transferWithRollbackFor(String from, String to, long cents) throws InsufficientFundsException {
        debitThenCredit(from, to, cents);
    }

    /** TRAP 2: calling an annotated method on `this` bypasses the proxy, so NO transaction starts. */
    public boolean selfInvocationHasTransaction() { return this.insideTransactional(); }

    @Transactional
    public boolean insideTransactional() { return TransactionSynchronizationManager.isActualTransactionActive(); }

    /** FIX 3 / REQUIRES_NEW: the audit row survives even though the outer transfer rolls back. */
    @Transactional
    public void transferWithAudit(String from, String to, long cents) {
        audit.record("attempt " + from + "->" + to + " " + cents);           // another bean -> goes through its proxy
        jdbc.update("UPDATE account SET balance = balance - ? WHERE id = ?", cents, from);
        throw new IllegalStateException("fraud check failed");               // rolls back the debit, not the audit
    }

    private void debitThenCredit(String from, String to, long cents) throws InsufficientFundsException {
        jdbc.update("UPDATE account SET balance = balance - ? WHERE id = ?", cents, from);
        Long balance = jdbc.queryForObject("SELECT balance FROM account WHERE id = ?", Long.class, from);
        if (balance < 0) throw new InsufficientFundsException(from + " would go to " + balance);
        jdbc.update("UPDATE account SET balance = balance + ? WHERE id = ?", cents, to);
    }

    @Service
    public static class AuditService {
        private final JdbcTemplate jdbc;
        AuditService(JdbcTemplate jdbc) { this.jdbc = jdbc; }

        @Transactional(propagation = Propagation.REQUIRES_NEW)               // suspends the caller's tx, commits on its own
        public void record(String message) { jdbc.update("INSERT INTO audit_log(message) VALUES (?)", message); }
    }
}
