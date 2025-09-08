import time
import random
import datetime
from typing import List, Dict, Optional
import pytz
from collections import defaultdict
import threading
from dataclasses import dataclass

@dataclass
class SendingWindow:
    start_hour: int
    end_hour: int
    timezone: str
    max_emails_per_hour: int

class IntelligentScheduler:
    def __init__(self):
        self.sending_windows = {
            'business': SendingWindow(9, 17, 'US/Eastern', 50),
            'consumer': SendingWindow(18, 22, 'US/Eastern', 30),
            'international': SendingWindow(10, 16, 'UTC', 20)
        }
        self.daily_limits = defaultdict(int)
        self.hourly_limits = defaultdict(int)
        self.current_hour = None
        self.warm_up_mode = True
        self.reputation_score = 0.0
        
    def get_optimal_send_time(self, recipient_email: str, campaign_type: str = 'business') -> datetime.datetime:
        """Calculate optimal send time based on recipient patterns and deliverability"""
        now = datetime.datetime.now()
        
   
        domain = recipient_email.split('@')[1].lower()
        timezone = self._detect_timezone_from_domain(domain)
        
      
        window = self.sending_windows.get(campaign_type, self.sending_windows['business'])
        
      
        target_tz = pytz.timezone(timezone)
        local_now = now.astimezone(target_tz)
        
     
        if window.start_hour <= local_now.hour <= window.end_hour:
         
            delay_minutes = random.randint(1, 30)
            return now + datetime.timedelta(minutes=delay_minutes)
        
      
        if local_now.hour < window.start_hour:
            next_send = local_now.replace(hour=window.start_hour, minute=random.randint(0, 59))
        else:
       
            next_send = (local_now + datetime.timedelta(days=1)).replace(
                hour=window.start_hour, minute=random.randint(0, 59)
            )
        
        return next_send.astimezone(pytz.UTC).replace(tzinfo=None)
    
    def _detect_timezone_from_domain(self, domain: str) -> str:
        """Detect likely timezone from email domain"""
        domain_tz_map = {
            'gmail.com': 'US/Pacific',
            'yahoo.com': 'US/Eastern', 
            'outlook.com': 'US/Eastern',
            'hotmail.com': 'US/Eastern',
            'aol.com': 'US/Eastern',
            'icloud.com': 'US/Pacific',
            'protonmail.com': 'Europe/Zurich',
            'yandex.ru': 'Europe/Moscow',
            'mail.ru': 'Europe/Moscow',
            'qq.com': 'Asia/Shanghai',
            '163.com': 'Asia/Shanghai',
            'naver.com': 'Asia/Seoul'
        }
        
        return domain_tz_map.get(domain, 'UTC')
    
    def calculate_sending_delay(self, smtp_config: Dict, reputation_score: float = 0.5) -> int:
        """Calculate intelligent delay between emails based on reputation and limits"""
        base_delay = 30  
        
      
        reputation_multiplier = max(0.5, 2.0 - reputation_score)
        
       
        if self.warm_up_mode:
            warmup_multiplier = 2.0  
        else:
            warmup_multiplier = 1.0
        
 
        jitter = random.uniform(0.8, 1.2)
        
 
        delay = int(base_delay * reputation_multiplier * warmup_multiplier * jitter)
        
       
        return max(15, min(300, delay)) 
    
    def should_pause_sending(self, smtp_config: Dict) -> tuple[bool, str]:
        """Determine if sending should be paused based on various factors"""
        current_hour = datetime.datetime.now().hour
      
        if current_hour < 6 or current_hour > 22:
            return True, "Outside optimal sending hours (6 AM - 10 PM)"
        
        
        today = datetime.date.today().isoformat()
        daily_sent = self.daily_limits.get(f"{smtp_config['email']}_{today}", 0)
        
        if daily_sent > 500:  
            return True, f"Daily limit reached: {daily_sent}/500"
        
     
        current_hour_key = f"{smtp_config['email']}_{datetime.datetime.now().strftime('%Y-%m-%d-%H')}"
        hourly_sent = self.hourly_limits.get(current_hour_key, 0)
        
        max_per_hour = 50 if not self.warm_up_mode else 25
        if hourly_sent >= max_per_hour:
            return True, f"Hourly limit reached: {hourly_sent}/{max_per_hour}"
        
        return False, "All clear"
    
    def update_sending_stats(self, smtp_config: Dict, success: bool):
        """Update sending statistics and reputation"""
        today = datetime.date.today().isoformat()
        current_hour_key = f"{smtp_config['email']}_{datetime.datetime.now().strftime('%Y-%m-%d-%H')}"
        
       
        self.daily_limits[f"{smtp_config['email']}_{today}"] += 1
        self.hourly_limits[current_hour_key] += 1
        
   
        if success:
            self.reputation_score = min(1.0, self.reputation_score + 0.01)
        else:
            self.reputation_score = max(0.0, self.reputation_score - 0.05)
        
       
        total_sent = sum(v for k, v in self.daily_limits.items() if smtp_config['email'] in k)
        if total_sent > 100:
            self.warm_up_mode = False

class ThrottleManager:
    def __init__(self):
        self.last_send_times = {}
        self.adaptive_delays = defaultdict(lambda: 30) 
        
    def get_throttle_delay(self, smtp_email: str, recent_failures: int = 0) -> int:
        """Get adaptive throttle delay based on recent performance"""
        base_delay = self.adaptive_delays[smtp_email]
        
     
        failure_multiplier = 1 + (recent_failures * 0.5)
        
      
        jitter = random.uniform(0.7, 1.3)
        
        return int(base_delay * failure_multiplier * jitter)
    
    def update_throttle(self, smtp_email: str, success: bool, response_time: float):
        """Update throttle settings based on success rate and response time"""
        current_delay = self.adaptive_delays[smtp_email]
        
        if success and response_time < 5.0:  
   
            self.adaptive_delays[smtp_email] = max(15, current_delay * 0.95)
        elif not success:
           
            self.adaptive_delays[smtp_email] = min(300, current_delay * 1.5)
        elif response_time > 10.0: 
        
            self.adaptive_delays[smtp_email] = min(120, current_delay * 1.1)

def create_intelligent_schedule(email_list: List[str], campaign_type: str = 'business') -> Dict[str, datetime.datetime]:
    """Create an intelligent sending schedule for email list"""
    scheduler = IntelligentScheduler()
    schedule = {}
    
    for email in email_list:
        optimal_time = scheduler.get_optimal_send_time(email, campaign_type)
        schedule[email] = optimal_time
    
    return schedule