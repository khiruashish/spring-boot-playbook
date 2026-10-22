# A · Interview Bank

341 questions with answers across five experience bands, plus system design and rapid-fire revision. It draws on the interview sections of all 44 chapters, adds cross-cutting questions that span several chapters, and is organized for two audiences: **candidates preparing** and **interviewers running structured interviews** (Chapter 43).

## How the bands work

| Band | Experience | What the questions test |
|---|---|---|
| [B1 · 0–2 years](b1-0-2-years.md) | Junior | Vocabulary and mechanics: what things are and how to use them |
| [B2 · 2–5 years](b2-2-5-years.md) | Mid-level | Correct use under normal conditions; common pitfalls |
| [B3 · 5–8 years](b3-5-8-years.md) | Senior | How things work internally; failure modes; design within a service |
| [B4 · 8–12 years](b4-8-12-years.md) | Staff / lead | Cross-service design, operations, trade-offs, platform decisions |
| [B5 · 12–15+ years](b5-12-15-years.md) | Principal / architect | Strategy, organization, risk, and when *not* to use something |
| [System Design](system-design.md) | B3–B5 | Grocery-domain design problems with model answers |
| [Rapid Fire](rapid-fire.md) | All | One-line answers for last-minute revision |

Bands describe **depth of reasoning**, not years alone. A strong B2 candidate who explains *why* `@Transactional` fails on self-invocation, and what the proxy is doing, is showing B3 reasoning.

## For candidates

1. Read your band and the one above it. Interviews usually probe one level higher than the role to find the ceiling.
2. Answer aloud before expanding the answer. The short answers here are **deliberately short** — a real answer adds an example from your own work.
3. For every "how does X work?", be ready for "what happens when it fails?" — that follow-up separates bands more than any other.
4. Build the capstone milestones (Chapter 44). A design question answered with "here's what I built and what broke" is far stronger than a textbook answer.

## For interviewers

| Stage | Suggested use |
|---|---|
| Phone screen | 4–6 questions from the candidate's band, across different chapters |
| Technical depth | Pick one domain, start one band below the role and follow the candidate upward |
| System design | One problem from the system-design page, scored with the rubric in Chapter 43 |
| Rapid fire | Warm-up or calibration only — never as a pass/fail filter |

**Follow the answer, not the script.** The best signal comes from the second and third follow-up questions, which is why each answer here names the chapter where the deeper material lives.

## Answer format

Each question uses a collapsible block with a **short answer** — the core of what a good response contains — and a chapter reference for depth:

??? question "B2 · Example: why does `@Transactional` not work on a private method?"
    **Short answer:** Spring applies transactions through a proxy; calls to private methods (and self-invocations) don't pass through the proxy, so no transaction starts. **See Chapters 04, 16.**

## Topic coverage by band

| Topic | B1 | B2 | B3 | B4 | B5 |
|---|---|---|---|---|---|
| Java, build, Boot fundamentals (01, 05) | ● | ● | ● | | |
| IoC, lifecycle, AOP (02–04) | ● | ● | ● | | |
| Configuration, logging (06, 07) | ● | ● | ● | ● | |
| REST, validation, errors, JSON (08–11) | ● | ● | ● | ● | |
| Data, JPA, migrations, transactions (12–16) | ● | ● | ● | ● | ● |
| Security and tokens (17, 18, 39) | ● | ● | ● | ● | ● |
| Clients, APIs, caching (19–21) | ● | ● | ● | ● | |
| NoSQL, messaging (22–24) | ● | ● | ● | ● | ● |
| Async, resilience, observability (25–27) | | ● | ● | ● | ● |
| Testing, packaging, Kubernetes (15, 28–30) | ● | ● | ● | ● | |
| Reactive, protocols, batch, performance (31–34) | | ● | ● | ● | ● |
| Microservices, consistency, architecture (35–37) | | ● | ● | ● | ● |
| Tenancy, AI, internals, upgrades (38, 40–42) | | ● | ● | ● | ● |
| Leadership (43) | | | ● | ● | ● |

---

[:material-arrow-left: Appendices](../index.md) · [B1 · 0–2 years :material-arrow-right:](b1-0-2-years.md)
