package com.playbook.interview.p10;

import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Configuration;

/** Boot auto-configures a ConcurrentMapCacheManager; in production use Caffeine (local) or Redis (shared) with TTLs. */
@Configuration
@EnableCaching
class CacheConfig { }
