package com.playbook.interview.p06;

import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.InterceptorRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
class WebConfig implements WebMvcConfigurer {
    private final RateLimitInterceptor rateLimit;
    WebConfig(RateLimitInterceptor rateLimit) { this.rateLimit = rateLimit; }

    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(rateLimit).addPathPatterns("/p06/**");      // scope it: only the limited API
    }
}
