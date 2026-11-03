package com.playbook.interview;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import java.time.Clock;

/** One application hosts all twelve solutions; each lives in its own package (p01..p12). */
@SpringBootApplication
public class InterviewApplication {
    public static void main(String[] args) {
        SpringApplication.run(InterviewApplication.class, args);
    }

    /** Inject time instead of calling Instant.now(): tests replace it with a @Primary controllable clock. */
    @Bean
    Clock clock() { return Clock.systemUTC(); }
}
