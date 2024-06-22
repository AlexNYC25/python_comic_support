from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from app.comic_processor import process_comic_book_file

# Define the blueprint
main_blueprint = Blueprint('main', __name__)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'cbz', 'cbr', 'cb7'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Register routes function
def register_routes(blueprint):
    # Example route
    @blueprint.route('/api/hello', methods=['GET'], endpoint='hello_v1')
    def hello():
        return jsonify(message="Hello from the single API route!")

    # Route to handle file upload and processing
    @blueprint.route('/api/comic-compress-upload', methods=['POST'], endpoint='comic_compress_upload_v1')
    def comic_compress_upload():
        try:
            if 'file' not in request.files:
                return jsonify(error="No file part"), 400

            file = request.files['file']

            if file.filename == '':
                return jsonify(error="No selected file"), 400

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'uploads')
                os.makedirs(upload_folder, exist_ok=True)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)

                # Extract optional parameters from request
                convert_extension = request.form.get('convert_extension', 'cbz')  # Default to 'cbz'
                convert_image_file_type = request.form.get('convert_image_file_type', 'webp')  # Default to 'webp'
                compress = request.form.get('compress', 'false').lower() == 'true'  # Default to False
                compress_rate = int(request.form.get('compress_rate', 80))  # Default to 80
                comicinfo = request.form.get('comicinfo', 'false').lower() == 'true'  # Default to False

                # Process the comic book file
                public_url = process_comic_book_file(
                    input_path=file_path,
                    output_dir=upload_folder,  # We process and save in the same base directory
                    convert_extension=convert_extension,
                    convert_image_file_type=convert_image_file_type,
                    compress=compress,
                    compress_rate=compress_rate,
                    comicinfo=comicinfo
                )

                if public_url:
                    # Construct full public URL using request.host_url to ensure correct scheme and port
                    full_public_url = request.host_url + public_url.lstrip('/')
                    return jsonify(message="File processed successfully", file_url=full_public_url), 200
                else:
                    return jsonify(error="Failed to process file", pub=public_url), 500

            return jsonify(error="File type not allowed"), 400

        except Exception as e:
            current_app.logger.error(f"Error processing file: {e}")
            return jsonify(error=str(e)), 500
