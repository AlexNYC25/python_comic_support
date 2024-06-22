import os
import shutil
import tempfile
from PIL import Image
from concurrent.futures import ThreadPoolExecutor
from pyunpack import Archive
from flask import current_app

# Initialize a global executor for concurrent tasks
executor = ThreadPoolExecutor(max_workers=4)

def process_comic_book_file(input_path, output_dir, convert_extension='cbz', convert_image_file_type='webp', compress=False, compress_rate=80, comicinfo=False):
    try:
        def allowed_file(filename):
            return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'cbz', 'cbr', 'cb7'}

        def create_temp_directory(directory):
            try:
                return tempfile.mkdtemp(dir=directory)
            except Exception as e:
                current_app.logger.error(f"Failed to create temporary directory: {e}")
                raise

        def convert_image_to_webp(image_path, compress_quality=100):
            try:
                with Image.open(image_path) as image:
                    size_of_original = os.path.getsize(image_path)
                    if image.width > 3500 or image.height > 3500:
                        image = image.resize((int(image.width / 2), int(image.height / 2)), Image.LANCZOS)

                    webp_path = image_path.replace(image_path.split('.')[-1], 'webp')
                    image = image.convert("RGB")
                    image.save(webp_path, 'webp', quality=compress_quality, optimize=True, lossless=False)

                    size_of_webp = os.path.getsize(webp_path)
                    if size_of_webp < size_of_original:
                        os.remove(image_path)
                    else:
                        os.remove(webp_path)
            except Exception as e:
                current_app.logger.error(f"Failed to convert image to webp {image_path}: {e}")
                return False

        def traverse_directory_for_image_webp_conversion(directory, compress, compress_rate):
            futures = []
            try:
                for root, _, files in os.walk(directory):
                    for file in files:
                        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')) and not file[0] == '.':
                            image_path = os.path.join(root, file)
                            future = executor.submit(convert_image_to_webp, image_path, compress_rate)
                            futures.append(future)

                for future in futures:
                    future.result()
            except Exception as e:
                current_app.logger.error(f"Error while converting images to webp in directory {directory}: {e}")
                raise

        def compress_directory_to_comic_book_file_cbz(directory, output):
            try:
                shutil.make_archive(output.rstrip('.cbz'), 'zip', directory)
                os.rename(f"{output.rstrip('.cbz')}.zip", output)  # Rename .zip to .cbz
                return True
            except Exception as e:
                current_app.logger.error(f"Failed to compress directory to CBZ {directory}: {e}")
                return False

        def compress_directory_to_comic_book_file_cbr(directory, output):
            try:
                shutil.make_archive(output.rstrip('.cbr'), 'gztar', directory)
                os.rename(f"{output.rstrip('.cbr')}.tar.gz", output)  # Rename .tar.gz to .cbr
                return True
            except Exception as e:
                current_app.logger.error(f"Failed to compress directory to CBR {directory}: {e}")
                return False

        def compress_directory_to_comic_book_file_cb7(directory, output):
            try:
                shutil.make_archive(output.rstrip('.cb7'), 'gztar', directory)
                os.rename(f"{output.rstrip('.cb7')}.tar.gz", output)  # Rename .tar.gz to .cb7
                return True
            except Exception as e:
                current_app.logger.error(f"Failed to compress directory to CB7 {directory}: {e}")
                return False

        def delete_directory(directory):
            try:
                shutil.rmtree(directory)
                return True
            except Exception as e:
                current_app.logger.error(f"Failed to delete directory {directory}: {e}")
                return False

        # Validate file type
        if not allowed_file(input_path):
            current_app.logger.error(f"Unsupported file type for {input_path}")
            return False

        # Create a temporary working directory
        temp_work_dir = create_temp_directory(output_dir)

        try:
            # Decompress the file using pyunpack
            try:
                Archive(input_path).extractall(temp_work_dir)
                current_app.logger.info(f"Decompressed {input_path} to {temp_work_dir}")
            except Exception as e:
                current_app.logger.error(f"Failed to decompress file {input_path}: {e}")
                return False

            if convert_image_file_type == 'webp':
                traverse_directory_for_image_webp_conversion(temp_work_dir, compress, compress_rate)

            # Determine the public directory and file name
            public_dir = current_app.config['PUBLIC_FOLDER']
            os.makedirs(public_dir, exist_ok=True)
            output_file_name = os.path.basename(input_path).replace(input_path.split('.')[-1], convert_extension)
            output_file_path = os.path.join(public_dir, output_file_name)

            if convert_extension == 'cbz':
                if not compress_directory_to_comic_book_file_cbz(temp_work_dir, output_file_path):
                    return False
            elif convert_extension == 'cbr':
                if not compress_directory_to_comic_book_file_cbr(temp_work_dir, output_file_path):
                    return False
            elif convert_extension == 'cb7':
                if not compress_directory_to_comic_book_file_cb7(temp_work_dir, output_file_path):
                    return False
            else:
                current_app.logger.error(f"Unsupported conversion extension type {convert_extension}")
                return False

            delete_directory(temp_work_dir)

            # Construct the public URL for the file
            public_url = os.path.join(current_app.config['PUBLIC_URL'], output_file_name)
            return public_url

        except Exception as e:
            current_app.logger.error(f"Error during file processing: {e}")
            # Clean up the temporary directory in case of error
            delete_directory(temp_work_dir)
            raise

    except Exception as e:
        current_app.logger.error(f"General error in process_comic_book_file: {e}")
        return False
