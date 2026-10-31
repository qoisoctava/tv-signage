import os
from flask import Flask
from config import Config
from core.models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Init DB
    db.init_app(app)

    # Pastikan semua direktori penting ada
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['TEMPLATES_STORE'], exist_ok=True)
    os.makedirs(app.config['GENERATED_ITEMS'], exist_ok=True)

    # Register blueprints
    from routes.dashboard import bp as dashboard_bp
    from routes.display import bp as display_bp
    from routes.api import bp as api_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(display_bp)
    app.register_blueprint(api_bp)

    # Serve file statis generated_items/
    from flask import send_from_directory

    @app.route('/generated/<path:filename>')
    def serve_generated(filename):
        return send_from_directory(app.config['GENERATED_ITEMS'], filename)

    # Error handlers
    from flask import render_template as rt, jsonify, request

    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Not found'}), 404
        return rt('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return rt('errors/404.html'), 500

    # Buat tabel DB jika belum ada
    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5500, debug=True)
