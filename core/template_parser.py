"""
Template Parser
===============
Membaca file HTML template di signage_templates/ dan mengekstrak
field definition dari sintaks {{nama:tipe:label:default}}.

Format field:
  {{nama_field:tipe:Label:default_value}}

Tipe yang didukung:
  text, textarea, image, color, number
"""

import re
import os

# Regex untuk menangkap field: {{name:type:label:default}}
FIELD_PATTERN = re.compile(
    r'\{\{(\w+)(?::([a-z]+))?(?::([^:}]*))?(?::([^}]*))?\}\}'
)

VALID_TYPES = {'text', 'textarea', 'image', 'color', 'number'}

DEFAULT_TYPE = 'text'


def parse_fields(html_content):
    """
    Ekstrak semua field dari konten HTML template.
    Return list of dict, urutan sesuai kemunculan di template,
    duplikat (nama sama) diambil yang pertama.

    Contoh return:
    [
        {'name': 'judul',    'type': 'text',     'label': 'Judul Iklan',  'default': ''},
        {'name': 'gambar',   'type': 'image',    'label': 'Foto Produk',  'default': ''},
        {'name': 'bg_color', 'type': 'color',    'label': 'Warna BG',     'default': '#000000'},
    ]
    """
    seen = set()
    fields = []

    for match in FIELD_PATTERN.finditer(html_content):
        name    = match.group(1)
        ftype   = (match.group(2) or DEFAULT_TYPE).lower()
        label   = match.group(3) or name.replace('_', ' ').title()
        default = match.group(4) or ''

        if name in seen:
            continue
        seen.add(name)

        if ftype not in VALID_TYPES:
            ftype = DEFAULT_TYPE

        fields.append({
            'name':    name,
            'type':    ftype,
            'label':   label,
            'default': default,
        })

    return fields


def render_template(html_content, field_data):
    """
    Ganti semua {{field...}} dengan value dari field_data.
    field_data: dict {nama_field: value}
    Return HTML string yang sudah dirender.
    """
    def replacer(match):
        name    = match.group(1)
        default = match.group(4) or ''
        return str(field_data.get(name, default))

    return FIELD_PATTERN.sub(replacer, html_content)


def read_template_file(filepath):
    """Baca isi file template. Return string atau None jika tidak ada."""
    if not os.path.exists(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()


def parse_template_file(filepath):
    """
    Baca file template dan langsung return fields.
    Return (html_content, fields) atau (None, []) jika file tidak ada.
    """
    content = read_template_file(filepath)
    if content is None:
        return None, []
    return content, parse_fields(content)
