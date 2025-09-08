from core.email_sender import EmailSender
from storage.directory_creator import create_required_directories
from config.config_loader import create_advanced_config
import os
import glob
import random
import time
import sys
import re
import datetime
from datetime import datetime, timedelta
from colorama import Fore, Style, Back, init
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid  
from security.troubleshoot import EmailTroubleshooter
from core.placeholder_processor import PlaceholderProcessor
from campaign.schedule_manager import IntelligentScheduler, ThrottleManager
from campaign.analyticsmonitoring import DeliveryabilityMonitor, RealTimeAlerts
from campaign.contentbestpractices import ContentBestPractices
from campaign.automatedlisthygiene import EmailValidator, ListCleaner
from campaign.robustauthentication import EmailAuthenticator, AuthenticationManager




def print_banner():
    """Print the 00x00 banner"""
    print("*" * 80)
    print("*" + " " * 78 + "*")
    print("*{:^78}*".format("00x00 ADVANCED EMAIL SENDER"))
    print("*{:^78}*".format("[keem_backup V1.0.0] Beta"))
    print("*" + " " * 78 + "*")
    print("*" + " " * 78 + "*")
    print("*{:^78}*".format("Author TG: @keem_backup"))
    print("*{:^78}*".format("Purchase BOT: @okeem_backup"))
    print("*{:^78}*".format("Support TG: https://t.me/keem_backup"))
    print("*" + " " * 78 + "*")
    print("*{:^78}*".format("USER LCNS: B93E5436-B6A0-4602-AA3F-7B3870998F12"))
    print("*{:^78}*".format("Happy Mailing!"))
    print("*" * 80)



def real_countdown(seconds=3.8):
    """Real countdown timer that counts down from seconds to 0 in tenths"""
    print(f"\n{Fore.YELLOW}[⏱️] Starting countdown: {seconds} seconds{Style.RESET_ALL}")

    total_tenths = int(round(seconds * 10))
    
    for tenths in range(total_tenths, -1, -1):
      
        if tenths > 0:
            whole = tenths // 10
            fractional = tenths % 10
            display = f"{whole}.{fractional}"
        else:
            display = "0"
        
        
        print(f"\r{Fore.CYAN}[⏳] {display}...{Style.RESET_ALL}", end='', flush=True)
        
 
        if tenths > 0:
            time.sleep(0.1)
    

    print(f"\n{Fore.GREEN}[✓] 0 - Ready! Sending email now...{Style.RESET_ALL}")

def process_countdown_placeholders(content):
    """Process countdown placeholders in email content"""
    countdown_pattern = r'##COUNTDOWN\[(\d+)\]##'
    matches = re.finditer(countdown_pattern, content)
    for match in matches:
        full_match = match.group(0)
        hours = int(match.group(1))
        future_time = datetime.now() + timedelta(hours=hours)
        countdown_html = f'''⏰ Offer expires: {future_time.strftime('%B %d, %Y at %I:%M %p')}'''
        content = content.replace(full_match, countdown_html)
    return content

class EmailSender:
    def __init__(self):
        self.convert_to_pdf = False
        self.smtp_servers = []
        self.smtp_configs = [] 
        self.sent_count = 0
        self.failed_count = 0
        self.enable_countdown = False
        self.countdown_time = 3.8
        self.current_smtp_index = 0  
        self.troubleshooter = EmailTroubleshooter()  
        self.processor = PlaceholderProcessor()
        self.scheduler = IntelligentScheduler()
        self.throttle_manager = ThrottleManager()
        self.monitor = DeliveryabilityMonitor()
        self.monitor.record_delivery_attempt = lambda *args, **kwargs: None 
        self.alerts = RealTimeAlerts(self.monitor)
        self.content_optimizer = ContentBestPractices()
        self.email_validator = EmailValidator()
        self.authenticator = EmailAuthenticator()
        self.dkim_signer = AuthenticationManager()
        self.dkim_signer = AuthenticationManager()

    def load_smtp_servers(self):
        """Load and parse SMTP servers from smtp.txt"""
        self.smtp_configs = []
        if os.path.exists("smtp.txt"):
            with open("smtp.txt", "r") as f:
                lines = f.readlines()
                for line_num, line in enumerate(lines, 1):
                    line = line.strip()
                    if line and not line.startswith("#"):
                        self.smtp_servers.append(line)
                      
                        if "|" in line:
                            parts = line.split("|")
                            if len(parts) >= 4:
                                try:
                                    config = {
                                    'server': parts[0],
                                    'port': int(parts[1]),
                                    'username': parts[2],
                                    'password': parts[3],
                                    'email': parts[2] 
                                    }
                                    self.smtp_configs.append(config)
                                    print(f"[DEBUG] Line {line_num}: Loaded {config['server']}:{config['port']} with user {config['username']}")
                                except ValueError as e:
                                    print(f"[ERROR] Line {line_num}: Invalid port number in '{line}' - {e}")
                            else:
                                print(f"[ERROR] Line {line_num}: Invalid format in '{line}' - Expected: server|port|username|password")
                        else:
                            print(f"[ERROR] Line {line_num}: Missing '|' separator in '{line}'")
            

        
        
        server_count = len(self.smtp_servers)
        print(f"Successfully loaded {server_count} SMTP " + Fore.MAGENTA + "server" + Style.RESET_ALL + "(s)")
       
        if server_count == 0:
            print("\n[INFO] Expected smtp.txt format:")
            print("smtp.gmail.com|587|your_email@gmail.com|your_app_password")
            print("smtp.outlook.com|587|your_email@outlook.com|your_password")
            print("# Lines starting with # are ignored")
        return server_count > 0    
            
    def get_next_smtp_config(self):
        """Get the next SMTP configuration in rotation"""
        if not self.smtp_configs:
            return None
        
        config = self.smtp_configs[self.current_smtp_index]
        self.current_smtp_index = (self.current_smtp_index + 1) % len(self.smtp_configs)
        return config
        
    def authenticate_smtp_servers(self):
        """Authenticate SMTP servers"""
        print("Verifying Loaded SMTP Servers. Please Wait Ω")
        authenticated = 0
        
        for config in self.smtp_configs:
            server_host = config['server']
            server_port = config['port']
            
            print(f"Now Authenticating {server_host}." + Fore.GREEN + f"{server_port}")
            
            try:
                import socket
                socket.setdefaulttimeout(10)  

                if server_port == 465:
                    server = smtplib.SMTP_SSL(server_host, server_port)
                else:
                    server = smtplib.SMTP(server_host, server_port)
                    server.starttls()
                
                server.login(config['username'], config['password'])
                server.quit()
                
                print("✓ " + f"{server_host}." + Fore.GREEN + f"{server_port}" + Style.RESET_ALL + " SMTP Authenticated Successfully")
                authenticated += 1

            except socket.gaierror as e:
                print("✗ " + f"{server_host}:{server_port}" + Style.RESET_ALL + f" DNS Resolution Failed: Check server address")
            except smtplib.SMTPAuthenticationError as e:
                print("✗ " + f"{server_host}:{server_port}" + Style.RESET_ALL + f" Authentication Failed: Invalid credentials")        
            except smtplib.SMTPConnectError as e:
                print("✗ " + f"{server_host}:{server_port}" + Style.RESET_ALL + f" Connection Failed: {str(e)}")
            except Exception as e:
                print("✗ " + f"{server_host}." + Fore.RED + f"{server_port}" + Style.RESET_ALL + f" SMTP Authentication Failed: {str(e)}")

                
        
        print(f"Successfully verified {authenticated} SMTP " + Fore.MAGENTA + "server" + Style.RESET_ALL + "(s)")
        return authenticated > 0
        
    def load_email_list(self, email_file):
        """Load email addresses from file"""
        emails = []
        if os.path.exists(email_file):
            with open(email_file, "r") as f:
                for line in f:
                    email = line.strip()
                    if email and "@" in email:
                        emails.append(email)
        return emails
        
    def load_templates(self, templates_dir, specific_template=None):
        """Load email templates"""
        templates = []
        if specific_template:
            template_path = os.path.join(templates_dir, specific_template)
            if os.path.exists(template_path):
                templates.append(template_path)
        else:
            templates = (
                glob.glob(os.path.join(templates_dir, "*.html")) + 
                glob.glob(os.path.join(templates_dir, "*.htm")) + 
                glob.glob(os.path.join(templates_dir, "*.svg"))
            )
        return templates
        
    def process_template_content(self, template_path, recipient_email):
        """Process template content and replace placeholders"""
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            
            content = self.processor.process_placeholders(content, recipient_email)
        
            
            return content
        except Exception as e:
            print(f"Error processing template: {e}")
            return ""
    
    def create_email_message(self, from_name, sender_email, recipient, subject, html_content):
        """Create MIME email message with proper headers"""
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{from_name} <{sender_email}>"
        msg['To'] = recipient
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid()
        msg['Reply-To'] = "do-not-reply@automailer.com"
        
        msg.attach(MIMEText(html_content, 'html'))
        return msg
        
    def send_email(self, recipient, template, from_name, subject):
        """Send email with SMTP rotation and real countdown before sending"""


        if not self.email_validator.is_valid_email(recipient):
            print(f"| Status      | {Fore.RED}✗ Invalid Email Format{Style.RESET_ALL}")
            self.failed_count += 1
            return False

  


        smtp_config = self.get_next_smtp_config()
        if not smtp_config:
           print("[!] No SMTP configuration available")
           return False
 
    

        start_time = time.time()
        response_time = 0
        processed_content = self.process_template_content(template, recipient)
        content_analysis = self.content_optimizer.analyze_content_quality(processed_content, subject)

        if content_analysis["score"] > 5.0:
           print(f"| Content     | {Fore.YELLOW}⚠ High Spam Risk: {content_analysis['score']:.1f}{Style.RESET_ALL}")
           if content_analysis["score"] > 7.0:
              subject = random.choice(self.content_optimizer.professional_subjects)
              print(f"| Subject     | {Fore.CYAN}Auto-optimized to: {subject}{Style.RESET_ALL}")

        delay = self.scheduler.calculate_sending_delay(smtp_config)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sender_email = smtp_config['email']

        print("=" * 80)
        print("|" + " " * 27 + "Email Sending Details" + " " * 28 + "|")
        print("=" * 80)
        print("| Process      |" + " " * 29 + "Details" + " " * 28 + "|")
        print("=" * 80)
        print(f"| From Name    | {from_name} <{sender_email}>" +
            " " * (63 - len(f'{from_name} <{sender_email}>')) + "|")
        print(f"| SMTP Server  | {smtp_config['server']}:{smtp_config['port']}" +
            " " * (63 - len(f'{smtp_config["server"]}:{smtp_config["port"]}')) + "|")
        print(f"| From Encoding| \"Quoted-Printable\"" +
            " " * (61 - len("\"Quoted-Printable\"")) + "|")
        print(f"| To           | {recipient}" + " " * (63 - len(recipient)) + "|")
        print(f"| Subject      | {subject}" + " " * (63 - len(subject)) + "|")
        print(f"| Subj Encoding| \"Quoted-Printable\"" +
            " " * (61 - len("\"Quoted-Printable\"")) + "|")
        print(f"| Reply-To     | do-not-reply@automailer.com" +
            " " * (63 - len("do-not-reply@automailer.com")) + "|")
        print("=" * 80)


        if self.enable_countdown:
           print(f"| Countdown    | Starting {self.countdown_time}s countdown...")
           real_countdown(self.countdown_time)


        try:
            if smtp_config['port'] == 465:
                server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'])
            else:
                server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
                server.starttls()

            server.login(smtp_config['username'], smtp_config['password'])

            msg = self.create_email_message(from_name, sender_email, recipient, subject, processed_content)
            signed_msg = self.dkim_signer.sign_message(msg, smtp_config['server'])

            server.sendmail(sender_email, recipient, msg.as_string())
            server.quit()

            self.monitor.record_delivery_attempt(smtp_config, recipient, 'sent', '250', response_time)
            self.scheduler.update_sending_stats(smtp_config, True)
            self.throttle_manager.update_throttle(smtp_config['email'], True, response_time)

            print("| Status       | " + Fore.GREEN + "✓ Successfully Sent" + Style.RESET_ALL)
            self.sent_count += 1
            success = True

        except Exception as e:
            response_time = time.time() - start_time
            report = self.troubleshooter.analyze_error(e, recipient, smtp_config)

            error_code = str(e)[:3] if str(e)[:3].isdigit() else "500"
            self.monitor.record_delivery_attempt(smtp_config, recipient, 'failed', error_code, response_time)
            self.scheduler.update_sending_stats(smtp_config, False)
            self.throttle_manager.update_throttle(smtp_config['email'], False, response_time)

            error_lines = self.troubleshooter.format_error_display(report)
            for line in error_lines:
                print(f"| {line}")

            if self.troubleshooter.should_retry(report):
                retry_delay = self.troubleshooter.get_retry_delay(report)
                print(f"| Retry Info   | {Fore.CYAN}Auto-retry recommended in {retry_delay}s{Style.RESET_ALL}")

            self.failed_count += 1
            success = False

        print(f"| Timestamp    | {timestamp}")
        print(f"| Support      | {Fore.CYAN}https://t.me/keem_backup{Style.RESET_ALL}")
        print("-" * 80)

        return success   
        
    def run_campaign(self, email_file, templates_dir, attachments_dir, use_random_template=True, specific_template=None):
        """Run the email campaign with SMTP rotation - sends one email at a time"""
        

        if not self.load_smtp_servers():
            print("[!] No SMTP servers found. Please configure smtp.txt")
            return
            
        if not self.authenticate_smtp_servers():
            print("[!] No SMTP servers authenticated successfully")
            return
        
        print()
        
        emails = self.load_email_list(email_file)
        if not emails:
            print("[!] No valid email addresses found")
            return
            
        templates = self.load_templates(templates_dir, specific_template)
        if not templates:
            print("[!] No templates found")
            return

        print("STARTING SEQUENTIAL EMAIL CAMPAIGN ✓ ✓ ✓ ✓ ✓ ✓")
        print(f"SMTP SERVERS: {len(self.smtp_configs)} | MULTITHREADING: Disabled | PROXY: Disabled")
        print(f"Sequential Mode: {'Enabled' if self.enable_countdown else 'Disabled'} | Load Timer: {self.countdown_time}s")
        print(f"Sending Pattern: {self.countdown_time}s load → send email → {self.countdown_time}s load → next email")
        print(f"SMTP Rotation: {'Enabled' if len(self.smtp_configs) > 1 else 'Single SMTP'}")
        print(f"{Fore.CYAN}Support Contact: https://t.me/keem_backup{Style.RESET_ALL}")
        print()
        
  
        from_names = ["Marketing Team", "Customer Support", "Sales Department", "Business Development"]
        subjects = ["Important Update", "Action Required", "Time Sensitive", "Your Account Status", "Exclusive Offer"]
        
        total_emails = len(emails)
        print(f"{Fore.GREEN}[📊] Starting sequential campaign: {total_emails} emails to process{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[⚡] Mode: One email at a time with {self.countdown_time}s load time before each{Style.RESET_ALL}")
        
        for i, email in enumerate(emails, 1):
            print(f"\n{Fore.CYAN}{'='*60}")
            print(f"PROCESSING EMAIL #{i} OF {len(emails)}")
            print(f"{'='*60}{Style.RESET_ALL}")
            
            if i % 10 == 0:
                print(f"{Fore.BLUE}[📊] Processed {i} emails so far...{Style.RESET_ALL}")

            from_name = random.choice(from_names)
            subject = random.choice(subjects)
            template = random.choice(templates) if use_random_template else templates[0]
            
         
            next_smtp = self.smtp_configs[self.current_smtp_index] if self.smtp_configs else None
            
            print(f"{Fore.YELLOW}[📧] Target: {email}{Style.RESET_ALL}")
            print(f"[📝] Template: {os.path.basename(template) if template else 'Default'}")
            print(f"[👤] From: {from_name}")
            print(f"[📋] Subject: {subject}")
            if next_smtp:
                print(f"[🔄] SMTP: {next_smtp['server']} ({next_smtp['email']})")
            print()
            
            smtp_config = next_smtp 
            success = self.send_email(email, template, from_name, subject)
            if not success:
                
                extra_delay = self.throttle_manager.get_throttle_delay(smtp_config['email'], 1)
                print(f"{Fore.YELLOW}[⏳] Extended delay due to failure: {extra_delay}s{Style.RESET_ALL}")
                time.sleep(extra_delay)
            
            progress_percent = (i / total_emails) * 100
            success_rate = (self.sent_count/(self.sent_count+self.failed_count)*100) if (self.sent_count+self.failed_count) > 0 else 0
            print(f"{Fore.BLUE}[📈] Campaign Progress: {i}/{total_emails} ({progress_percent:.1f}%) | Success Rate: {success_rate:.1f}%{Style.RESET_ALL}")
            
            if i == total_emails:
                print(f"\n{Fore.GREEN}[🎉] FINAL EMAIL #{i} SENT! Campaign completed!{Style.RESET_ALL}")
        
     
        print(f"\n{Fore.GREEN}{'='*60}")
        print("MASS EMAIL CAMPAIGN COMPLETED")
        print(f"{'='*60}{Style.RESET_ALL}")
        print(f"📊 Campaign Statistics:")
        print(f"   • Total Processed: {self.sent_count + self.failed_count}")
        print(f"   • Successfully Sent: {Fore.GREEN}{self.sent_count}{Style.RESET_ALL}")
        print(f"   • Failed: {Fore.RED}{self.failed_count}{Style.RESET_ALL}")
        success_rate = (self.sent_count/(self.sent_count+self.failed_count)*100) if (self.sent_count+self.failed_count) > 0 else 0
        print(f"   • Success Rate: {Fore.CYAN}{success_rate:.1f}%{Style.RESET_ALL}")
        print(f"   • SMTP Servers Used: {len(self.smtp_configs)}")
        print(f"   • Total Time: ~{(total_emails * self.countdown_time)/60:.1f} minutes")
        print(f"\n{Fore.CYAN}💬 For support and feedback: https://t.me/keem_backup{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}⚡ Thank you for using 00x00 Email Sender!{Style.RESET_ALL}")


def show_delivery_stats(self):
    """Show delivery statistics for the campaign"""
    print("REAL-TIME DELIVERY ANALYTICS")
    print(f"{'='*60}{Style.RESET_ALL}")
    print(f"📊 Success Rate: {Fore.GREEN}{stats['success_rate']}%{Style.RESET_ALL}")
    print(f"📈 Total Attempts: {stats['total_attempts']}")
    print(f"📉 Bounce Rate: {Fore.YELLOW}{stats['bounce_rate']}%{Style.RESET_ALL}")

    alerts = self.alerts.check_alerts()
    if alerts:
        print(f"{Fore.RED}🚨 ACTIVE ALERTS:")
        for alert in alerts[-3:]:
            print(f"  - {alert['type']}: {alert['message']} {Style.RESET_ALL}")

        


def main():
    init(autoreset=True)
    print_banner()
    print("Starting 00x00 Advanced Email Sender...")
    print(f"{Fore.CYAN}💬 Need support? Contact: https://t.me/keem_backup{Style.RESET_ALL}")
    print()
    create_required_directories()
    create_advanced_config()

    sender = EmailSender()
    
    email_file = "email.txt"
    if not os.path.exists(email_file):
        print(f"[!] Email list file not found: {email_file}")
        print("[*] Creating a sample email list file...")
        with open(email_file, "w") as f:
            f.write("recipient1@example.com\nrecipient2@example.com\n")
    
    print("\nOptions:")
    print("1. Start Mass Campaign (with 3.8s load time)")
    print("2. Start campaign with specific template")
    print("3. Convert attachments to PDF")
    print("4. Configure mass sending settings")
    print("5. Exit")
    
    choice = input("\nSelect an option (1-5): ")

    
    
    if choice == "1":
        print(f"{Fore.GREEN}[📧] Starting Sequential Email Campaign with {sender.countdown_time}s load time{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[⚡] Mode: Load {sender.countdown_time}s → Send email → Load {sender.countdown_time}s → Send next email{Style.RESET_ALL}")
        sender.enable_countdown = True
        sender.run_campaign(email_file, "templates", "attachments", use_random_template=True)
        
        print(f"{Fore.YELLOW}[🔍] Pre-flight checks...{Style.RESET_ALL}")
        emails = sender.load_email_list(email_file)
        valid_emails = [e for e in emails if sender.email_validator.is_valid_email(e)]
        print(f"[✓] Validated {len(valid_emails)}/{len(emails)} emails")
        


    elif choice == "2":
        templates_dir = "templates"
        templates = (
            glob.glob(os.path.join(templates_dir, "*.html")) + 
            glob.glob(os.path.join(templates_dir, "*.htm")) + 
            glob.glob(os.path.join(templates_dir, "*.svg"))
        )
        if not templates:
            print("[!] No templates found in templates directory.")
            return
            
        print("\nAvailable templates:")
        for i, template in enumerate(templates):
            print(f"{i+1}. {os.path.basename(template)}")
            
        template_choice = input(f"\nSelect a template (1-{len(templates)}): ")
        try:
            template_index = int(template_choice) - 1
            if 0 <= template_index < len(templates):
                template_name = os.path.basename(templates[template_index])
                sender.enable_countdown = True
                sender.run_campaign(email_file, templates_dir, "attachments", 
                                   use_random_template=False, specific_template=template_name)
            else:
                print("[!] Invalid template selection.")
        except ValueError:
            print("[!] Invalid input.")
    elif choice == "5":
        print("Exiting...")
        print(f"{Fore.CYAN}💬 For support and updates: https://t.me/keem_backup{Style.RESET_ALL}")
    else:
        print("[!] Invalid choice.")

if __name__ == "__main__":
    main()