package com.playbook.interview.p08;

import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;

/**
 * Problem 8: a custom auto-configuration. Registered in
 * META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports, which also keeps it out of component scanning.
 */
@AutoConfiguration
@ConditionalOnProperty(prefix = "greeting", name = "enabled", havingValue = "true", matchIfMissing = true)
@EnableConfigurationProperties(GreetingProperties.class)
public class GreetingAutoConfiguration {

    /** Back off if the application defines its own GreetingService: user beans always win. */
    @Bean
    @ConditionalOnMissingBean
    GreetingService greetingService(GreetingProperties props) {
        return name -> props.prefix() + ", " + name + "!";
    }
}
