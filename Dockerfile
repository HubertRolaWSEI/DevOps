# ETAP 1: BUILD - Budowanie aplikacji
# Używamy obrazu z Mavenem i JDK 17 do skompilowania kodu
FROM maven:3.8.8-eclipse-temurin-17 AS build

# Ustawienie katalogu roboczego w kontenerze
WORKDIR /app

# Kopiowanie plików konfiguracyjnych i kodu źródłowego
COPY pom.xml .
COPY src ./src

# Budowanie aplikacji i utworzenie pliku JAR. Pomiń testy.
RUN mvn clean package -DskipTests

# ETAP 2: RUN - Uruchomienie aplikacji
# Używamy lekkiego obrazu z samym JRE 17 do uruchomienia gotowej aplikacji
FROM eclipse-temurin:17-jdk-jammy

# Ustawienie katalogu roboczego
WORKDIR /app

# Skopiowanie zbudowanej jarki z pierwszego etapu
COPY --from=build /app/target/demoWeb-0.0.1-SNAPSHOT.jar /app/demoWeb.jar

# Wystawienie portu 8080, na którym działa aplikacja Spring Boot
EXPOSE 8080

# Definicja polecenia, które zostanie uruchomione przy starcie kontenera
ENTRYPOINT ["java", "-jar", "/app/demoWeb.jar"]
