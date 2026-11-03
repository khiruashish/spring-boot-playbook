package com.playbook.interview.p03;

import com.playbook.interview.support.WebTestBase;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import org.junit.jupiter.api.Test;

import java.time.LocalDate;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

class BookingValidationTest extends WebTestBase {

    private final Validator validator = Validation.buildDefaultValidatorFactory().getValidator();

    @Test
    void validator_unit_reportsCrossFieldErrorOnCheckOut() {
        var r = new BookingRequest(LocalDate.of(2025, 3, 10), LocalDate.of(2025, 3, 8), "ROOM-STD", 2);
        var violations = validator.validate(r);
        assertThat(violations).hasSize(1);
        assertThat(violations.iterator().next().getPropertyPath().toString()).isEqualTo("checkOut");
    }

    @Test
    void validator_unit_enforcesMaxNightsFromTheAnnotation() {
        var r = new BookingRequest(LocalDate.of(2025, 3, 1), LocalDate.of(2025, 3, 20), "ROOM-STD", 2);
        assertThat(validator.validate(r)).extracting(v -> v.getMessage()).containsExactly("checkOut must be after checkIn and the stay at most 14 nights");
    }

    @Test
    void validator_unit_unknownRoomType() {
        var r = new BookingRequest(LocalDate.of(2025, 3, 1), LocalDate.of(2025, 3, 3), "ROOM-XXL", 2);
        assertThat(validator.validate(r)).extracting(v -> v.getMessage()).containsExactly("unknown room type");
    }

    @Test
    void endpoint_validBooking_201() throws Exception {
        mvc.perform(post("/p03/bookings").contentType("application/json").content("""
                {"checkIn":"2025-03-01","checkOut":"2025-03-04","roomType":"ROOM-DLX","guests":2}"""))
           .andExpect(status().isCreated()).andExpect(jsonPath("$.nights").value(3));
    }

    @Test
    void endpoint_invalidRange_400() throws Exception {
        mvc.perform(post("/p03/bookings").contentType("application/json").content("""
                {"checkIn":"2025-03-04","checkOut":"2025-03-01","roomType":"ROOM-DLX","guests":2}"""))
           .andExpect(status().isBadRequest());
    }
}
