from flask import Flask, send_from_directory

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object('app.config.Config')
    
    
    # Serve static files from the public directory
    @app.route('/public/<path:filename>')
    def serve_public_file(filename):
        return send_from_directory(app.config['PUBLIC_FOLDER'], filename)

    # Import and register the main blueprint
    from .routes import main_blueprint
    app.register_blueprint(main_blueprint)
    
    return app
