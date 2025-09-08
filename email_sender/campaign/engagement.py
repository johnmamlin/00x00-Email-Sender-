import json
import random
from datetime import datetime, timedelta
import hashlib
import re
from collections import defaultdict
import time

class EngagementOptimizer:
    def __init__(self):
        self.engagement_data = defaultdict(dict)
        self.send_times = []
        self.open_rates = {}
        self.click_rates = {}
        self.engagement_history = {}
        
       
        self.optimal_send_times = {
            0: [9, 10, 14, 15],  # Monday
            1: [9, 10, 11, 14, 15],  # Tuesday  
            2: [9, 10, 11, 14, 15],  # Wednesday
            3: [9, 10, 11, 14, 15],  # Thursday
            4: [9, 10, 11, 14],  # Friday
            5: [10, 11, 12],  # Saturday
            6: [10, 11, 12, 19, 20]  # Sunday
        }
        

        self.industry_benchmarks = {
            'open_rate': 0.21, 
            'click_rate': 0.027,  
            'unsubscribe_rate': 0.002 
        }
    
    def calculate_engagement_score(self, recipient_email, template_id):
        """Calculate engagement score for recipient-template combination"""
        base_score = 50  
        

        if recipient_email in self.engagement_history:
            history = self.engagement_history[recipient_email]
            
           
            recent_opens = sum(1 for date in history.get('opens', []) 
                             if (datetime.now() - datetime.fromisoformat(date)).days <= 30)
            recent_sends = sum(1 for date in history.get('sends', []) 
                             if (datetime.now() - datetime.fromisoformat(date)).days <= 30)
            
            if recent_sends > 0:
                recent_open_rate = recent_opens / recent_sends
                base_score += (recent_open_rate - 0.2) * 100  
            
         
            recent_clicks = sum(1 for date in history.get('clicks', []) 
                              if (datetime.now() - datetime.fromisoformat(date)).days <= 30)
            if recent_clicks > 0:
                base_score += 10 
            

            last_engagement = max(
                history.get('opens', ['2020-01-01']),
                history.get('clicks', ['2020-01-01'])
            )
            if last_engagement:
                days_since = (datetime.now() - datetime.fromisoformat(last_engagement[-1])).days
                if days_since <= 7:
                    base_score += 15
                elif days_since <= 30:
                    base_score += 5
                elif days_since > 90:
                    base_score -= 10
        
  
        if template_id in self.open_rates:
            template_performance = self.open_rates[template_id]
            base_score += (template_performance - 0.2) * 50
        

        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        if current_hour in self.optimal_send_times.get(current_day, []):
            base_score += 10
        
        return max(0, min(100, base_score))
    
    def optimize_send_timing(self, recipient_list, timezone_offset=0):
        """Determine optimal send times for recipient list"""
        optimal_times = []
        
        for recipient in recipient_list:
      
            if recipient in self.engagement_history:
                opens = self.engagement_history[recipient].get('opens', [])
                best_hours = []
                
                for open_time in opens:
                    hour = datetime.fromisoformat(open_time).hour
                    best_hours.append(hour)
                
                if best_hours:
              
                    hour_counts = defaultdict(int)
                    for hour in best_hours:
                        hour_counts[hour] += 1
                    
                    best_hour = max(hour_counts, key=hour_counts.get)
                    optimal_times.append(best_hour)
                else:
                  
                    day = datetime.now().weekday()
                    optimal_times.append(random.choice(self.optimal_send_times.get(day, [10])))
            else:
              
                day = datetime.now().weekday()
                optimal_times.append(random.choice(self.optimal_send_times.get(day, [10])))
        

        if optimal_times:
            hour_counts = defaultdict(int)
            for hour in optimal_times:
                hour_counts[hour] += 1
            return max(hour_counts, key=hour_counts.get)
        
        return 10 
    
    def create_engagement_tracking_pixels(self, email_id, recipient_email):
        """Create tracking pixels for engagement monitoring"""
  
        tracking_id = hashlib.md5(f"{email_id}{recipient_email}{datetime.now()}".encode()).hexdigest()
        
    
        open_pixel = f'''<img src="https://track.yourdomain.com/open/{tracking_id}" width="1" height="1" style="display:none;" alt="">'''
        
     
        def wrap_links_with_tracking(html_content):
            def replace_link(match):
                original_url = match.group(1)
                tracked_url = f"https://track.yourdomain.com/click/{tracking_id}?url={original_url}"
                return f'href="{tracked_url}"'
            
            return re.sub(r'href=["\']([^"\']*)["\']', replace_link, html_content)
        
        return {
            'tracking_id': tracking_id,
            'open_pixel': open_pixel,
            'link_wrapper': wrap_links_with_tracking
        }
    
    def personalize_content(self, html_content, recipient_data):
        """Advanced content personalization based on recipient data"""
        personalized_content = html_content
     
        placeholders = {
            '##FIRST_NAME##': recipient_data.get('first_name', 'Valued Customer'),
            '##LAST_NAME##': recipient_data.get('last_name', ''),
            '##FULL_NAME##': f"{recipient_data.get('first_name', '')} {recipient_data.get('last_name', '')}".strip(),
            '##EMAIL##': recipient_data.get('email', ''),
            '##COMPANY##': recipient_data.get('company', ''),
            '##LOCATION##': recipient_data.get('location', ''),
            '##INDUSTRY##': recipient_data.get('industry', ''),
        }
        
        
        for placeholder, value in placeholders.items():
            personalized_content = personalized_content.replace(placeholder, value)
        

        if recipient_data.get('email') in self.engagement_history:
            history = self.engagement_history[recipient_data.get('email')]
            
          
            if history.get('clicks'):
              
                personalized_content = personalized_content.replace(
                    '##ENGAGEMENT_CONTENT##',
                    '<p>We noticed you\'ve been engaging with our emails - here\'s something special for you!</p>'
                )
            else:
        
                personalized_content = personalized_content.replace(
                    '##ENGAGEMENT_CONTENT##',
                    '<p>We want to make sure you\'re getting the most relevant content from us.</p>'
                )
        
      
        current_hour = datetime.now().hour
        if current_hour < 12:
            greeting = "Good morning"
        elif current_hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        personalized_content = personalized_content.replace('##TIME_GREETING##', greeting)
        
      
        if recipient_data.get('email') in self.engagement_history:
            history = self.engagement_history[recipient_data.get('email')]
            last_open = history.get('opens', [])
            
            if last_open and (datetime.now() - datetime.fromisoformat(last_open[-1])).days > 30:
           
                urgency_text = "We haven't heard from you in a while - don't miss out!"
            else:

                urgency_text = "Limited time offer - act now!"
            
            personalized_content = personalized_content.replace('##URGENCY_TEXT##', urgency_text)
        
        return personalized_content
    
    def segment_recipients(self, recipient_list):
        """Segment recipients based on engagement patterns"""
        segments = {
            'highly_engaged': [],
            'moderately_engaged': [],
            'low_engagement': [],
            'new_subscribers': [],
            'at_risk': []
        }
        
        for recipient in recipient_list:
            email = recipient.get('email', '')
            
            if email not in self.engagement_history:
                segments['new_subscribers'].append(recipient)
                continue
            
            history = self.engagement_history[email]
            
        
            opens = len(history.get('opens', []))
            clicks = len(history.get('clicks', []))
            sends = len(history.get('sends', []))
            
            if sends == 0:
                segments['new_subscribers'].append(recipient)
                continue
            
            open_rate = opens / sends if sends > 0 else 0
            click_rate = clicks / sends if sends > 0 else 0
            
  
            last_open = history.get('opens', [])
            days_since_last_open = 999
            if last_open:
                days_since_last_open = (datetime.now() - datetime.fromisoformat(last_open[-1])).days
            

            if open_rate > 0.4 and click_rate > 0.05:
                segments['highly_engaged'].append(recipient)
            elif open_rate > 0.2 and days_since_last_open < 30:
                segments['moderately_engaged'].append(recipient)
            elif days_since_last_open > 60:
                segments['at_risk'].append(recipient)
            else:
                segments['low_engagement'].append(recipient)
        
        return segments
    
    def generate_ab_test_variants(self, base_content, variant_count=3):
        """Generate A/B test variants for content optimization"""
        variants = []

        variants.append({
            'id': 'control',
            'content': base_content,
            'type': 'control'
        })
        
 
        subject_variants = [
            'Question-based subject',
            'Urgency-focused subject', 
            'Benefit-focused subject',
            'Personalized subject'
        ]
        
 
        cta_variants = [
            'Learn More',
            'Get Started',
            'Claim Now',
            'Discover More',
            'Take Action'
        ]
        
      
        for i in range(variant_count):
            variant_content = base_content
            
     
            cta_text = random.choice(cta_variants)
            variant_content = re.sub(
                r'(href="[^"]*"[^>]*>)[^<]*(</a>)',
                f'\\1{cta_text}\\2',
                variant_content
            )
            
     
            if i == 1:

                variant_content = variant_content.replace(
                    '</body>',
                    '<div style="margin: 20px 0; padding: 15px; background: #f5f5f5; border-left: 4px solid #007cba;">'
                    '<p><em>"This has been a game-changer for our business!" - Happy Customer</em></p>'
                    '</div></body>'
                )
            elif i == 2:
             
                variant_content = variant_content.replace(
                    '##URGENCY_TEXT##',
                    'Only 24 hours left! Limited spots available.'
                )
            
            variants.append({
                'id': f'variant_{i+1}',
                'content': variant_content,
                'type': 'test',
                'changes': f'CTA: {cta_text}, Variant type: {i+1}'
            })
        
        return variants
    
    def track_engagement_event(self, email_id, recipient_email, event_type, metadata=None):
        """Track engagement events for future optimization"""
        if recipient_email not in self.engagement_history:
            self.engagement_history[recipient_email] = {
                'opens': [],
                'clicks': [],
                'sends': [],
                'unsubscribes': []
            }
        
        timestamp = datetime.now().isoformat()
        
        if event_type in self.engagement_history[recipient_email]:
            self.engagement_history[recipient_email][event_type].append(timestamp)
        
   
        if metadata:
            self.engagement_history[recipient_email][f'{event_type}_metadata'] = metadata
    
    def get_engagement_recommendations(self, campaign_stats):
        """Generate recommendations based on engagement analysis"""
        recommendations = []
        
        open_rate = campaign_stats.get('open_rate', 0)
        click_rate = campaign_stats.get('click_rate', 0)
        unsubscribe_rate = campaign_stats.get('unsubscribe_rate', 0)
 
        if open_rate < self.industry_benchmarks['open_rate']:
            recommendations.append({
                'type': 'subject_line',
                'message': f'Open rate ({open_rate:.1%}) below benchmark ({self.industry_benchmarks["open_rate"]:.1%}). Consider testing different subject lines.',
                'priority': 'high'
            })
        

        if click_rate < self.industry_benchmarks['click_rate']:
            recommendations.append({
                'type': 'content',
                'message': f'Click rate ({click_rate:.1%}) below benchmark. Improve call-to-action visibility and content relevance.',
                'priority': 'medium'
            })
        
 
        if unsubscribe_rate > self.industry_benchmarks['unsubscribe_rate']:
            recommendations.append({
                'type': 'frequency',
                'message': f'High unsubscribe rate ({unsubscribe_rate:.1%}). Consider reducing send frequency or improving targeting.',
                'priority': 'high'
            })
        
        return recommendations
    
    def optimize_send_frequency(self, recipient_segments):
        """Determine optimal send frequency for each segment"""
        frequency_recommendations = {}
        
        for segment_name, recipients in recipient_segments.items():
            if segment_name == 'highly_engaged':
                frequency_recommendations[segment_name] = {
                    'frequency': 'daily',
                    'max_per_week': 5,
                    'optimal_days': [0, 1, 2, 3, 4]  # Weekdays
                }
            elif segment_name == 'moderately_engaged':
                frequency_recommendations[segment_name] = {
                    'frequency': 'bi-weekly',
                    'max_per_week': 3,
                    'optimal_days': [1, 2, 3]  # Tue, Wed, Thu
                }
            elif segment_name == 'low_engagement':
                frequency_recommendations[segment_name] = {
                    'frequency': 'weekly',
                    'max_per_week': 1,
                    'optimal_days': [2]  # Wednesday
                }
            elif segment_name == 'at_risk':
                frequency_recommendations[segment_name] = {
                    'frequency': 'bi-weekly',
                    'max_per_week': 1,
                    'optimal_days': [1],  # Tuesday
                    'special_content': 'reengagement'
                }
            else:  # new_subscribers
                frequency_recommendations[segment_name] = {
                    'frequency': 'welcome_series',
                    'max_per_week': 2,
                    'optimal_days': [1, 4]  # Tue, Fri
                }
        
        return frequency_recommendationss