package com.playbook.interview.p03;

import jakarta.validation.ConstraintValidator;
import jakarta.validation.ConstraintValidatorContext;

import java.util.Set;

/** A field-level validator that is a Spring bean, so it could inject a repository (here: a fixed catalogue). */
public class SkuValidator implements ConstraintValidator<KnownSku, String> {
    private static final Set<String> CATALOGUE = Set.of("ROOM-STD", "ROOM-DLX", "ROOM-STE");

    @Override
    public boolean isValid(String sku, ConstraintValidatorContext ctx) { return sku == null || CATALOGUE.contains(sku); }
}
