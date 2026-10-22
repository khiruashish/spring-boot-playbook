# Spring Boot 3 & 4 Enterprise Handbook

MkDocs Material site. Beginner → 15+ years. Spring Boot 3.5 and 4.x side by side, grounded in a multi-vendor grocery marketplace.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve
```

Status: complete — 44 chapters (Parts 0–3) and appendices A–H. Builds cleanly with `mkdocs build --strict`.

## PDF

A single-file PDF of the whole handbook can be generated with the scripts in `tools/pdf/` (see its README).

## Deployment

Every push to `main` builds the site with `mkdocs build --strict` and publishes it to the `gh-pages` branch
(`.github/workflows/deploy.yml`). Live site: https://khiruashish.github.io/spring-boot-playbook/
