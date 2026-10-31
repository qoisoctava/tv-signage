import os
from flask import Blueprint, jsonify, request, current_app
from core.models import db, MediaFile, TemplateFile, Item, Channel, PlaylistItem
from core.file_manager import save_upload, delete_upload, format_size
from core.template_parser import parse_template_file, parse_fields, read_template_file
from core.item_generator import generate_item_file, delete_generated_file, get_generated_url

bp = Blueprint('api', __name__, url_prefix='/api')


# ─── Status ───────────────────────────────────────────────────────────────────

@bp.route('/status')
def status():
    return jsonify({
        'status': 'ok',
        'counts': {
            'media': MediaFile.query.count(),
            'templates': TemplateFile.query.count(),
            'items': Item.query.count(),
            'channels': Channel.query.count(),
        }
    })


# ─── Media ────────────────────────────────────────────────────────────────────

@bp.route('/media', methods=['GET'])
def media_list():
    type_filter = request.args.get('type')
    q = MediaFile.query.order_by(MediaFile.created_at.desc())
    if type_filter in ('image', 'video'):
        q = q.filter_by(type=type_filter)
    return jsonify([{
        **m.to_dict(),
        'size_label': format_size(m.size),
        'url': f"/static/{m.path}",
    } for m in q.all()])


@bp.route('/media/upload', methods=['POST'])
def media_upload():
    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'Tidak ada file'}), 400

    results, errors = [], []
    for file in files:
        saved = save_upload(file)
        if not saved:
            errors.append(file.filename)
            continue
        media = MediaFile(
            name=saved['original_name'],
            filename=saved['filename'],
            type=saved['type'],
            path=saved['path'],
            size=saved['size'],
        )
        db.session.add(media)
        db.session.flush()
        results.append({
            **media.to_dict(),
            'size_label': format_size(media.size),
            'url': f"/static/{media.path}",
        })

    db.session.commit()
    return jsonify({'uploaded': results, 'errors': errors}), 201


@bp.route('/media/<int:media_id>', methods=['DELETE'])
def media_delete(media_id):
    media = MediaFile.query.get_or_404(media_id)
    used_by = Item.query.filter_by(media_id=media_id).count()
    if used_by > 0:
        return jsonify({'error': f'Media masih digunakan oleh {used_by} item.'}), 409
    delete_upload(media.path)
    db.session.delete(media)
    db.session.commit()
    return jsonify({'deleted': media_id})


# ─── Templates ────────────────────────────────────────────────────────────────

@bp.route('/templates', methods=['GET'])
def templates_list():
    templates = TemplateFile.query.order_by(TemplateFile.created_at.desc()).all()
    result = []
    for t in templates:
        d = t.to_dict()
        d['item_count'] = Item.query.filter_by(template_id=t.id).count()
        result.append(d)
    return jsonify(result)


@bp.route('/templates', methods=['POST'])
def templates_create():
    """Daftarkan template HTML yang sudah ada di signage_templates/."""
    data = request.get_json()
    name     = (data.get('name') or '').strip()
    filename = (data.get('filename') or '').strip()
    desc     = (data.get('description') or '').strip()

    if not name or not filename:
        return jsonify({'error': 'name dan filename wajib diisi'}), 400

    # Pastikan file ada di disk
    tmpl_path = os.path.join(current_app.config['TEMPLATES_STORE'], filename)
    if not os.path.exists(tmpl_path):
        return jsonify({'error': f'File {filename} tidak ditemukan di signage_templates/'}), 404

    # Cek duplikat filename
    if TemplateFile.query.filter_by(filename=filename).first():
        return jsonify({'error': 'Filename sudah terdaftar'}), 409

    tmpl = TemplateFile(name=name, filename=filename, description=desc)
    db.session.add(tmpl)
    db.session.commit()
    return jsonify(tmpl.to_dict()), 201


@bp.route('/templates/upload', methods=['POST'])
def templates_upload():
    """Upload file HTML baru ke signage_templates/ dan daftarkan."""
    if 'file' not in request.files:
        return jsonify({'error': 'Tidak ada file'}), 400

    file = request.files['file']
    name = (request.form.get('name') or '').strip()
    desc = (request.form.get('description') or '').strip()

    if not file.filename.endswith('.html'):
        return jsonify({'error': 'Hanya file .html yang diperbolehkan'}), 400

    if not name:
        name = file.filename.rsplit('.', 1)[0].replace('_', ' ').title()

    from werkzeug.utils import secure_filename
    filename = secure_filename(file.filename)
    tmpl_dir = current_app.config['TEMPLATES_STORE']
    save_path = os.path.join(tmpl_dir, filename)

    # Jangan overwrite
    if os.path.exists(save_path):
        base, ext = filename.rsplit('.', 1)
        import uuid
        filename = f"{base}_{uuid.uuid4().hex[:6]}.{ext}"
        save_path = os.path.join(tmpl_dir, filename)

    file.save(save_path)

    # Baca dan parse fields langsung
    with open(save_path, 'r', encoding='utf-8') as f:
        content = f.read()
    fields = parse_fields(content)

    tmpl = TemplateFile(name=name, filename=filename, description=desc)
    db.session.add(tmpl)
    db.session.commit()

    return jsonify({**tmpl.to_dict(), 'fields': fields}), 201


@bp.route('/templates/<int:tmpl_id>', methods=['DELETE'])
def templates_delete(tmpl_id):
    tmpl = TemplateFile.query.get_or_404(tmpl_id)
    used = Item.query.filter_by(template_id=tmpl_id).count()
    if used > 0:
        return jsonify({'error': f'Template masih digunakan oleh {used} item.'}), 409
    # Hapus file dari disk
    tmpl_path = os.path.join(current_app.config['TEMPLATES_STORE'], tmpl.filename)
    if os.path.exists(tmpl_path):
        os.remove(tmpl_path)
    db.session.delete(tmpl)
    db.session.commit()
    return jsonify({'deleted': tmpl_id})


@bp.route('/templates/<int:tmpl_id>/fields', methods=['GET'])
def templates_fields(tmpl_id):
    """Parse dan return daftar field dari template."""
    tmpl = TemplateFile.query.get_or_404(tmpl_id)
    tmpl_path = os.path.join(current_app.config['TEMPLATES_STORE'], tmpl.filename)
    content, fields = parse_template_file(tmpl_path)
    if content is None:
        return jsonify({'error': 'File template tidak ditemukan di disk'}), 404
    return jsonify({'template': tmpl.to_dict(), 'fields': fields})


@bp.route('/templates/scan', methods=['GET'])
def templates_scan():
    """Scan signage_templates/ dan return file .html yang belum terdaftar."""
    tmpl_dir = current_app.config['TEMPLATES_STORE']
    registered = {t.filename for t in TemplateFile.query.all()}
    unregistered = []
    if os.path.exists(tmpl_dir):
        for fname in sorted(os.listdir(tmpl_dir)):
            if fname.endswith('.html') and fname not in registered:
                fpath = os.path.join(tmpl_dir, fname)
                content = read_template_file(fpath)
                fields = parse_fields(content) if content else []
                unregistered.append({'filename': fname, 'field_count': len(fields)})
    return jsonify(unregistered)


# ─── Items ────────────────────────────────────────────────────────────────────

def _item_detail(item):
    d = item.to_dict()
    d['generated_url'] = get_generated_url(item.generated_file)
    if item.type == 'media' and item.media:
        d['media'] = {
            **item.media.to_dict(),
            'url': f"/static/{item.media.path}",
        }
    if item.type == 'html' and item.template:
        d['template'] = item.template.to_dict()
    return d


@bp.route('/items', methods=['GET'])
def items_list():
    items = Item.query.order_by(Item.created_at.desc()).all()
    return jsonify([_item_detail(i) for i in items])


@bp.route('/items', methods=['POST'])
def items_create():
    data = request.get_json()
    name      = (data.get('name') or '').strip()
    item_type = data.get('type')  # 'media' | 'html'

    if not name:
        return jsonify({'error': 'name wajib diisi'}), 400
    if item_type not in ('media', 'html'):
        return jsonify({'error': 'type harus media atau html'}), 400

    item = Item(name=name, type=item_type)

    if item_type == 'media':
        media_id = data.get('media_id')
        if not media_id:
            return jsonify({'error': 'media_id wajib untuk tipe media'}), 400
        media = MediaFile.query.get(media_id)
        if not media:
            return jsonify({'error': 'Media tidak ditemukan'}), 404
        item.media_id = media_id

    elif item_type == 'html':
        template_id = data.get('template_id')
        field_data  = data.get('field_data', {})
        if not template_id:
            return jsonify({'error': 'template_id wajib untuk tipe html'}), 400
        tmpl = TemplateFile.query.get(template_id)
        if not tmpl:
            return jsonify({'error': 'Template tidak ditemukan'}), 404
        item.template_id = template_id
        item.field_data  = field_data

    db.session.add(item)
    db.session.flush()  # dapat id dulu

    # Generate file HTML jika tipe html
    if item_type == 'html':
        filename = generate_item_file(item)
        if filename:
            item.generated_file = filename

    db.session.commit()
    return jsonify(_item_detail(item)), 201


@bp.route('/items/<int:item_id>', methods=['GET'])
def items_get(item_id):
    item = Item.query.get_or_404(item_id)
    return jsonify(_item_detail(item))


@bp.route('/items/<int:item_id>', methods=['PUT'])
def items_update(item_id):
    item = Item.query.get_or_404(item_id)
    data = request.get_json()

    if 'name' in data:
        item.name = (data['name'] or '').strip() or item.name

    if item.type == 'media' and 'media_id' in data:
        media = MediaFile.query.get(data['media_id'])
        if not media:
            return jsonify({'error': 'Media tidak ditemukan'}), 404
        item.media_id = data['media_id']

    if item.type == 'html':
        if 'field_data' in data:
            item.field_data = data['field_data']
        if 'template_id' in data:
            tmpl = TemplateFile.query.get(data['template_id'])
            if not tmpl:
                return jsonify({'error': 'Template tidak ditemukan'}), 404
            item.template_id = data['template_id']
        # Regenerate
        filename = generate_item_file(item)
        if filename:
            item.generated_file = filename

    from datetime import datetime
    item.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_item_detail(item))


@bp.route('/items/<int:item_id>', methods=['DELETE'])
def items_delete(item_id):
    item = Item.query.get_or_404(item_id)
    # Cek apakah masih di playlist
    in_playlist = PlaylistItem.query.filter_by(item_id=item_id).count()
    if in_playlist > 0:
        return jsonify({'error': f'Item masih ada di {in_playlist} playlist.'}), 409
    if item.generated_file:
        delete_generated_file(item.generated_file)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'deleted': item_id})


@bp.route('/items/<int:item_id>/regenerate', methods=['POST'])
def items_regenerate(item_id):
    item = Item.query.get_or_404(item_id)
    if item.type != 'html':
        return jsonify({'error': 'Hanya item tipe html yang bisa diregenerate'}), 400
    filename = generate_item_file(item)
    if not filename:
        return jsonify({'error': 'Gagal generate file'}), 500
    item.generated_file = filename
    from datetime import datetime
    item.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_item_detail(item))


# ─── Channels ─────────────────────────────────────────────────────────────────

def _channel_detail(channel):
    return {
        **channel.to_dict(),
        'display_url': f"/display-{channel.slug}",
    }


@bp.route('/channels', methods=['GET'])
def channels_list():
    channels = Channel.query.order_by(Channel.created_at.asc()).all()
    return jsonify([_channel_detail(c) for c in channels])


@bp.route('/channels', methods=['POST'])
def channels_create():
    data = request.get_json()
    name = (data.get('name') or '').strip()
    slug = (data.get('slug') or '').strip().lower()

    if not name:
        return jsonify({'error': 'name wajib diisi'}), 400
    if not slug:
        # auto-generate slug dari name
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
    if not slug:
        return jsonify({'error': 'slug tidak valid'}), 400
    if Channel.query.filter_by(slug=slug).first():
        return jsonify({'error': f'Slug "{slug}" sudah digunakan'}), 409

    channel = Channel(name=name, slug=slug)
    db.session.add(channel)
    db.session.commit()
    return jsonify(_channel_detail(channel)), 201


@bp.route('/channels/<int:channel_id>', methods=['PUT'])
def channels_update(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    data = request.get_json()
    if 'name' in data:
        channel.name = (data['name'] or '').strip() or channel.name
    db.session.commit()
    return jsonify(_channel_detail(channel))


@bp.route('/channels/<int:channel_id>', methods=['DELETE'])
def channels_delete(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    db.session.delete(channel)
    db.session.commit()
    return jsonify({'deleted': channel_id})


# ─── Playlist ─────────────────────────────────────────────────────────────────

def _playlist_item_detail(pi):
    item = pi.item
    d = {
        'playlist_item_id': pi.id,
        'item_id': pi.item_id,
        'order': pi.order,
        'duration': pi.duration,
        'name': item.name,
        'type': item.type,
        'generated_url': get_generated_url(item.generated_file) if item.type == 'html' else None,
    }
    if item.type == 'media' and item.media:
        d['media_type'] = item.media.type
        d['src'] = f"/static/{item.media.path}"
    elif item.type == 'html' and item.generated_file:
        d['src'] = get_generated_url(item.generated_file)
    else:
        d['src'] = None
    return d


@bp.route('/channels/<int:channel_id>/playlist', methods=['GET'])
def playlist_get(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    items = PlaylistItem.query.filter_by(channel_id=channel_id)\
        .order_by(PlaylistItem.order).all()
    return jsonify({
        'channel': _channel_detail(channel),
        'items': [_playlist_item_detail(pi) for pi in items],
    })


@bp.route('/channels/by-slug/<slug>/playlist', methods=['GET'])
def playlist_get_by_slug(slug):
    """Dipakai oleh display player — akses via slug."""
    channel = Channel.query.filter_by(slug=slug).first_or_404()
    items = PlaylistItem.query.filter_by(channel_id=channel.id)\
        .order_by(PlaylistItem.order).all()
    return jsonify({
        'channel': _channel_detail(channel),
        'items': [_playlist_item_detail(pi) for pi in items],
    })


@bp.route('/channels/<int:channel_id>/playlist', methods=['PUT'])
def playlist_reorder(channel_id):
    """Terima array [{playlist_item_id, order, duration}] — update semuanya."""
    Channel.query.get_or_404(channel_id)
    data = request.get_json()
    entries = data if isinstance(data, list) else data.get('items', [])

    for entry in entries:
        pi = PlaylistItem.query.get(entry['playlist_item_id'])
        if pi and pi.channel_id == channel_id:
            pi.order    = entry.get('order', pi.order)
            pi.duration = entry.get('duration', pi.duration)

    db.session.commit()
    items = PlaylistItem.query.filter_by(channel_id=channel_id)\
        .order_by(PlaylistItem.order).all()
    return jsonify([_playlist_item_detail(pi) for pi in items])


@bp.route('/channels/<int:channel_id>/playlist', methods=['POST'])
def playlist_add(channel_id):
    """Tambah item ke playlist."""
    Channel.query.get_or_404(channel_id)
    data = request.get_json()
    item_id  = data.get('item_id')
    duration = data.get('duration', 10)

    if not item_id:
        return jsonify({'error': 'item_id wajib diisi'}), 400

    item = Item.query.get(item_id)
    if not item:
        return jsonify({'error': 'Item tidak ditemukan'}), 404

    # Urutan: taruh di akhir
    last = PlaylistItem.query.filter_by(channel_id=channel_id)\
        .order_by(PlaylistItem.order.desc()).first()
    next_order = (last.order + 1) if last else 0

    # Video: duration None = auto (ikut durasi video)
    if item.type == 'media' and item.media and item.media.type == 'video':
        duration = None

    pi = PlaylistItem(
        channel_id=channel_id,
        item_id=item_id,
        order=next_order,
        duration=duration,
    )
    db.session.add(pi)
    db.session.commit()
    return jsonify(_playlist_item_detail(pi)), 201


@bp.route('/channels/<int:channel_id>/playlist/<int:pi_id>', methods=['DELETE'])
def playlist_remove(channel_id, pi_id):
    pi = PlaylistItem.query.filter_by(id=pi_id, channel_id=channel_id).first_or_404()
    db.session.delete(pi)
    db.session.commit()
    return jsonify({'deleted': pi_id})
