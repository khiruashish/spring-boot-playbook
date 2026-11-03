package com.playbook.interview.p03;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.time.temporal.ChronoUnit;

public class DateRangeValidator implements ConstraintValidator<ValidDateRange, BookingRequest> {

    private int maxNights;

    @Override
    public void initialize(ValidDateRange annotation) { this.maxNights = annotation.maxNights(); }

    @Override
    public boolean isValid(BookingRequest r, ConstraintValidatorContext ctx) {
        if (r == null || r.checkIn() == null || r.checkOut() == null) return true;   // @NotNull handles nulls: single responsibility
        long nights = ChronoUnit.DAYS.between(r.checkIn(), r.checkOut());
        if (nights > 0 && nights <= maxNights) return true;
        ctx.disableDefaultConstraintViolation();                                      // attach the error to the checkOut field
        ctx.buildConstraintViolationWithTemplate(ctx.getDefaultConstraintMessageTemplate())
           .addPropertyNode("checkOut").addConstraintViolation();
        return false;
    }
}
