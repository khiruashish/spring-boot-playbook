package com.playbook.interview.p02;

public class OrderNotFoundException extends RuntimeException {
    final String orderId;
    public OrderNotFoundException(String orderId) { super("order " + orderId + " not found"); this.orderId = orderId; }
}
