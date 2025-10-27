-- Migration: Add enriched fields to pokemon table
-- Add derived fields computed by enrich_and_derive

ALTER TABLE pokemon 
ADD COLUMN IF NOT EXISTS height_m DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS weight_kg DOUBLE PRECISION,
ADD COLUMN IF NOT EXISTS base_stat_total INTEGER,
ADD COLUMN IF NOT EXISTS bulk_index DOUBLE PRECISION;

-- Optional: Add comments to document the fields
COMMENT ON COLUMN pokemon.height_m IS 'Height in meters (computed from height in decimeters)';
COMMENT ON COLUMN pokemon.weight_kg IS 'Weight in kilograms (computed from weight in hectograms)';
COMMENT ON COLUMN pokemon.base_stat_total IS 'Sum of the 6 standard Pokemon stats (hp, attack, defense, special-attack, special-defense, speed)';
COMMENT ON COLUMN pokemon.bulk_index IS 'BMI-like metric: kg / (m ** 2)';
