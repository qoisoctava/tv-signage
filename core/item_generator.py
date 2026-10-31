"""
Item Generator
==============
Generate file HTML statis dari template + field_data,
simpan ke generated_items/, dan bersihkan file lama.
"""

import os
import uuid
from flask import current_app
from core.template_parser import render_template, read_template_file


def generate_item_file(item, html_content=None):
    """
    Generate file HTML untuk item dari tipe 'html'.
    - Jika html_content None, baca dari template file di disk.
    - Simpan hasil ke generated_items/item_{id}_{hash}.html
    - Return path relatif file yang disimpan, atau None jika gagal.
    """
    if html_content is None:
        if not item.template:
            return None
        tmpl_path = os.path.join(
            current_app.config['TEMPLATES_STORE'],
            item.template.filename
        )
        html_content = read_template_file(tmpl_path)
        if html_content is None:
            return None

    rendered = render_template(html_content, item.field_data or {})

    # Hapus file lama jika ada
    if item.generated_file:
        delete_generated_file(item.generated_file)

    gen_dir = current_app.config['GENERATED_ITEMS']
    filename = f"item_{item.id}_{uuid.uuid4().hex[:8]}.html"
    abs_path = os.path.join(gen_dir, filename)

    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(rendered)

    return filename


def delete_generated_file(filename):
    """Hapus file generated dari disk."""
    if not filename:
        return
    gen_dir = current_app.config['GENERATED_ITEMS']
    abs_path = os.path.join(gen_dir, filename)
    if os.path.exists(abs_path):
        os.remove(abs_path)


def get_generated_url(filename):
    """Return URL untuk akses file generated."""
    if not filename:
        return None
    return f"/generated/{filename}"
