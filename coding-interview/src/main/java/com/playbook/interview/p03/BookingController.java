package com.playbook.interview.p03;

import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.time.temporal.ChronoUnit;
import java.util.Map;

@RestController
@RequestMapping("/p03/bookings")
class BookingController {
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    Map<String, Object> book(@Valid @RequestBody BookingRequest r) {
        return Map.of("roomType", r.roomType(), "nights", ChronoUnit.DAYS.between(r.checkIn(), r.checkOut()));
    }
}
