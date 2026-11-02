package com.playbook.interview;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.Customizer;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.web.SecurityFilterChain;

/**
 * Problems 1-11 are public endpoints; problem 12 (/p12/**) requires authentication and uses method security.
 * Stateless API: no sessions, no CSRF tokens (CSRF protects cookie-authenticated browser sessions).
 */
@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    @Bean
    SecurityFilterChain api(HttpSecurity http) throws Exception {
        http.csrf(csrf -> csrf.disable())
            .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                    .requestMatchers("/p12/**").authenticated()
                    .anyRequest().permitAll())
            .httpBasic(Customizer.withDefaults());
        return http.build();
    }
}
