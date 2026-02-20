from odoo import models, api


class WebsiteSaleProduct(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_search_domain(self, search, category=None, attrib_values=None):
        """Use product_search_cache for fast multilingual website search with ranking"""
        if not search:
            return super()._get_search_domain(search, category=category, attrib_values=attrib_values)

        search_lower = search.lower()
        keywords = search_lower.split()

        # Build full-text query
        query = """
            SELECT product_id,
                   ts_rank(to_tsvector('simple', name_search_all_lower), plainto_tsquery('simple', %s)) AS rank
            FROM product_search_cache
            WHERE name_search_all_lower ILIKE %s
            ORDER BY rank DESC
            LIMIT 100
        """
        params = [search_lower, f"%{search_lower}%"]

        self.env.cr.execute(query, params)
        product_ids = [r[0] for r in self.env.cr.fetchall()]

        return [('id', 'in', product_ids)]
