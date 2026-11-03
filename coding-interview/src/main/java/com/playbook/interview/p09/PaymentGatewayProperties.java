package com.playbook.interview.p09;

import jakarta.validation.constraints.*;
import org.hibernate.validator.constraints.URL;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.boot.context.properties.bind.DefaultValue;
import org.springframework.validation.annotation.Validated;

import java.time.Duration;
import java.util.List;

/** Problem 9: type-safe, immutable, VALIDATED configuration. A bad value fails startup, not the first payment at 3 a.m. */
@Validated
@ConfigurationProperties("payments.gateway")
public record PaymentGatewayProperties(
        @NotNull @URL String baseUrl,
        @NotBlank String apiKey,
        @DefaultValue("2s") Duration connectTimeout,
        @DefaultValue("5s") Duration readTimeout,
        @Min(0) @Max(5) @DefaultValue("2") int maxRetries,
        @DefaultValue("INR") List<@Pattern(regexp = "[A-Z]{3}") String> currencies) {

    @AssertTrue(message = "readTimeout must be >= connectTimeout")
    public boolean isTimeoutsConsistent() { return readTimeout == null || connectTimeout == null || readTimeout.compareTo(connectTimeout) >= 0; }
}
