package com.playbook.interview.p08;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties("greeting")
public record GreetingProperties(String prefix, boolean enabled) {
    public GreetingProperties {
        if (prefix == null) prefix = "Hello";
    }
}
