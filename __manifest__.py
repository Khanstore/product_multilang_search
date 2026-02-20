{
    "name": "Product Multilingual Search Pro V3",
    "version": "18.0.5.0.0",
    "category": "Website",
    "summary": "Fast multilingual product search with full-text ranking, relevance ordering, all languages, cache, and cron",
    "description": """
Advanced multilingual product search for Odoo 18
- Full-text ranking (most relevant products first)
- All installed languages included
- Multi-word partial search
- Optimized for large catalogs
- Automatic cache updates via triggers
- Daily cron batch update
- Website search integration
- Fast search with PostgreSQL pg_trgm
""",
    "author": "SM Ashraf",
    "website": "https://www.khan-store.com",
    "license": "LGPL-3",
    "images": [
        "static/description/icon.png",
        "static/description/screenshot1.png"
    ],
    "depends": ["product", "website_sale", "base"],
    "data": [
        "data/product_search_cache.sql",
        "data/cron_refresh_cache.xml"
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
}
