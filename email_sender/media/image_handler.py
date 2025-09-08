import os
import base64
import logging


class ImageHandler:

    def load_image_from_directory(self,image_dir, image_name=None):
        if not os.path.exists(image_dir):
            return None

        image_extensions = ['.jpg', '.jpeg', '.png' ,'gif' , '.bmp'] 

        if image_name:
            base_name= os.path.splitext(image_name)[0]
            for ext in image_extensions:
                image_path = os.path.join(image_dir, base_name + ext)
                if os.path.exists(image_path):
                    try:
                        with open(image_path, "rb")as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            file_ext = ext[1:]

                            return f"data:image/{file_ext};base64,{img_data}"
                    except Exception as e:
                        self.logger.error(f"Error loading image {image_path}: {e}")

        else:
            for filename in os.listdir(image_dir):
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    image_path = os.path.join(image_dir, filename)
                    try:
                        with open (image_path, "rb") as img_file:
                            img_data = base64.b64encode(img_file.read()).decode('utf-8')
                            file_ext = os.path.splitext(filename)[1][1:]
                            return f"data:image/ {file_ext};base64,{img_data}"
                    except Exception as e:
                        self.logger.error(f"Error loading image {image_path}: {e}")


        return None 