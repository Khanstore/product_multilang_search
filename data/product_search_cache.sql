-- Enable pg_trgm extension
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Cache table
CREATE TABLE IF NOT EXISTS product_search_cache (
    product_id bigint PRIMARY KEY,
    name_search_all text,
    name_search_all_lower text,
    name_search_tsv tsvector
);

-- Trigram index
CREATE INDEX IF NOT EXISTS product_search_cache_trgm_idx
ON product_search_cache USING gin (name_search_all_lower gin_trgm_ops);

-- Full-text index
CREATE INDEX IF NOT EXISTS product_search_cache_tsv_idx
ON product_search_cache USING gin (name_search_tsv);

-- Function to update cache
CREATE OR REPLACE FUNCTION update_product_search_cache() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO product_search_cache(product_id, name_search_all, name_search_all_lower, name_search_tsv)
    VALUES (
        NEW.id,
        COALESCE(NEW.name_search_all, ''),
        COALESCE(LOWER(NEW.name_search_all), ''),
        to_tsvector('simple', COALESCE(NEW.name_search_all, ''))
    )
    ON CONFLICT (product_id)
    DO UPDATE SET
        name_search_all = EXCLUDED.name_search_all,
        name_search_all_lower = EXCLUDED.name_search_all_lower,
        name_search_tsv = EXCLUDED.name_search_tsv;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
DROP TRIGGER IF EXISTS trg_update_product_search_cache ON product_template;
CREATE TRIGGER trg_update_product_search_cache
AFTER INSERT OR UPDATE OF name_search_all ON product_template
FOR EACH ROW
EXECUTE FUNCTION update_product_search_cache();

-- Initialize cache
INSERT INTO product_search_cache(product_id, name_search_all, name_search_all_lower, name_search_tsv)
SELECT id, name_search_all, LOWER(name_search_all), to_tsvector('simple', name_search_all)
FROM product_template
ON CONFLICT (product_id) DO UPDATE
SET name_search_all = EXCLUDED.name_search_all,
    name_search_all_lower = EXCLUDED.name_search_all_lower,
    name_search_tsv = EXCLUDED.name_search_tsv;
