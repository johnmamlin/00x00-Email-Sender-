# CRITICAL FIXES for your placeholder_processor.py:

import base64
import uuid
import random
import datetime
import re
import os
from email.utils import formatdate


class PlaceholderProcessor:
    def __init__(self, config=None):
        self.config = config or {}


    def load_dictionary(self):
        return ['hello', 'world', 'email', 'message', 'update', 'system', 'notification']
    
    def generate_fake_statistics(self):
        return {
            'users_joined_today': random.randint(50, 500),
            'active_users': random.randint(1000, 10000),
            'success_rate': random.randint(85, 99),
            'satisfaction_score': random.randint(4, 5)
        }
    
    def generate_random_ip(self):
        return f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
    
    def generate_tracking_pixel(self, email):
        return f'<img src="https://example.com/pixel.gif?email={base64.b64encode(email.encode()).decode()}" width="1" height="1">'
    
    def load_image_from_directory(self, directory, filename=None):
        return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
    
    def get_domain_logo(self, domain):
        return f'<img src="https://logo.clearbit.com/{domain}.com" alt="{domain}" style="height:50px;">'
    
    def generate_random_numbers(self, length):
        if length == 'unlimited':
            length = random.randint(5, 15)
        return ''.join([str(random.randint(0, 9)) for _ in range(int(length))])
    
    def generate_random_text(self, length):
        if length == 'unlimited':
            length = random.randint(5, 15)
        letters = 'abcdefghijklmnopqrstuvwxyz'
        return ''.join(random.choice(letters) for _ in range(int(length)))

 
    def process_placeholders(self, content, to_email):
        dictionary_words = self.load_dictionary()
        username = to_email.split('@')[0] if '@' in to_email else to_email
        domain_parts = to_email.split('@')[1] if '@' in to_email else ""
        domain_name = domain_parts.split('.')[0] if '.' in domain_parts else domain_parts

        now = datetime.datetime.now()
        stats = self.generate_fake_statistics()

        replacements = {
            '##EMAIL##': to_email,
            '##BASE64EMAIL##': base64.b64encode(to_email.encode()).decode(),
            '##USERNAME##': username,
            '##USERNAME1##': username.capitalize(),
            '##DOMAIN0##': domain_name.capitalize(),
            '##DOMAIN1##': domain_name.upper(),
            '##DOMAIN2##': domain_parts,
            '##DATE##': now.strftime('%A, %B %d, %Y'),
            '##DATE1##': now.strftime('%d/%m/%Y'),
            '##DATE2##': now.strftime('%A'),
            '##DATE3##': now.strftime('%B'),
            '##DATE4##': str(now.year),
            '##TIME##': now.strftime('%H:%M:%S'),
            '##RANDOMIP##': self.generate_random_ip(),
            '##TIMESTAMP##': formatdate(localtime=True),
            '##TENANT-ID##': str(uuid.uuid4()),
            '##RANDOM-ID##': str(uuid.uuid4()),
            '##RANDOM-DIAG##': f"diag-{random.randint(100000, 999999)}-{random.randint(1000, 9999)}",
            '##USERS-TODAY##': str(stats['users_joined_today']),
            '##ACTIVE-USERS##': str(stats['active_users']),
            '##SUCCESS-RATE##': f"{stats['success_rate']}%",
            '##SATISFACTION##': str(stats['satisfaction_score']),
            '##TRACKING-PIXEL##': self.generate_tracking_pixel(to_email),
            '##UNSUBSCRIBE-LINK##': f"https://example.com/unsubscribe?email={base64.b64encode(to_email.encode()).decode()}",
            '##LOGIN-LINK##': f"https://example.com/login?ref={base64.b64encode(to_email.encode()).decode()}",
            '##VERIFY-LINK##': f"https://example.com/verify?token={uuid.uuid4()}",
            '##URGENCY-TIMER##': f"{random.randint(1, 24)} hours remaining",
            '##FAKE-VIEWS##': str(random.randint(1000, 50000)),
            '##FAKE-DOWNLOADS##': str(random.randint(500, 10000)),
            '##COUPON-CODE##': f"SAVE{random.randint(10, 50)}",
            '##BROWSER-INFO##': random.choice(['Chrome', 'Firefox', 'Safari', 'Edge']),
            '##OS-INFO##': random.choice(['Windows 10', 'macOS', 'Linux', 'iOS', 'Android']),
            '##LOCATION##': random.choice(['New York', 'London', 'Tokyo', 'Sydney', 'Toronto']),
        }
        
     
        if len(dictionary_words) >= 3:
            random_subject = ' '.join(random.sample(dictionary_words, 3)).title()
            replacements['##RANDSUBJECT##'] = random_subject

        if dictionary_words:
            random_from_name = random.choice(dictionary_words).title()
            replacements['##RANDFROMNAME##'] = random_from_name

        images_dir = "images"
        pix_image = self.load_image_from_directory(images_dir)
        if pix_image:
            clickable_url = self.config.get("Image_Clickable_URL", "")
            if clickable_url:
                replacements['##PIX##'] = f'<a href="{clickable_url}"><img src="{pix_image}" style="max-width: 100%; height: auto;"></a>'
            else:
                replacements['##PIX##'] = f'<img src="{pix_image}" style="max-width: 100%; height: auto;">'

        for i in range(1, 10):
            img_data = self.load_image_from_directory(images_dir, f"image{i}")
            if img_data:
                clickable_url = self.config.get("Image_Clickable_URL", "")
                if clickable_url:
                    replacements[f'##PIX{i}##'] = f'<a href="{clickable_url}"><img src="{img_data}" style="max-width: 100%; height: auto;"></a>'
                else:
                    replacements[f'##PIX{i}##'] = f'<img src="{img_data}" style="max-width: 100%; height: auto;">'

        domain_logo = self.get_domain_logo(domain_name)
        replacements['##DOMAINLOGO##'] = domain_logo


        for placeholder, value in replacements.items():
            content = content.replace(placeholder, str(value))

        content = self.process_advanced_patterns(content)


        ran_num_pattern = r'##RAN-NUM\[?(\d+|unlimited)\]?##'
        content = re.sub(ran_num_pattern, lambda m: self.generate_random_numbers(m.group(1)), content)
        
        ran_txt_pattern = r'##RAN-TXT\[?(\d+|unlimited)\]?##'
        content = re.sub(ran_txt_pattern, lambda m: self.generate_random_text(m.group(1)), content)

        return content

    def process_advanced_patterns(self, content):
        countdown_pattern = r'##COUNTDOWN\[(\d+)\]##'
        matches = re.finditer(countdown_pattern, content)
        for match in matches:
            full_match = match.group(0)
            hours = int(match.group(1))
            future_time = datetime.datetime.now() + datetime.timedelta(hours=hours)
            countdown_html = f'''
            <div style="background: #ff4444; color: white; padding: 10px; text-align: center; border-radius: 5px;">
                ⏰ Offer expires: {future_time.strftime('%B %d, %Y at %I:%M %p')}
            </div>
            '''
            content = content.replace(full_match, countdown_html)
        return content