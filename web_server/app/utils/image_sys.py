"""
image_sys.py - Module for image-related utility functions.

This module provides functions for handling image files, including checking allowed file extensions,
saving base64-encoded images to the file system, and converting image files to base64 for retrieval.

Functions:
- allowed_file(filename): Check if the file extension is allowed.
- save_base64_image(file, filename): Save the decoded base64 image data to the file system.
- file_to_base64(file_path): Convert an image file to base64-encoded content for retrieval.

Constants:
- ALLOWED_EXTENSIONS: List of allowed image file extensions.
- UPLOADS_FOLDER: Absolute path to where uploaded images should be saved.
"""
import os
import base64

#list of extensions of imgs the user can upload
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
#absolute path to where the uploaded images should be saved
UPLOADS_FOLDER = os.path.abspath('app/uploads/images/')

#function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#takes the base64 data and filename as parameters and saves the decoded image to the file system.
def save_base64_image(file, filename):
    try:
        # Decode the base64 data
        image_data = base64.b64decode(file)

        # Split the filename and extension
        filename, extension = os.path.splitext(filename)
        # Lowercase the extension
        extension = extension.lower()
        # Generates the full file path by appending the UPLOADS_FOLDER and filename together,
        # ensuring that the correct path is formed regardless of the operating system using (/ or \)
        save_path = os.path.join(UPLOADS_FOLDER, f'{filename}{extension}')
        # Save the decoded image data to the file system
        # with statement, the file is automatically closed when the block of code inside the with statement is exited. 
        # This ensures that the file is properly closed and resources are released.
        # 'wb' mode indicates that the file should be opened for writing in binary mode
        # f.write --> writes the image_data to the file using the write method of the file object f
        with open(save_path, 'wb') as f:
            f.write(image_data)
        return True
    except Exception as e:
        print(str(e))
        return False

# takes a file path as input and returns the base64-encoded content of the file (for get api)
def file_to_base64(file_path):
    try:
        # open function is used to open the file specified by file_path in binary mode ('rb')
        # with statement, ensures that the file is properly closed after reading its content.
        with open(file_path, 'rb') as file:
            # Read the file content & result is stored in the file_content variable
            file_content = file.read()
            # split the file path into the file's base name and extension.
            _, file_extension = os.path.splitext(file_path)
            # extension is extracted and stored in the file_extension variable
            # remove the leading dot (.) using slicing (file_extension[1:])
            file_extension = file_extension[1:]

            # Encode the file content to base64
            base64_encoded = base64.b64encode(file_content).decode('utf-8')

            # returns the base64_encoded string representing the file content
            prefix = f"data:image/{file_extension.lower()};base64,"
            return prefix + base64_encoded

    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None
