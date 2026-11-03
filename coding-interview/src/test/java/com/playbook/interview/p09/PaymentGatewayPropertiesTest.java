package com.playbook.interview.p09;

import org.junit.jupiter.api.Test;
import org.springframework.boot.autoconfigure.AutoConfigurations;
import org.springframework.boot.autoconfigure.context.ConfigurationPropertiesAutoConfiguration;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.validation.autoconfigure.ValidationAutoConfiguration;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;
import org.springframework.context.annotation.Configuration;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;

class PaymentGatewayPropertiesTest {

    @Configuration
    @EnableConfigurationProperties(PaymentGatewayProperties.class)
    static class Config { }

    private final ApplicationContextRunner runner = new ApplicationContextRunner()
            .withConfiguration(AutoConfigurations.of(ConfigurationPropertiesAutoConfiguration.class, ValidationAutoConfiguration.class))
            .withUserConfiguration(Config.class);

    @Test
    void validConfig_bindsWithDefaults() {
        runner.withPropertyValues("payments.gateway.base-url=https://pay.example.com", "payments.gateway.api-key=sk_test")
              .run(ctx -> {
                  var p = ctx.getBean(PaymentGatewayProperties.class);
                  assertThat(p.readTimeout()).isEqualTo(Duration.ofSeconds(5));       // @DefaultValue
                  assertThat(p.maxRetries()).isEqualTo(2);
                  assertThat(p.currencies()).containsExactly("INR");
              });
    }

    @Test
    void relaxedBinding_andDurationParsing() {
        runner.withPropertyValues("payments.gateway.base-url=https://pay.example.com", "payments.gateway.api-key=k",
                        "payments.gateway.connectTimeout=750ms", "payments.gateway.currencies=INR,USD")
              .run(ctx -> {
                  var p = ctx.getBean(PaymentGatewayProperties.class);
                  assertThat(p.connectTimeout()).isEqualTo(Duration.ofMillis(750));
                  assertThat(p.currencies()).containsExactly("INR", "USD");
              });
    }

    @Test
    void missingApiKey_failsStartup() {
        runner.withPropertyValues("payments.gateway.base-url=https://pay.example.com")
              .run(ctx -> assertThat(ctx).hasFailed().getFailure().rootCause().hasMessageContaining("apiKey"));
    }

    @Test
    void crossFieldRule_failsStartup() {
        runner.withPropertyValues("payments.gateway.base-url=https://pay.example.com", "payments.gateway.api-key=k",
                        "payments.gateway.connect-timeout=10s", "payments.gateway.read-timeout=1s", "payments.gateway.max-retries=9")
              .run(ctx -> assertThat(ctx).hasFailed().getFailure().rootCause()
                      .hasMessageContaining("readTimeout must be >= connectTimeout").hasMessageContaining("maxRetries"));
    }
}
