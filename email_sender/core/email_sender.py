import smtplib
import time
import random
import logging
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
from networking.smtp_manager import SMTPManager
from core.email_composer import create_email
from core.template_engine import load_template_from_folder
from attachments.attachment_loader import AttachmentLoader
from config.config_loader import load_config
import os
import sys
import glob
from cryptography.fernet import Fernet


import os
import random
import time
import logging
import smtplib
import glob
from attachments.attachment_loader import AttachmentLoader
from core.email_composer import create_email

class EmailSender:
    def __init__(self, config_file="config.ini"):
      
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='email_campaign.log'
        )
        self.logger = logging.getLogger("EmailSender")
        
       
        self.smtp_servers = []  
        self.current_smtp_index = 0
        self.success_count = 0
        self.failed_count = 0
        self.convert_to_pdf = False  
        
        self.load_smtp_servers("smtp.txt")

     
        try:
            import pdfkit
            self.pdf_support = True
        except ImportError:
            self.pdf_support = False
            self.logger.warning("PDF conversion libraries not available")

    def load_smtp_servers(self, smtp_file):
        """Load SMTP servers from a configuration file"""
        smtp_servers = []
        if os.path.exists(smtp_file):
            with open(smtp_file, "r") as f:
                for line in f:
                    if line.strip() and not line.strip().startswith("#"):
                        parts = line.strip().split("|")
                        if len(parts) >= 4:
                            smtp_servers.append({
                                "server": parts[0],
                                "port": int(parts[1]),
                                "username": parts[2],
                                "password": parts[3]
                            })
        self.smtp_servers = smtp_servers        
        if smtp_servers:
            self.logger.info(f"Loaded {len(smtp_servers)} SMTP servers")
            print(f"[*] Loaded {len(smtp_servers)} SMTP servers")
        else:
            self.logger.warning("No valid SMTP servers found in file")
            

            



    def run_campaign(self, email_file, templates_dir, attachments_dir, 
                    use_random_template=False, specific_template=None):
        """Complete campaign execution method"""
        try:
          
            if not os.path.exists(email_file):
                self.logger.error(f"Email file not found: {email_file}")
                return False

     
            with open(email_file, 'r') as f:
                emails = [line.strip() for line in f if line.strip()]
            
        
            template_content = self._load_template(templates_dir, use_random_template, specific_template)
            if not template_content:
                self.logger.error("Failed to load email template")
                return False
                
         
            attachments = []
            if os.path.exists(attachments_dir):
                loader = AttachmentLoader()
                attachments = loader.load_attachments(attachments_dir, self.convert_to_pdf)
            
           
            for email in emails:
                self.send_email(email, template_content, attachments)
                time.sleep(random.uniform(1, 3))  
            return True
            
        except Exception as e:
            self.logger.error(f"Campaign failed: {str(e)}")
            return False

    def _load_template(self, templates_dir, use_random, specific_template):
        """Internal template loading logic"""
        if specific_template:
            template_path = os.path.join(templates_dir, specific_template)
        elif use_random:
            templates = glob.glob(os.path.join(templates_dir, "*.html")) + \
                       glob.glob(os.path.join(templates_dir, "*.htm"))
            template_path = random.choice(templates) if templates else None
        else:
            template_path = None  # Default behavior
            
        if template_path and os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def send_email(self, to_email, template_content, attachments=None):
        """Send an email to the recipient"""
        if not self.smtp_servers:
            print(f"\033[91m[!] No SMTP servers available\033[0m")
            self.logger.error("No SMTP servers available")
            return False
            
        smtp_info = self.get_next_smtp()
        if not smtp_info:
            return False
            
        try:
            msg = create_email(to_email, template_content, attachments)
            
            with smtplib.SMTP(smtp_info["server"], smtp_info["port"]) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_info["username"], smtp_info["password"])
                server.send_message(msg)

            print(f"\033[92m[+] Email sent successfully to: {to_email}\033[0m")
            self.logger.info(f"Email sent successfully to: {to_email}")
            self.success_count += 1
            return True
        except Exception as e:
            print(f"\033[91m[!] Failed to send email to {to_email}: {str(e)}\033[0m")
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            self.failed_count += 1
            return False

    def get_next_smtp(self):
        """Get next available SMTP server"""
        if not self.smtp_servers:
            return None
            
        smtp = self.smtp_servers[self.current_smtp_index]
        self.current_smtp_index = (self.current_smtp_index + 1) % len(self.smtp_servers)
        return smtp