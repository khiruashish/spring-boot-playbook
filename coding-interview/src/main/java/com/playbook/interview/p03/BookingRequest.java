package com.playbook.interview.p03;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotNull;

import java.time.LocalDate;

@ValidDateRange(maxNights = 14)
public record BookingRequest(@NotNull LocalDate checkIn, @NotNull LocalDate checkOut, @NotNull @KnownSku String roomType, @Min(1) int guests) { }
