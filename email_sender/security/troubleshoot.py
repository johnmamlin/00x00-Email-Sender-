"""
Email Troubleshooting and Error Diagnostics Module
Part of 00x00 Advanced Email Sender Security Suite
"""

from colorama import Fore, Style
import re


class EmailTroubleshooter:
    """Advanced email delivery troubleshooting and error analysis"""
    
    def __init__(self):
        self.error_patterns = {
            'authentication': [
                'authentication failed', 'auth', 'username', 'password', 
                '535', 'invalid credentials', 'login failed'
            ],
            'recipient': [
                'recipient', 'mailbox', 'user unknown', '550', '551',
                'address rejected', 'no such user', 'invalid recipient'
            ],
            'rate_limit': [
                'rate limit', 'quota', 'too many', '421', '452',
                'throttled', 'sending limit', 'exceeded'
            ],
            'connection': [
                'connection', 'timeout', 'refused', 'network', 
                'unreachable', 'host', 'socket'
            ],
            'security_ssl': [
                'ssl', 'tls', 'certificate', 'handshake',
                'secure connection', 'encryption'
            ],
            'malware_spam': [
                'virus', 'malware', 'spam', 'blocked', 'security', 
                'policy', '554', 'content filtered', 'suspicious'
            ],
            'content': [
                'content', 'message', 'body', 'mime', 'format',
                'encoding', 'invalid message'
            ],
            'dns': [
                'dns', 'domain', 'mx record', 'nxdomain',
                'name resolution', 'lookup failed'
            ],
            'temporary': [
                'temporary', 'try again', '4', 'service unavailable',
                'server busy'
            ],
            'blacklist': [
                'blacklist', 'reputation', 'rbl', 'dnsbl',
                'blocked ip', 'sender reputation'
            ]
        }
    
    def analyze_error(self, error, recipient, smtp_config):
        """
        Analyze email delivery error and provide detailed diagnosis
        
        Args:
            error: Exception object or error message
            recipient: Target email address
            smtp_config: SMTP configuration dictionary
            
        Returns:
            dict: Detailed troubleshooting report
        """
        error_str = str(error).lower()
        error_code = self._extract_error_code(error)
        
   
        error_category = self._categorize_error(error_str)
        
 
        report = self._generate_report(error_category, error_str, recipient, smtp_config)
        report['technical_details'] = str(error)
        report['error_code'] = error_code
        
        return report
    
    def _extract_error_code(self, error):
        """Extract SMTP error code from exception"""
        if hasattr(error, 'smtp_code'):
            return error.smtp_code
        
       
        error_str = str(error)
        code_match = re.search(r'\b([45]\d{2})\b', error_str)
        return code_match.group(1) if code_match else None
    
    def _categorize_error(self, error_str):
        """Categorize error based on patterns"""
        for category, patterns in self.error_patterns.items():
            if any(pattern in error_str for pattern in patterns):
                return category
        return 'unknown'
    
    def _generate_report(self, category, error_str, recipient, smtp_config):
        """Generate detailed troubleshooting report"""
        
        reports = {
            'authentication': {
                'issue_type': 'SMTP Authentication Failed',
                'root_cause': f'Invalid credentials for {smtp_config.get("username", "unknown")} on {smtp_config.get("server", "unknown")}',
                'recommended_action': 'Verify SMTP username/password in smtp.txt file',
                'severity': 'HIGH',
                'auto_retry': False
            },
            'recipient': {
                'issue_type': 'Recipient Address Invalid',
                'root_cause': f'Email address {recipient} does not exist or is rejected by server',
                'recommended_action': 'Remove invalid email from list or verify correct address format',
                'severity': 'MEDIUM',
                'auto_retry': False
            },
            'rate_limit': {
                'issue_type': 'Rate Limiting Detected',
                'root_cause': f'SMTP server {smtp_config.get("server", "unknown")} is limiting send rate',
                'recommended_action': 'Reduce sending speed, implement delays, or rotate SMTP servers',
                'severity': 'MEDIUM',
                'auto_retry': True
            },
            'connection': {
                'issue_type': 'Connection Failed',
                'root_cause': f'Cannot establish connection to {smtp_config.get("server", "unknown")}:{smtp_config.get("port", "unknown")}',
                'recommended_action': 'Check internet connection, firewall settings, and SMTP server status',
                'severity': 'HIGH',
                'auto_retry': True
            },
            'security_ssl': {
                'issue_type': 'SSL/TLS Security Error',
                'root_cause': f'Secure connection handshake failed with {smtp_config.get("server", "unknown")}',
                'recommended_action': 'Verify SSL port (465) or STARTTLS port (587) configuration',
                'severity': 'HIGH',
                'auto_retry': False
            },
            'malware_spam': {
                'issue_type': 'Security/Content Blocked',
                'root_cause': 'Email flagged as spam/malware by security filters',
                'recommended_action': 'Review email content, remove suspicious links/attachments, check sender reputation',
                'severity': 'HIGH',
                'auto_retry': False
            },
            'content': {
                'issue_type': 'Email Content Error',
                'root_cause': 'Invalid email format, encoding, or MIME structure',
                'recommended_action': 'Check template file format, character encoding, and MIME headers',
                'severity': 'MEDIUM',
                'auto_retry': False
            },
            'dns': {
                'issue_type': 'DNS Resolution Failed',
                'root_cause': f'Cannot resolve domain for {recipient.split("@")[1] if "@" in recipient else "unknown domain"}',
                'recommended_action': 'Verify recipient domain exists and has valid MX records',
                'severity': 'MEDIUM',
                'auto_retry': True
            },
            'temporary': {
                'issue_type': 'Temporary Server Error',
                'root_cause': 'SMTP server experiencing temporary issues (4xx error)',
                'recommended_action': 'Retry sending after brief delay - server should recover',
                'severity': 'LOW',
                'auto_retry': True
            },
            'blacklist': {
                'issue_type': 'Sender Blacklisted',
                'root_cause': 'Sender IP or domain is on blacklist/reputation database',
                'recommended_action': 'Check sender reputation, use different SMTP provider, or contact blacklist for removal',
                'severity': 'HIGH',
                'auto_retry': False
            },
            'unknown': {
                'issue_type': 'Unknown Error',
                'root_cause': 'Unable to categorize specific error cause',
                'recommended_action': 'Review technical details and check SMTP configuration',
                'severity': 'MEDIUM',
                'auto_retry': False
            }
        }
        
        return reports.get(category, reports['unknown'])
    
    def format_error_display(self, report):
        """Format error report for console display"""
        severity_colors = {
            'HIGH': Fore.RED,
            'MEDIUM': Fore.YELLOW,
            'LOW': Fore.CYAN
        }
        
        color = severity_colors.get(report.get('severity', 'MEDIUM'), Fore.YELLOW)
        
        formatted_lines = [
            f"| Status{' ' * 6}| {Fore.RED}✗ {report['issue_type']}{Style.RESET_ALL}",
            f"| Severity{' ' * 4}| {color}{report.get('severity', 'MEDIUM')}{Style.RESET_ALL}",
            f"| Root Cause{' ' * 2}| {Fore.YELLOW}{report['root_cause']}{Style.RESET_ALL}",
            f"| Action{' ' * 6}| {Fore.CYAN}{report['recommended_action']}{Style.RESET_ALL}"
        ]
        
       
        tech_details = report.get('technical_details', '')
        if tech_details and len(tech_details) < 60:
            formatted_lines.append(f"| Technical{' ' * 3}| {tech_details}")
        elif tech_details:
            formatted_lines.append(f"| Technical{' ' * 3}| {tech_details[:57]}...")
        
       
        if report.get('error_code'):
            formatted_lines.append(f"| Error Code{' ' * 2}| {report['error_code']}")
        

        retry_text = "Recommended" if report.get('auto_retry', False) else "Not Recommended"
        formatted_lines.append(f"| Auto Retry{' ' * 2}| {retry_text}")
        
        return formatted_lines
    
    def should_retry(self, report):
        """Determine if error should trigger automatic retry"""
        return report.get('auto_retry', False)
    
    def get_retry_delay(self, report):
        """Get recommended delay before retry based on error type"""
        delay_map = {
            'rate_limit': 60,  # 1 minute
            'connection': 30,  # 30 seconds
            'temporary': 120,  # 2 minutes
            'dns': 45         # 45 seconds
        }
        
  
        issue_type = report.get('issue_type', '').lower()
        for category, delay in delay_map.items():
            if category.replace('_', ' ') in issue_type:
                return delay
        
        return 30  



def troubleshoot_email_error(error, recipient, smtp_config):
    """
    Convenience function to troubleshoot email errors
    
    Args:
        error: Exception object or error message
        recipient: Target email address  
        smtp_config: SMTP configuration dictionary
        
    Returns:
        dict: Detailed troubleshooting report
    """
    troubleshooter = EmailTroubleshooter()
    return troubleshooter.analyze_error(error, recipient, smtp_config)