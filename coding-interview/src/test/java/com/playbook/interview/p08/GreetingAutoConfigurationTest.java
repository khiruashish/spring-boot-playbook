package com.playbook.interview.p08;

import org.junit.jupiter.api.Test;
import org.springframework.boot.autoconfigure.AutoConfigurations;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import static org.assertj.core.api.Assertions.assertThat;

/** ApplicationContextRunner: start tiny contexts in milliseconds, one per scenario. */
class GreetingAutoConfigurationTest {

    private final ApplicationContextRunner runner = new ApplicationContextRunner()
            .withConfiguration(AutoConfigurations.of(GreetingAutoConfiguration.class));

    @Test
    void createsDefaultBean() {
        runner.run(ctx -> assertThat(ctx.getBean(GreetingService.class).greet("Ana")).isEqualTo("Hello, Ana!"));
    }

    @Test
    void bindsProperties() {
        runner.withPropertyValues("greeting.prefix=Namaste")
              .run(ctx -> assertThat(ctx.getBean(GreetingService.class).greet("Ana")).isEqualTo("Namaste, Ana!"));
    }

    @Test
    void backsOffWhenUserDefinesTheirOwnBean() {
        runner.withUserConfiguration(CustomGreeting.class)
              .run(ctx -> {
                  assertThat(ctx).hasSingleBean(GreetingService.class);
                  assertThat(ctx.getBean(GreetingService.class).greet("Ana")).isEqualTo("Hi Ana (custom)");
              });
    }

    @Test
    void canBeSwitchedOff() {
        runner.withPropertyValues("greeting.enabled=false").run(ctx -> assertThat(ctx).doesNotHaveBean(GreetingService.class));
    }

    @Configuration
    static class CustomGreeting {
        @Bean GreetingService custom() { return name -> "Hi " + name + " (custom)"; }
    }
}
