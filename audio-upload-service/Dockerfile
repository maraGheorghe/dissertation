# =========================
# Build Stage (Alpine)
# =========================
FROM gradle:8-jdk17 AS build
WORKDIR /app

# Copy Gradle metadata first for better caching
COPY build.gradle settings.gradle ./
COPY gradle/ ./gradle/

# (No ffmpeg here since you only need it at runtime)
# Pre-fetch dependencies to leverage cache
RUN --mount=type=cache,target=/home/gradle/.gradle \
    gradle dependencies --no-daemon

# Copy the rest and build
COPY . .
RUN --mount=type=cache,target=/home/gradle/.gradle \
    gradle build -x test --no-daemon


# =========================
# Runtime Stage (Debian)
# =========================
FROM openjdk:17-jdk-slim
WORKDIR /app

# Install ffmpeg at runtime (no sudo needed; you're root)
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir /app/tmp

# Copy the built jar
COPY --from=build /app/build/libs/*.jar app.jar

EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
