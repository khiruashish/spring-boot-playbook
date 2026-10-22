# Setup

## 1. JDKs via SDKMAN

We use **Java 21** for Spring Boot 3.5 examples and **Java 25** for Spring Boot 4.x examples.

```bash title="Install SDKMAN and JDKs"
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

sdk list java | grep -E "21\.|25\."   # pick current Temurin builds
sdk install java 21.0.x-tem           # replace x with the latest patch shown
sdk install java 25.0.x-tem
sdk default java 25.0.x-tem

java -version
```

!!! tip "Per-project JDK"
    Add a `.sdkmanrc` file (`java=25.0.x-tem`) to the repo root and run `sdk env`. Gradle toolchains (Chapter 01) make the build itself independent of your shell JDK.

## 2. Build tools

- **Gradle 9** via the wrapper — you never install Gradle globally for a project; `./gradlew` downloads the pinned version.
- **Maven 3.9+** — only needed if you follow the Maven tabs (`sdk install maven`).

## 3. IDE

| IDE | Notes |
|---|---|
| IntelliJ IDEA (Ultimate or Community) | Best Spring support; enable *Build and run using: Gradle* |
| VS Code | Install *Extension Pack for Java* + *Spring Boot Extension Pack* |
| Eclipse / Spring Tools | Spring Tools 4 plugin |

Enable annotation processing (needed for the configuration-properties metadata processor).

## 4. Docker

Docker Desktop, Rancher Desktop, Colima or Podman. Required for Testcontainers, `spring-boot-docker-compose`, and Buildpacks.

```bash
docker run --rm hello-world
```

## 5. Companion repository layout

```text title="grocery-handbook/"
grocery-handbook/
├── settings.gradle.kts
├── gradle/
│   ├── libs.versions.toml          # version catalog
│   └── wrapper/
├── build-logic/                    # convention plugins (Chapter 01, Level 4)
│   └── src/main/kotlin/
│       ├── grocery.java-conventions.gradle.kts
│       └── grocery.spring-service.gradle.kts
├── libs/
│   └── grocery-common/             # Money, Pincode, GST types
├── services/
│   ├── catalog-service/
│   ├── cart-service/
│   ├── order-service/
│   └── ...
└── handbook/                       # this MkDocs site
    ├── mkdocs.yml
    └── docs/
```

## 6. Run this handbook locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve        # http://127.0.0.1:8000
mkdocs build        # static site in ./site
```
