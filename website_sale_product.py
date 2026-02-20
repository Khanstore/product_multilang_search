from odoo import models, api


class WebsiteSaleProduct(models.Model):
    _inherit = 'product.template'

    @api.model
    def _get_search_domain(self, search, category=None, attrib_values=None):
        """
        Override for website product search to use name_search_all
        so search works for both English & Bengali names.
        """
        domain = super()._get_search_domain(
            search, category=category, attrib_values=attrib_values
        )

        if search:
            # Use our multilingual search field instead of name
            domain = [('name_search_all', 'ilike', search)]

        return domain
