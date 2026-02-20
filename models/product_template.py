from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    name_search_all = fields.Char(
        compute="_compute_name_search_all",
        store=True,
        index=True,
    )
    name_search_all_lower = fields.Char(
        compute="_compute_name_search_all",
        store=True,
        index=True,
    )
    name_search_tsv = fields.Text(
        compute="_compute_name_search_all",
        store=True,
        index=True,
    )

    @api.depends('name')
    def _compute_name_search_all(self):
        """Combine product names in all installed languages and compute tsvector"""
        langs = [lang['code'] for lang in self.env['res.lang'].search([])]
        for record in self:
            names = set()
            for lang_code in langs:
                with record.env.cr.savepoint():
                    names.add(record.with_context(lang=lang_code).name or '')
            names = [n.strip() for n in names if n.strip()]
            combined = " ".join(names)
            record.name_search_all = combined
            record.name_search_all_lower = combined.lower()
            # Use simple space-separated words for tsvector
            record.name_search_tsv = " ".join(combined.split())
