package com.playbook.interview.p03;

import jakarta.validation.Constraint;
import jakarta.validation.Payload;

import java.lang.annotation.*;

@Target({ElementType.FIELD, ElementType.PARAMETER, ElementType.RECORD_COMPONENT})
@Retention(RetentionPolicy.RUNTIME)
@Constraint(validatedBy = SkuValidator.class)
public @interface KnownSku {
    String message() default "unknown room type";
    Class<?>[] groups() default {};
    Class<? extends Payload>[] payload() default {};
}
