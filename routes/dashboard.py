from flask import Blueprint, render_template
from core.models import Channel

bp = Blueprint('dashboard', __name__)

@bp.route('/')
@bp.route('/dashboard')
def index():
    return render_template('dashboard/index.html')

@bp.route('/dashboard/media')
def media():
    return render_template('dashboard/media.html',
        breadcrumb=[{'label': 'Media', 'url': '/dashboard/media'}])

@bp.route('/dashboard/templates')
def templates():
    return render_template('dashboard/templates.html',
        breadcrumb=[{'label': 'Templates', 'url': '/dashboard/templates'}])

@bp.route('/dashboard/items')
def items():
    return render_template('dashboard/items.html',
        breadcrumb=[{'label': 'Items', 'url': '/dashboard/items'}])

@bp.route('/dashboard/channels')
def channels():
    return render_template('dashboard/channels.html',
        breadcrumb=[{'label': 'Channels', 'url': '/dashboard/channels'}])

@bp.route('/dashboard/channels/<int:channel_id>/playlist')
def playlist(channel_id):
    channel = Channel.query.get_or_404(channel_id)
    return render_template('dashboard/playlist.html',
        channel_id=channel_id,
        breadcrumb=[
            {'label': 'Channels', 'url': '/dashboard/channels'},
            {'label': channel.name, 'url': f'/dashboard/channels/{channel_id}/playlist'},
        ])
