import os
import base64

#list of extensions of imgs the user can upload
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg', 'gif', 'JPG', 'PNG', 'JPEG', 'GIF']
#absolute path to where the uploaded images should be saved
UPLOADS_FOLDER = os.path.abspath('app/uploads/images/')

#function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_base64_image(data, filename):
    try:
        # Decode the base64 data
        image_data = base64.b64decode(data)
        
        # Generate the full file path by appending the UPLOADS_FOLDER and filename together
        save_path = os.path.join(UPLOADS_FOLDER, filename)

        # Save the decoded image data to the file system
        with open(save_path, 'wb') as f:
            f.write(image_data)
        
        return True
    except Exception as e:
        print(str(e))
        return False