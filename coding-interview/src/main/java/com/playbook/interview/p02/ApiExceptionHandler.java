package com.playbook.interview.p02;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.http.ProblemDetail;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.servlet.mvc.method.annotation.ResponseEntityExceptionHandler;

import java.net.URI;
import java.util.UUID;

/**
 * Problem 2: one place maps exceptions to RFC 9457 ProblemDetail. Extending ResponseEntityExceptionHandler keeps
 * Spring's own handling (validation errors, 405, 415...) in the same format.
 */
@RestControllerAdvice
class ApiExceptionHandler extends ResponseEntityExceptionHandler {

    private static final Logger log = LoggerFactory.getLogger(ApiExceptionHandler.class);

    @ExceptionHandler(OrderNotFoundException.class)
    ProblemDetail notFound(OrderNotFoundException e) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, e.getMessage());
        pd.setType(URI.create("https://errors.example.com/order-not-found"));
        pd.setTitle("Order not found");
        pd.setProperty("orderId", e.orderId);
        return pd;
    }

    @ExceptionHandler(InvalidStateException.class)
    ProblemDetail conflict(InvalidStateException e) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.CONFLICT, e.getMessage());
        pd.setType(URI.create("https://errors.example.com/invalid-state"));
        pd.setTitle("Invalid order state");
        pd.setProperty("currentState", e.state);
        return pd;
    }

    /**
     * Method-security denials (problem 12) are thrown inside the controller call. Without this handler the catch-all
     * below would turn a 403 into a 500.
     */
    @ExceptionHandler(AccessDeniedException.class)
    ProblemDetail forbidden(AccessDeniedException e) {
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.FORBIDDEN, "You are not allowed to do this");
        pd.setTitle("Forbidden");
        return pd;
    }

    /** Catch-all: log the details with a correlation id, return a generic message. Never leak internals. */
    @ExceptionHandler(Exception.class)
    ProblemDetail unexpected(Exception e) {
        String errorId = UUID.randomUUID().toString();
        log.error("unhandled error {}", errorId, e);
        ProblemDetail pd = ProblemDetail.forStatusAndDetail(HttpStatus.INTERNAL_SERVER_ERROR, "Unexpected error. Reference: " + errorId);
        pd.setTitle("Internal error");
        pd.setProperty("errorId", errorId);
        return pd;
    }
}
