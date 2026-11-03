package com.playbook.interview.support;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.context.TestConfiguration;
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Import;
import org.springframework.context.annotation.Primary;
import org.springframework.test.web.servlet.MockMvc;

import java.time.*;

/** All web tests share ONE application context (same config = Spring's test context cache reuses it). */
@SpringBootTest
@AutoConfigureMockMvc
@Import(WebTestBase.TestClockConfig.class)
public abstract class WebTestBase {

    @Autowired protected MockMvc mvc;
    @Autowired protected MutableClock clock;

    /** A clock tests can move forward: no Thread.sleep in tests. */
    public static final class MutableClock extends Clock {
        private Instant now = Instant.parse("2025-01-01T00:00:00Z");
        public void advance(Duration d) { now = now.plus(d); }
        @Override public ZoneId getZone() { return ZoneOffset.UTC; }
        @Override public Clock withZone(ZoneId zone) { return this; }
        @Override public Instant instant() { return now; }
    }

    @TestConfiguration
    static class TestClockConfig {
        @Bean @Primary MutableClock testClock() { return new MutableClock(); }
    }
}
