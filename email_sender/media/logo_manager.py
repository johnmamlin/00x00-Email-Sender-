import os
import base64



class LogoManager:
     
    def get_domain_logo(self, domain):
        logos_dir = "logos"
        if os.path.exists(logos_dir):
            logo_path = os.path.join(logos_dir, f"{domain}.png")
            if os.path.exists(logo_path):
                try:
                    with open(logo_path,"rb") as img_file:
                        img_data = base64.b64encode(img_file.read()).decode('utf-8')
                        return f"data:image/png;base64, {img_data}"
                except:
                    pass
        return f'<div style="background: #333; color: white; padding: 10px; text-align: center; font-weight: bold;">{domain.upper()}</div>'            