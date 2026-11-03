package com.playbook.interview.p11;

import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClient;

import java.util.Optional;

/** Problem 11: an HTTP client with RestClient: base URL, error mapping, and a typed result. Tested with MockRestServiceServer. */
@Component
public class WeatherClient {

    public record Forecast(String city, double tempC, String summary) { }

    public static class WeatherUnavailableException extends RuntimeException {
        public WeatherUnavailableException(String m) { super(m); }
    }

    private final RestClient http;

    public WeatherClient(RestClient.Builder builder) {                         // inject the Boot-configured builder
        this.http = builder.baseUrl("https://weather.example.com").build();
    }

    /** 200 -> Forecast; 404 -> Optional.empty(); 5xx -> domain exception (a caller can retry or fall back). */
    public Optional<Forecast> forecast(String city) {
        try {
            return Optional.ofNullable(http.get()
                    .uri("/v1/forecast/{city}", city)                               // URI template: city is encoded safely
                    .accept(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .onStatus(HttpStatusCode::is5xxServerError, (req, res) -> {
                        throw new WeatherUnavailableException("weather service returned " + res.getStatusCode().value());
                    })
                    .body(Forecast.class));
        } catch (HttpClientErrorException.NotFound e) {
            return Optional.empty();
        }
    }
}
