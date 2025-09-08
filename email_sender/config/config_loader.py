import os

def load_config(config_file="config.ini"):
    """Load configuration from ini file"""
    config = {}
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            for line in f:
                if "=" in line and not line.strip().startswith("#"):
                    key, value = line.strip().split("=", 1)
                    config[key.strip()] = value.strip()
    return config

def create_advanced_config():
    """Create advanced configuration file"""
    config_content = """# Advanced Email Sender Configuration
    
from_email=sender@example.com
from_names=Marketing Team|Customer Support|Sales Department|Business Development
subjects=Important Update|Action Required|Time Sensitive|Your Account Status|Exclusive Offer
reply_to=noreply@example.com
use_encoding=False
encrypt_attachments=False
emails_per_smtp=10
delay_min=2.0
delay_max=5.0
convert_to_pdf=False
use_random_template=True

# Advanced Features
qr_url=https://example.com/track?email=##EMAIL##&id=##RANDOM-ID##
tracking_url=https://example.com/analytics
smtp_health_check=True
use_text_version=True
advanced_headers=True

# Anti-Spam Settings
rotate_message_id=True
randomize_send_times=True
use_realistic_delays=True
"""
    if not os.path.exists("config.ini"):
        with open("config.ini", "w") as f:
            f.write(config_content)
        print("[*] Created advanced config.ini file")
    
    if not os.path.exists("smtp.txt"):
        with open("smtp.txt", "w") as f:
            f.write("""# SMTP Server Configuration
# Format: server|port|username|password
# Example:
smtp.example.com|587|user@example.com|yourpassword
smtp2.example.com|587|user2@example.com|yourpassword2
""")
        print("[*] Created sample smtp.txt file. Please update with your SMTP servers.")