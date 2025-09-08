import smtplib
import socket
from typing import Tuple, Optional


def check_smtp_health(smtp_info):
    """Check if SMTP server is healthy (standalone function)"""
    try:
        with smtplib.SMTP(smtp_info["server"], smtp_info["port"], timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_info["username"], smtp_info["password"])
            return True
        
    except Exception as e:
        print(f"SMTP health check failed for {smtp_info['server']}: {e}")
        return False


class SMTPHealthChecker:

    def check_smtp_health(self, smtp_info):
        """Check if SMTP server is healthy"""
        try:
            with smtplib.SMTP(smtp_info["server"], smtp_info["port"], timeout=10) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(smtp_info["username"], smtp_info["password"])
                return True
            
        except Exception as e:
            self.logger.warning(f"SMTP health check failed for {smtp_info['server']}: {e}")
            return False
        
    def get_healthy_smtp(self):
        """Get a healthy SMTP server"""
        max_attempts = len(self.smtp_servers)
        attempts = 0

        while attempts < max_attempts:
            smtp_info = self.get_next_smtp()
            if self.check_smtp_health(smtp_info):
                return smtp_info
            attempts += 1
        self.logger.error("No healthy SMTP servers available")
        return None