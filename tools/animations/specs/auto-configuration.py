import sys
from animlib import Anim

a = Anim("pb-ac", "How Boot decides — <code>JdbcTemplateAutoConfiguration</code> through the selection pipeline",
         "Auto-configuration selection",
         "Your configuration is registered first. AutoConfigurationImportSelector reads every AutoConfiguration.imports "
         "file, removes exclusions, pre-filters with the metadata file, sorts by before/after, then evaluates each "
         "candidate's conditions. For JdbcTemplateAutoConfiguration: OnClass(JdbcTemplate), "
         "OnSingleCandidate(DataSource) and OnMissingBean(JdbcOperations) decide whether Boot's JdbcTemplate, your own, "
         "or none is registered, and every decision goes into the ConditionEvaluationReport.", 800, 320, top=40)

a.text(16, 50, "Auto-configuration import (deferred: runs after your configuration)", "t-sm t-b")
a.box("imp", 16, 60, 140, 64, "AutoConfiguration", extra=[(".imports", "t-b t-11 t-mono"), ("in every JAR", "t-xs t-sub")], title_cls="t-11")
a.box("excl", 170, 60, 130, 64, "Exclusions", ["exclude = …"], sub_mono=True)
a.box("pre", 314, 60, 150, 64, "Pre-filter", ["metadata file:", "OnClass, no class loading"])
a.box("sort", 478, 60, 130, 64, "Sort", ["before / after"], sub_mono=True)
a.box("eval", 622, 60, 162, 64, "Evaluate conditions", ["per class and @Bean"], title_cls="t-11")
a.box("user", 16, 150, 200, 70, "Your @Configuration", ["+ scanned components", "registered FIRST"], title_cls="t-mono t-11")
a.box("registry", 250, 150, 200, 70, "Bean registry", ["what the context will create"])
a.box("report", 250, 240, 200, 64, "Conditions report", ["--debug · /actuator/conditions"], sub_mono=True)

a.route("i2e", [(156, 92), (170, 92)])
a.route("e2p", [(300, 92), (314, 92)])
a.route("p2s", [(464, 92), (478, 92)])
a.route("s2v", [(608, 92), (622, 92)])
a.route("u2r", [(216, 185), (250, 185)])
a.route("v2c", [(703, 124), (703, 150)])
a.route("c2r", [(480, 286), (466, 286), (466, 196), (450, 196)])
a.route("rep", [(560, 304), (560, 312), (466, 312), (466, 272), (450, 272)])

COND = {"match": ("MATCH ✓", "active"), "fail": ("NO MATCH", "rolledback")}
a.chip("c1", 480, 150, 304, "OnClass(JdbcTemplate)", COND)
a.chip("c2", 480, 190, 304, "OnSingleCandidate(DataSource)", COND)
a.chip("c3", 480, 230, 304, "OnMissingBean(JdbcOperations)", {"match": ("MATCH ✓", "active"), "fail": ("BACKS OFF", "suspended")})
a.chip("result", 480, 270, 304, "JdbcTemplate", {"boot": ("BOOT'S DEFAULT", "committed"), "yours": ("YOURS · Boot backed off", "committed"),
                                                 "none": ("NOT CREATED", "rolledback")})
a.chip("cand", 16, 240, 220, "Candidates", {"all": ("ALL", "none"), "excl": ("− EXCLUDED", "none"), "pre": ("− FILTERED", "none"),
                                            "sorted": ("ORDERED", "committed")})

a.scene("boot", "1 · Boot's default", [
    {"path": "u2r", "hl": "user registry", "text": "Your own <code>@Configuration</code> classes and scanned components are registered first. In this app none of them defines a <code>JdbcTemplate</code>."},
    {"hl": "imp", "tx": {"cand": "all"}, "text": "<code>AutoConfigurationImportSelector</code> reads every <code>AutoConfiguration.imports</code> file on the classpath: hundreds of candidates."},
    {"path": "i2e", "hl": "excl", "tx": {"cand": "excl"}, "text": "Exclusions are removed: <code>@SpringBootApplication(exclude = …)</code> and <code>spring.autoconfigure.exclude</code>."},
    {"path": "e2p", "hl": "pre", "tx": {"cand": "pre"}, "text": "A fast pre-filter reads <code>spring-autoconfigure-metadata.properties</code> and drops candidates whose <code>@ConditionalOnClass</code> can't match, <strong>without loading them</strong>."},
    {"path": "p2s", "hl": "sort", "tx": {"cand": "sorted"}, "text": "Survivors are sorted by <code>@AutoConfiguration(before/after)</code>. <code>JdbcTemplateAutoConfiguration</code> runs after <code>DataSourceAutoConfiguration</code>, so a <code>DataSource</code> already exists."},
    {"path": "s2v,v2c", "hl": "eval", "tx": {"c1": "match", "c2": "match"}, "text": "Full evaluation of the class: <code>JdbcTemplate</code> is on the classpath ✓, and there is exactly one <code>DataSource</code> ✓."},
    {"hl": "eval", "tx": {"c3": "match"}, "text": "Then the <code>@Bean</code> method's own condition: is there already a <code>JdbcOperations</code> bean? No, so <code>@ConditionalOnMissingBean</code> matches."},
    {"path": "c2r", "hl": "registry", "tx": {"result": "boot"}, "text": "Boot registers its <code>JdbcTemplate</code>, configured from <code>spring.jdbc.template.*</code> properties."},
    {"path": "rep", "hl": "report", "text": "Every decision is recorded. Run with <code>--debug</code> or open <code>/actuator/conditions</code> to see positive and negative matches, each with its reason."},
])

a.scene("yours", "2 · Your bean wins", [
    {"path": "u2r", "hl": "user registry", "text": "This time your <code>@Configuration</code> declares its own <code>JdbcTemplate</code> (say, with a custom fetch size). It's registered first."},
    {"path": "i2e,e2p,p2s,s2v", "hl": "eval", "tx": {"cand": "sorted"}, "text": "The auto-configuration import is a <code>DeferredImportSelector</code>, so it runs only after all of your configuration…"},
    {"path": "v2c", "hl": "eval", "tx": {"c1": "match", "c2": "match"}, "text": "…and the class-level conditions still match."},
    {"hl": "eval", "tx": {"c3": "fail", "result": "yours"}, "text": "But <code>@ConditionalOnMissingBean(JdbcOperations.class)</code> finds your bean, so Boot <strong>backs off</strong> and its default is never created. The golden rule: <em>your beans win</em>."},
    {"path": "rep", "hl": "report", "text": "The report lists this as a negative match, <em>found beans of type JdbcOperations</em>. It's the first place to look when Boot seems to ignore a default."},
])

a.scene("missing", "3 · Library not on the classpath", [
    {"hl": "imp", "tx": {"cand": "all"}, "text": "Now <code>spring-jdbc</code> isn't on the classpath (say, a WebFlux service using R2DBC). <code>JdbcTemplateAutoConfiguration</code> is still listed in Boot's imports file."},
    {"path": "i2e,e2p", "hl": "pre", "warn": "pre", "tx": {"cand": "pre", "c1": "fail", "result": "none"}, "text": "The pre-filter sees that <code>@ConditionalOnClass(JdbcTemplate.class)</code> can't match and drops the candidate before the class is loaded. That's why a class referring to <code>JdbcTemplate</code> doesn't cause a <code>ClassNotFoundException</code>."},
    {"path": "rep", "hl": "report", "dim": "sort eval", "text": "It still shows up in the report as a negative match: <em>did not find required class</em>."},
])

a.write(sys.argv[1])
