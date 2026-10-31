from flask import Blueprint, render_template
from core.models import Channel

bp = Blueprint('display', __name__)

@bp.route('/display-<slug>')
def show(slug):
    channel = Channel.query.filter_by(slug=slug).first()
    if not channel:
        return render_template('display/404.html', slug=f'/display-{slug}'), 404
    return render_template('display/index.html', channel=channel)
