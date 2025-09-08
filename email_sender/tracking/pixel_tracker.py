import base64

class PixelTracker:


     def generate_tracking_pixel(self, email):
        """Generate tracking pixel for email opens"""
        tracking_url = self.config.get("tracking_url", "https://example.com/track")
        email_hash = base64.b64encode(email.encode()).decode().replace('=', '')
        return f'<img src="{tracking_url}/open?id={email_hash}" width="1" height="1" style="display:none;" />'