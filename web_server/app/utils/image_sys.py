import os
import base64

#list of extensions of imgs the user can upload
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif']
#absolute path to where the uploaded images should be saved
UPLOADS_FOLDER = os.path.abspath('app/uploads/images/')

#function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#takes the base64 data and filename as parameters and saves the decoded image data to the file system.
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
        # with statement, the file is automatically closed when the block of code inside the with statement is exited. This ensures that the file is properly closed and resources are released.
        # 'wb' mode indicates that the file should be opened for writing in binary mode
        # f.write --> writes the image_data to the file using the write method of the file object f
        with open(save_path, 'wb') as f:
            f.write(image_data)
            
        return True
    except Exception as e:
        print(str(e))
        return False