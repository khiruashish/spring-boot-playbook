package com.playbook.interview.p12;

import org.springframework.security.access.prepost.PostAuthorize;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;

import java.util.Map;

/** Problem 12: authorization rules on the service layer: roles, ownership checks, and filtering by result. */
@Service
public class DocumentService {

    public record Document(String id, String owner, String title) { }

    private final Map<String, Document> docs = Map.of(
            "d1", new Document("d1", "ana", "Ana's payslip"),
            "d2", new Document("d2", "bob", "Bob's payslip"));

    /** Ownership check AFTER loading: only the owner or an admin may see the document. */
    @PostAuthorize("returnObject.owner == authentication.name or hasRole('ADMIN')")
    public Document get(String id) {
        Document d = docs.get(id);
        if (d == null) throw new IllegalArgumentException("no document " + id);
        return d;
    }

    @PreAuthorize("hasRole('ADMIN')")
    public int purgeAll() { return docs.size(); }

    /** Check an argument BEFORE running: users may only list their own documents. */
    @PreAuthorize("#owner == authentication.name or hasRole('ADMIN')")
    public long countFor(String owner) { return docs.values().stream().filter(d -> d.owner().equals(owner)).count(); }
}
