package com.playbook.interview.p03;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

/** Problem 3: a CLASS-level constraint, because "checkOut after checkIn" involves two fields. */
@Target(ElementType.TYPE)
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = DateRangeValidator.class)
@Documented
public @interface ValidDateRange {
    String message() default "checkOut must be after checkIn and the stay at most {maxNights} nights";
    int maxNights() default 30;
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
