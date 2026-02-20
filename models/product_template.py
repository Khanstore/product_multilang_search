from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name_search_all = fields.Char(
        compute="_compute_name_search_all",
        store=True,
        index=True,
    )

    @api.depends('name')
    def _compute_name_search_all(self):
        """
        Combine English + Bengali translations of product name
        into a single stored indexable field.
        """
        for record in self:
            en_name = record.with_context(lang='en_US').name or ''
            bn_name = record.with_context(lang='bn_BD').name or ''

            # Only include non-empty values
            parts = [p for p in (en_name, bn_name) if p]
            record.name_search_all = " ".join(parts)

    def write(self, vals):
        """
        Recompute name_search_all when 'name' changes.
        """
        # Detect if product name JSON is being updated
        trigger = 'name' in vals

        result = super().write(vals)

        if trigger:
            self.invalidate_recordset(['name_search_all'])
            self.recompute()

        return result
