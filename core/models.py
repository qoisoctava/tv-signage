from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class MediaFile(db.Model):
    __tablename__ = 'media_files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)        # nama display
    filename = db.Column(db.String(255), nullable=False)    # nama file di disk
    type = db.Column(db.String(10), nullable=False)         # 'image' atau 'video'
    path = db.Column(db.String(512), nullable=False)        # path relatif dari static/
    size = db.Column(db.Integer, default=0)                 # bytes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relasi
    items = db.relationship('Item', backref='media', lazy=True,
                            foreign_keys='Item.media_id')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'filename': self.filename,
            'type': self.type,
            'path': self.path,
            'size': self.size,
            'created_at': self.created_at.isoformat(),
        }


class TemplateFile(db.Model):
    __tablename__ = 'template_files'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)        # nama display
    filename = db.Column(db.String(255), nullable=False)    # nama file di signage_templates/
    description = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relasi
    items = db.relationship('Item', backref='template', lazy=True,
                            foreign_keys='Item.template_id')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'filename': self.filename,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
        }


class Item(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(10), nullable=False)         # 'media' atau 'html'
    media_id = db.Column(db.Integer, db.ForeignKey('media_files.id'), nullable=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template_files.id'), nullable=True)
    field_data = db.Column(db.JSON, default=dict)           # hasil isian form
    generated_file = db.Column(db.String(512), nullable=True)  # path file generated
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relasi
    playlist_items = db.relationship('PlaylistItem', backref='item', lazy=True,
                                     cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'media_id': self.media_id,
            'template_id': self.template_id,
            'field_data': self.field_data,
            'generated_file': self.generated_file,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class Channel(db.Model):
    __tablename__ = 'channels'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)  # untuk /display-{slug}
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relasi
    playlist_items = db.relationship('PlaylistItem', backref='channel', lazy=True,
                                     cascade='all, delete-orphan',
                                     order_by='PlaylistItem.order')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'created_at': self.created_at.isoformat(),
            'item_count': len(self.playlist_items),
        }


class PlaylistItem(db.Model):
    __tablename__ = 'playlist_items'

    id = db.Column(db.Integer, primary_key=True)
    channel_id = db.Column(db.Integer, db.ForeignKey('channels.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)
    duration = db.Column(db.Integer, default=10)    # detik, None = auto (video)

    def to_dict(self):
        return {
            'id': self.id,
            'channel_id': self.channel_id,
            'item_id': self.item_id,
            'order': self.order,
            'duration': self.duration,
        }
