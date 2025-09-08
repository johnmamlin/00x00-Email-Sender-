import qrcode
import io
import base64
from core.placeholder_processor import process_placeholders


class QRCodeGenerator:
    
    def generate_qr_code(self, email, size=200):
        """Generate a QR code for the recipient's email"""
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )

        qr_url = self.config.get("qr_url", f"https://example.com/track?email={email}")
        qr_url = self.process_placeholders(qr_url, email)

        qr.add_data(qr_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()
    


        

        qr.add_data(f"mailto:{email}")
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        return img_byte_arr