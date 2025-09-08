import smtplib
import time
import random
import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.image import MIMEImage
from email.utils import formatdate, make_msgid
import re

def create_email(to_email, template_content, attachments=None):
    """Standalone function to create email"""
    msg = MIMEMultipart('related')
    msg['Message-ID'] = make_msgid(domain="sender.local")
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = "Default Subject"
    msg['From'] = "Sender <sender@example.com>"
    msg['To'] = to_email
    msg['X-Priority'] = '1'
    msg['X-MSMail-Priority'] = 'High'
    msg['Importance'] = 'High'
    
    # Replace email placeholder
    template_content = template_content.replace("##EMAIL##", to_email)
    
    # Handle SVG content
    svg_matches = re.findall(r'<svg[^>]*>[\s\S]*?</svg>', template_content)
    for i, svg in enumerate(svg_matches):
        svg_id = f"svg_{i}"
        template_content = template_content.replace(svg, f'<img src="cid:{svg_id}" />')
        
        svg_data = svg.encode('utf-8')
        svg_img = MIMEImage(svg_data, 'svg+xml')
        svg_img.add_header('Content-ID', f'<{svg_id}>')
        svg_img.add_header('Content-Disposition', 'inline')
        msg.attach(svg_img)
    
    # Create the main HTML part
    html_part = MIMEText(template_content, 'html', 'utf-8')
    msg.attach(html_part)
    
    # Handle attachments
    if attachments:
        for attachment_name, attachment_data in attachments:
            special_formats = ['.js', '.xml', '.html', '.svg', '.xhtml', '.shtml', '.htm']
            is_special_format = any(ext in attachment_name.lower() for ext in special_formats)
            
            if is_special_format:
                base64_data = base64.b64encode(attachment_data).decode('utf-8')
                processed_data = f"##Base64Email##{base64_data}".encode('utf-8')
            else:
                processed_data = attachment_data
                
            part = MIMEApplication(processed_data)
            part.add_header('Content-Disposition', 'attachment', filename=attachment_name)
            msg.attach(part)
    
    return msg