1️⃣ Enable PostgreSQL pg_trgm extension

This allows fast ILIKE searches using trigrams.

CREATE EXTENSION IF NOT EXISTS pg_trgm;

Run this in your database (via psql or pgAdmin)

You need superuser privileges

Then we can create trigram index on the name_search_all field.

2️⃣ Create a cache table for search

Instead of querying product_template directly every time:

CREATE TABLE product_search_cache (
    product_id bigint PRIMARY KEY,
    name_search_all text
);

product_id → product_template.id

name_search_all → combined English + Bengali string

This avoids recomputing JSON translations on every search.

3️⃣ Add a trigram index on the cache
CREATE INDEX product_search_cache_trgm_idx
ON product_search_cache
USING gin (name_search_all gin_trgm_ops);

✅ Now ILIKE queries are very fast even on 100k+ products.

4️⃣ Maintain cache using ON CONFLICT UPDATE triggers
Step 1: Create function
CREATE OR REPLACE FUNCTION update_product_search_cache() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO product_search_cache (product_id, name_search_all)
    VALUES (NEW.id,
            coalesce(NEW.name_search_all, ''))
    ON CONFLICT (product_id)
    DO UPDATE SET name_search_all = EXCLUDED.name_search_all;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
Step 2: Create trigger
CREATE TRIGGER trg_update_product_search_cache
AFTER INSERT OR UPDATE ON product_template
FOR EACH ROW
EXECUTE FUNCTION update_product_search_cache();

✅ Now every time product_template is updated (including translations), the cache table is updated automatically.

5️⃣ Use cache in website search

Override _get_search_domain to query cache table:

from odoo import models, api


class WebsiteSaleProduct(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_search_domain(self, search, category=None, attrib_values=None):
        if not search:
            return super()._get_search_domain(search, category, attrib_values)

        # Query product IDs from cache
        self.env.cr.execute("""
            SELECT product_id
            FROM product_search_cache
            WHERE name_search_all ILIKE %s
        """, (f'%{search}%',))
        product_ids = [r[0] for r in self.env.cr.fetchall()]

        # Limit results if necessary
        return [('id', 'in', product_ids)]
6️⃣ Advantages

✅ Extremely fast search (even 100k+ products)
✅ Supports multilingual search (English + Bengali)
✅ Fully indexable via trigram
✅ Automatic cache updates using triggers

7️⃣ Optional Improvements

Use GIN + pg_trgm index on both product_search_cache.name_search_all and a normalized lower() column for case-insensitive search.

Add batch update for existing products:

INSERT INTO product_search_cache(product_id, name_search_all)
SELECT id, name_search_all FROM product_template
ON CONFLICT (product_id) DO UPDATE
SET name_search_all = EXCLUDED.name_search_all;

For very large catalogs, schedule a cron job to refresh cache nightly.
