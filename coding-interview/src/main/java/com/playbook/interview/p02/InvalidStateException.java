package com.playbook.interview.p02;

public class InvalidStateException extends RuntimeException {
    final String orderId, state, action;
    public InvalidStateException(String orderId, String state, String action) {
        super("cannot " + action + " order " + orderId + " in state " + state);
        this.orderId = orderId; this.state = state; this.action = action;
    }
}
