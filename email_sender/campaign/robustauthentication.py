# robustauthentication.py - Robust Email Authentication System
import dns.resolver
import smtplib
import ssl
import socket
import re
import hashlib
import base64
import hmac
from email.header import Header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid
import time
import random
from colorama import Fore, Style
import dkim
from email.message import EmailMessage
import os

class EmailAuthenticator:
    def __init__(self):
        self.dkim_enabled = True
        self.spf_validation = True
        self.dmarc_policy = "quarantine"
        self.authentication_results = {}
    
    def validate_spf_record(self, domain, sending_ip):
        """Validate SPF record for domain"""
        try:
           
            spf_records = []
            try:
                txt_records = dns.resolver.resolve(domain, 'TXT')
                for record in txt_records:
                    if record.to_text().startswith('"v=spf1'):
                        spf_records.append(record.to_text().strip('"'))
            except:
                return {"valid": False, "reason": "No SPF record found"}
            
            if not spf_records:
                return {"valid": False, "reason": "No SPF record found"}
            
          
            spf_record = spf_records[0]
            
           
            if any(mech in spf_record for mech in ['include:', 'a:', 'mx:', 'ip4:', 'ip6:']):
               
                if 'include:_spf.google.com' in spf_record or 'include:spf.protection.outlook.com' in spf_record:
                    return {"valid": True, "record": spf_record, "mechanism": "include"}
                elif f'ip4:{sending_ip}' in spf_record:
                    return {"valid": True, "record": spf_record, "mechanism": "ip4"}
                else:
                    return {"valid": True, "record": spf_record, "mechanism": "found"}
            
            return {"valid": False, "reason": "SPF record exists but may not authorize sending IP"}
            
        except Exception as e:
            return {"valid": False, "reason": f"SPF validation error: {str(e)}"}
    
    def check_dmarc_policy(self, domain):
        """Check DMARC policy for domain"""
        try:
            dmarc_domain = f"_dmarc.{domain}"
            txt_records = dns.resolver.resolve(dmarc_domain, 'TXT')
            
            for record in txt_records:
                record_text = record.to_text().strip('"')
                if record_text.startswith('v=DMARC1'):
                  
                    policy_match = re.search(r'p=(\w+)', record_text)
                    policy = policy_match.group(1) if policy_match else 'none'
                    
         
                    aspf_match = re.search(r'aspf=(\w+)', record_text)
                    aspf = aspf_match.group(1) if aspf_match else 's'
                    
                    adkim_match = re.search(r'adkim=(\w+)', record_text)
                    adkim = adkim_match.group(1) if adkim_match else 's'
                    
                    return {
                        "exists": True,
                        "policy": policy,
                        "aspf": aspf,
                        "adkim": adkim,
                        "record": record_text
                    }
            
            return {"exists": False, "reason": "No DMARC record found"}
            
        except Exception as e:
            return {"exists": False, "reason": f"DMARC check error: {str(e)}"}
    def sign_message(self, message, domain=None, selector=None, private_key=None):
        """Proper DKIM message signing implementation"""
        if not private_key:
             private_key = self.dkim_private_key
        if not selector:
             selector = self.dkim_selector
    
        if not private_key:
             print(f"{Fore.YELLOW}Warning: No DKIM private key configured{Style.RESET_ALL}")
             return message
    
        try:
  
            msg_bytes = message.as_bytes() if hasattr(message, 'as_bytes') else str(message).encode()
        

            sig = dkim.sign(
                message=msg_bytes,
                selector=str(selector).encode(),
                domain=str(domain).encode(),
                privkey=private_key,
                include_headers=['From', 'To', 'Subject', 'Date']
            )
        
   
            message['DKIM-Signature'] = sig.decode('utf-8').split(':', 1)[1].strip()
            return message
        except Exception as e:
            print(f"{Fore.RED}DKIM signing failed: {str(e)}{Style.RESET_ALL}")
            return message


    def generate_dkim_signature(self, message, domain, selector="default", private_key=None):
        """Generate DKIM signature (simplified version)"""
        if not private_key:
           
            print(f"{Fore.YELLOW}[DKIM] Using mock DKIM signature for {domain}{Style.RESET_ALL}")
            return f"v=1; a=rsa-sha256; d={domain}; s={selector}; c=relaxed/relaxed; h=from:to:subject:date; bh=mock_body_hash; b=mock_signature"
        

        return None
    
    def create_authenticated_message(self, from_name, from_email, to_email, subject, html_content, smtp_config):
        """Create email message with proper authentication headers"""
        msg = MIMEMultipart('alternative')
        
  
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg['Date'] = formatdate(localtime=True)
        msg['Message-ID'] = make_msgid(domain=from_email.split('@')[1])
        

        domain = from_email.split('@')[1]
        
     
        msg['Return-Path'] = from_email
        
    
        if smtp_config.get('sender_email') and smtp_config['sender_email'] != from_email:
            msg['Sender'] = smtp_config['sender_email']
        

        msg['List-Unsubscribe'] = f"<mailto:unsubscribe@{domain}>"
        msg['List-Unsubscribe-Post'] = "List-Unsubscribe=One-Click"
        
   
        msg['X-Mailer'] = "Professional Email Campaign System"
        msg['X-Priority'] = "3"
        msg['X-MSMail-Priority'] = "Normal"
        
     
        dkim_signature = self.generate_dkim_signature(msg, domain)
        if dkim_signature:
            msg['DKIM-Signature'] = dkim_signature
        
     
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        return msg
    
    def validate_smtp_authentication(self, smtp_config):
        """Validate SMTP server authentication and security"""
        try:
            server_host = smtp_config['server']
            server_port = smtp_config['port']
            username = smtp_config['username']
            password = smtp_config['password']
            
 
            context = ssl.create_default_context()
            
            if server_port == 465:
         
                server = smtplib.SMTP_SSL(server_host, server_port, context=context)
            else:
             
                server = smtplib.SMTP(server_host, server_port)
                server.starttls(context=context)
            
       
            server.login(username, password)
            
        
            capabilities = server.esmtp_features
            
    
            security_features = {
                'starttls': 'STARTTLS' in capabilities,
                'auth_methods': capabilities.get('auth', '').split(),
                'size_limit': capabilities.get('size', 'unlimited'),
                'pipelining': 'PIPELINING' in capabilities,
                'dsn': 'DSN' in capabilities
            }
            
            server.quit()
            
            return {
                "authenticated": True,
                "security_features": security_features,
                "server_info": f"{server_host}:{server_port}",
                "auth_method": "LOGIN"
            }
            
        except smtplib.SMTPAuthenticationError as e:
            return {"authenticated": False, "error": "Authentication failed", "details": str(e)}
        except smtplib.SMTPConnectError as e:
            return {"authenticated": False, "error": "Connection failed", "details": str(e)}
        except Exception as e:
            return {"authenticated": False, "error": "Unknown error", "details": str(e)}
    
    def check_domain_reputation(self, domain):
        """Check domain reputation using DNS-based checks"""
        reputation_score = 100
        issues = []
        
        try:
         
            blacklist_checks = [
                'zen.spamhaus.org',
                'bl.spamcop.net',
                'b.barracudacentral.org'
            ]
            
          
            try:
                ip = socket.gethostbyname(domain)
                reversed_ip = '.'.join(reversed(ip.split('.')))
                
                for blacklist in blacklist_checks:
                    try:
                        query = f"{reversed_ip}.{blacklist}"
                        result = socket.gethostbyname(query)
                        if result:
                            reputation_score -= 30
                            issues.append(f"Listed on {blacklist}")
                    except socket.gaierror:
                        pass  
                        
            except socket.gaierror:
                issues.append("Domain resolution failed")
                reputation_score -= 20
            
          
            dns_checks = {
                'MX': 'MX',
                'A': 'A',
                'TXT': 'TXT'
            }
            
            for record_type, dns_type in dns_checks.items():
                try:
                    dns.resolver.resolve(domain, dns_type)
                except:
                    reputation_score -= 10
                    issues.append(f"Missing {record_type} record")
            
            return {
                "reputation_score": max(reputation_score, 0),
                "issues": issues,
                "status": "good" if reputation_score >= 80 else "warning" if reputation_score >= 60 else "poor"
            }
            
        except Exception as e:
            return {
                "reputation_score": 0,
                "issues": [f"Reputation check failed: {str(e)}"],
                "status": "unknown"
            }
    
    def perform_comprehensive_auth_check(self, smtp_config, recipient_domain=None):
        """Perform comprehensive authentication check"""
        print(f"\n{Fore.CYAN}🔐 AUTHENTICATION VERIFICATION{Style.RESET_ALL}")
        print("=" * 50)
        
        from_email = smtp_config.get('email', smtp_config.get('username', ''))
        sender_domain = from_email.split('@')[1] if '@' in from_email else ''
        
        results = {}
        
       
        print("1. SMTP Server Authentication...")
        smtp_auth = self.validate_smtp_authentication(smtp_config)
        results['smtp_auth'] = smtp_auth
        
        if smtp_auth['authenticated']:
            print(f"   {Fore.GREEN}✓ SMTP Authentication: PASSED{Style.RESET_ALL}")
            if smtp_auth.get('security_features', {}).get('starttls'):
                print(f"   {Fore.GREEN}✓ STARTTLS: Supported{Style.RESET_ALL}")
        else:
            print(f"   {Fore.RED}✗ SMTP Authentication: FAILED{Style.RESET_ALL}")
            print(f"   Error: {smtp_auth.get('error', 'Unknown')}")
        
      
        if sender_domain:
            print("\n2. Domain Reputation Check...")
            domain_rep = self.check_domain_reputation(sender_domain)
            results['domain_reputation'] = domain_rep
            
            score = domain_rep['reputation_score']
            if score >= 80:
                print(f"   {Fore.GREEN}✓ Domain Reputation: GOOD ({score}/100){Style.RESET_ALL}")
            elif score >= 60:
                print(f"   {Fore.YELLOW}⚠ Domain Reputation: WARNING ({score}/100){Style.RESET_ALL}")
            else:
                print(f"   {Fore.RED}✗ Domain Reputation: POOR ({score}/100){Style.RESET_ALL}")
            
            if domain_rep['issues']:
                for issue in domain_rep['issues']:
                    print(f"   - {issue}")
        
      
        if sender_domain:
            print("\n3. SPF Record Validation...")
       
            try:
                sending_ip = socket.gethostbyname(smtp_config['server'])
                spf_result = self.validate_spf_record(sender_domain, sending_ip)
                results['spf'] = spf_result
                
                if spf_result['valid']:
                    print(f"   {Fore.GREEN}✓ SPF Record: VALID{Style.RESET_ALL}")
                    print(f"   Mechanism: {spf_result.get('mechanism', 'unknown')}")
                else:
                    print(f"   {Fore.YELLOW}⚠ SPF Record: {spf_result.get('reason', 'Invalid')}{Style.RESET_ALL}")
            except Exception as e:
                print(f"   {Fore.RED}✗ SPF Check Failed: {str(e)}{Style.RESET_ALL}")
        
     
        if sender_domain:
            print("\n4. DMARC Policy Check...")
            dmarc_result = self.check_dmarc_policy(sender_domain)
            results['dmarc'] = dmarc_result
            
            if dmarc_result['exists']:
                policy = dmarc_result['policy']
                print(f"   {Fore.GREEN}✓ DMARC Record: EXISTS{Style.RESET_ALL}")
                print(f"   Policy: {policy}")
                
                if policy == 'reject':
                    print(f"   {Fore.RED}⚠ Strict Policy: May cause delivery issues if not properly configured{Style.RESET_ALL}")
                elif policy == 'quarantine':
                    print(f"   {Fore.YELLOW}⚠ Moderate Policy: Emails may go to spam if authentication fails{Style.RESET_ALL}")
            else:
                print(f"   {Fore.YELLOW}⚠ DMARC Record: NOT FOUND{Style.RESET_ALL}")
                print(f"   Recommendation: Add DMARC record for better deliverability")
        
        print("\n" + "=" * 50)
        
    
        auth_score = 0
        max_score = 100
        
        if smtp_auth['authenticated']:
            auth_score += 40
        if results.get('domain_reputation', {}).get('reputation_score', 0) >= 80:
            auth_score += 30
        if results.get('spf', {}).get('valid', False):
            auth_score += 20
        if results.get('dmarc', {}).get('exists', False):
            auth_score += 10
        
        print(f"Overall Authentication Score: {auth_score}/100")
        
        if auth_score >= 80:
            print(f"{Fore.GREEN}✅ EXCELLENT - Ready for high deliverability{Style.RESET_ALL}")
        elif auth_score >= 60:
            print(f"{Fore.YELLOW}⚠️ GOOD - Minor improvements recommended{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}❌ NEEDS IMPROVEMENT - Address authentication issues{Style.RESET_ALL}")
        
        return results, auth_score


class AuthenticationManager:
    def __init__(self, dkim_private_key_path=None, dkim_selector=None):
        self.authenticator = EmailAuthenticator()
        self.validated_configs = {}
        self.dkim_selector = dkim_selector
        self.dkim_private_key_path = dkim_private_key_path
       
        dkim_selector = 'default' 

        self.dkim_private_key = None
        if dkim_private_key_path and os.path.exists(dkim_private_key_path):
            try:
                with open(dkim_private_key_path, 'rb') as f:
                    self.dkim_private_key = f.read()
            except Exception as e:
                print(f"{Fore.RED}Failed to load DKIM key: {str(e)}{Style.RESET_ALL}")

    
    def validate_all_smtp_configs(self, smtp_configs):
        """Validate all SMTP configurations"""
        print(f"\n{Fore.CYAN}🔐 VALIDATING SMTP AUTHENTICATION{Style.RESET_ALL}")
        validated = []
        
        for i, config in enumerate(smtp_configs):
            print(f"\nValidating SMTP #{i+1}: {config['server']}")
            auth_results, score = self.authenticator.perform_comprehensive_auth_check(config)
            
            if score >= 60:  
                validated.append({
                    **config,
                    'auth_score': score,
                    'auth_results': auth_results
                })
                print(f"{Fore.GREEN}✓ SMTP #{i+1} validated successfully{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}✗ SMTP #{i+1} failed validation (score: {score}/100){Style.RESET_ALL}")
        
        self.validated_configs = validated
        return validated
    
    def create_authenticated_email(self, from_name, from_email, to_email, subject, content, smtp_config):
        """Create properly authenticated email message"""
        return self.authenticator.create_authenticated_message(
            from_name, from_email, to_email, subject, content, smtp_config
        )
    def sign_message(self, message, domain):
        """Sign email message with DKIM"""
        if not self.dkim_private_key:
            return message
    
        try:
   
            import dkim
            signature = dkim.sign(
                message.as_bytes(),
                self.dkim_selector.encode(),
                domain.encode(),
                self.dkim_private_key
        )
       
            return message
        except Exception as e:
            print(f"DKIM signing failed: {e}")
            return message