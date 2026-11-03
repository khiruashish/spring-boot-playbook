package com.playbook.interview.p11;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.restclient.test.autoconfigure.RestClientTest;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;

import static org.assertj.core.api.Assertions.*;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;

/** @RestClientTest: only the client + Jackson + a MockRestServiceServer bound to the RestClient.Builder. No network. */
@RestClientTest(WeatherClient.class)
class WeatherClientTest {

    @Autowired WeatherClient client;
    @Autowired MockRestServiceServer server;

    @Test
    void ok_mapsJsonToRecord() {
        server.expect(requestTo("https://weather.example.com/v1/forecast/Pune"))
              .andExpect(header("Accept", MediaType.APPLICATION_JSON_VALUE))
              .andRespond(withSuccess("""
                      {"city":"Pune","tempC":31.5,"summary":"Sunny"}""", MediaType.APPLICATION_JSON));
        assertThat(client.forecast("Pune")).contains(new WeatherClient.Forecast("Pune", 31.5, "Sunny"));
        server.verify();
    }

    @Test
    void notFound_becomesEmptyOptional() {
        server.expect(requestTo("https://weather.example.com/v1/forecast/Atlantis")).andRespond(withStatus(HttpStatus.NOT_FOUND));
        assertThat(client.forecast("Atlantis")).isEmpty();
    }

    @Test
    void serverError_becomesDomainException() {
        server.expect(requestTo("https://weather.example.com/v1/forecast/Delhi")).andRespond(withServerError());
        assertThatThrownBy(() -> client.forecast("Delhi")).isInstanceOf(WeatherClient.WeatherUnavailableException.class).hasMessageContaining("500");
    }

    @Test
    void pathVariablesAreEncoded() {
        server.expect(requestTo("https://weather.example.com/v1/forecast/New%20York")).andRespond(withSuccess("""
                {"city":"New York","tempC":4.0,"summary":"Snow"}""", MediaType.APPLICATION_JSON));
        assertThat(client.forecast("New York")).isPresent();
    }
}
