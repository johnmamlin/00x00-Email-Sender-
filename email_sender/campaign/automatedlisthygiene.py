import re
import dns.resolver
import socket
from email_validator import validate_email, EmailNotValidError

class EmailValidator:
    """Validate email addresses for deliverability"""
    def __init__(self):
        pass
    
    def validate_email_syntax(self, email):
        """Validate email syntax"""
        try:
            validate_email(email)
            return True
        except:
            return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None
    
    def is_valid_email(self, email):
        """Check if email is valid"""
        return self.validate_email_syntax(email)
    
    def check_mx_record(self, domain):
        """Check if domain has MX record"""
        try:
            dns.resolver.resolve(domain, 'MX')
            return True
        except:
            return False
    
    def validate_email_full(self, email):
        """Full email validation"""
        if not self.validate_email_syntax(email):
            return False, "Invalid syntax"
        
        domain = email.split('@')[1]
        if not self.check_mx_record(domain):
            return False, "No MX record"
        
        return True, "Valid"

class ListCleaner:
    """Clean and maintain email lists"""
    def __init__(self):
        self.validator = EmailValidator()
    
    def clean_list(self, email_list):
        """Clean email list"""
        clean_emails = []
        invalid_emails = []
        
        for email in email_list:
            is_valid, reason = self.validator.validate_email_full(email)
            if is_valid:
                clean_emails.append(email)
            else:
                invalid_emails.append((email, reason))
        
        return clean_emails, invalid_emails
    
    def remove_duplicates(self, email_list):
        """Remove duplicate emails"""
        return list(set(email_list))
    
    def suppress_bounces(self, email_list, bounce_list):
        """Remove bounced emails from list"""
        return [email for email in email_list if email not in bounce_list]
