# reporting.py - Advanced Email Campaign Reporting & Analytics
import json
import sqlite3
import datetime
from collections import defaultdict
import os
from colorama import Fore, Style
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

class CampaignReporter:
    def __init__(self, db_path="campaign_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for campaign tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS campaign_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                campaign_id TEXT,
                recipient_email TEXT,
                smtp_server TEXT,
                delivery_status TEXT,
                bounce_type TEXT,
                engagement_score REAL,
                delivery_time REAL,
                ip_reputation REAL,
                domain_reputation REAL,
                spam_score REAL,
                authentication_status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deliverability_trends (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE,
                total_sent INTEGER,
                delivered INTEGER,
                bounced INTEGER,
                spam_folder INTEGER,
                inbox_rate REAL,
                domain_reputation_avg REAL,
                ip_reputation_avg REAL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def log_email_attempt(self, campaign_id, recipient, smtp_server, status, **kwargs):
        """Log individual email sending attempt with deliverability metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO campaign_metrics 
            (campaign_id, recipient_email, smtp_server, delivery_status, 
             bounce_type, engagement_score, delivery_time, ip_reputation, 
             domain_reputation, spam_score, authentication_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id, recipient, smtp_server, status,
            kwargs.get('bounce_type', ''),
            kwargs.get('engagement_score', 0.0),
            kwargs.get('delivery_time', 0.0),
            kwargs.get('ip_reputation', 0.0),
            kwargs.get('domain_reputation', 0.0),
            kwargs.get('spam_score', 0.0),
            kwargs.get('auth_status', 'unknown')
        ))
        
        conn.commit()
        conn.close()
    
    def calculate_deliverability_score(self, campaign_id=None):
        """Calculate comprehensive deliverability score"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if campaign_id:
            cursor.execute('''
                SELECT delivery_status, ip_reputation, domain_reputation, 
                       spam_score, authentication_status
                FROM campaign_metrics WHERE campaign_id = ?
            ''', (campaign_id,))
        else:
            cursor.execute('''
                SELECT delivery_status, ip_reputation, domain_reputation, 
                       spam_score, authentication_status
                FROM campaign_metrics WHERE timestamp >= date('now', '-7 days')
            ''')
        
        results = cursor.fetchall()
        conn.close()
        
        if not results:
            return {"overall_score": 0, "recommendations": []}
        
   
        total_emails = len(results)
        delivered = sum(1 for r in results if r[0] == 'delivered')
        avg_ip_rep = sum(r[1] for r in results if r[1] > 0) / max(1, sum(1 for r in results if r[1] > 0))
        avg_domain_rep = sum(r[2] for r in results if r[2] > 0) / max(1, sum(1 for r in results if r[2] > 0))
        avg_spam_score = sum(r[3] for r in results if r[3] > 0) / max(1, sum(1 for r in results if r[3] > 0))
        auth_success = sum(1 for r in results if r[4] in ['pass', 'dkim_pass', 'spf_pass'])
        
  
        delivery_rate = (delivered / total_emails) * 100
        ip_score = min(avg_ip_rep * 20, 25)
        domain_score = min(avg_domain_rep * 20, 25)
        spam_score = max(25 - (avg_spam_score * 5), 0)
        auth_score = (auth_success / total_emails) * 25
        
        overall_score = delivery_rate * 0.4 + ip_score * 0.2 + domain_score * 0.2 + spam_score * 0.1 + auth_score * 0.1
        
     
        recommendations = []
        if delivery_rate < 85:
            recommendations.append("🚨 Low delivery rate - Check SMTP configuration and recipient list quality")
        if avg_ip_rep < 7:
            recommendations.append("📍 Poor IP reputation - Consider IP warming or new SMTP provider")
        if avg_domain_rep < 7:
            recommendations.append("🌐 Domain reputation issues - Implement SPF, DKIM, DMARC records")
        if avg_spam_score > 5:
            recommendations.append("⚠️ High spam score - Review email content and sender practices")
        if auth_success/total_emails < 0.8:
            recommendations.append("🔐 Authentication failures - Fix SPF/DKIM/DMARC setup")
        
        return {
            "overall_score": round(overall_score, 2),
            "delivery_rate": round(delivery_rate, 2),
            "ip_reputation": round(avg_ip_rep, 2),
            "domain_reputation": round(avg_domain_rep, 2),
            "spam_score": round(avg_spam_score, 2),
            "auth_success_rate": round((auth_success/total_emails)*100, 2),
            "recommendations": recommendations
        }
    
    def generate_deliverability_report(self, campaign_id=None, days=7):
        """Generate comprehensive deliverability report"""
        print(f"\n{Fore.CYAN}📊 DELIVERABILITY REPORT{Style.RESET_ALL}")
        print("=" * 60)
        
     
        metrics = self.calculate_deliverability_score(campaign_id)
        
      
        score = metrics["overall_score"]
        if score >= 85:
            color = Fore.GREEN
            status = "EXCELLENT"
        elif score >= 70:
            color = Fore.YELLOW
            status = "GOOD"
        else:
            color = Fore.RED
            status = "NEEDS IMPROVEMENT"
        
        print(f"Overall Deliverability Score: {color}{score}/100 ({status}){Style.RESET_ALL}")
        print()
        
     
        print("📈 Key Metrics:")
        print(f"   • Delivery Rate: {metrics['delivery_rate']}%")
        print(f"   • IP Reputation: {metrics['ip_reputation']}/10")
        print(f"   • Domain Reputation: {metrics['domain_reputation']}/10")
        print(f"   • Spam Score: {metrics['spam_score']}/10 (lower is better)")
        print(f"   • Authentication Success: {metrics['auth_success_rate']}%")
        print()
        
      
        if metrics["recommendations"]:
            print(f"{Fore.YELLOW}💡 Recommendations:{Style.RESET_ALL}")
            for rec in metrics["recommendations"]:
                print(f"   {rec}")
        else:
            print(f"{Fore.GREEN}✅ No critical issues detected!{Style.RESET_ALL}")
        
        print("=" * 60)
        
        return metrics
    
    def export_detailed_report(self, filename="deliverability_report.json"):
        """Export detailed report to JSON"""
        conn = sqlite3.connect(self.db_path)
        
    
        df = pd.read_sql_query('''
            SELECT * FROM campaign_metrics 
            WHERE timestamp >= date('now', '-30 days')
            ORDER BY timestamp DESC
        ''', conn)
        
        conn.close()
        
        if df.empty:
            print("No data available for report generation")
            return
        

        report = {
            "report_generated": datetime.datetime.now().isoformat(),
            "summary": self.calculate_deliverability_score(),
            "smtp_performance": df.groupby('smtp_server').agg({
                'delivery_status': lambda x: (x == 'delivered').mean(),
                'delivery_time': 'mean',
                'spam_score': 'mean'
            }).to_dict(),
            "domain_analysis": self._analyze_recipient_domains(df),
            "time_trends": self._analyze_time_trends(df),
            "bounce_analysis": df.groupby('bounce_type').size().to_dict()
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"{Fore.GREEN}📋 Detailed report exported to: {filename}{Style.RESET_ALL}")
        return report
    
    def _analyze_recipient_domains(self, df):
        """Analyze performance by recipient domain"""
        df['domain'] = df['recipient_email'].str.split('@').str[1]
        domain_stats = df.groupby('domain').agg({
            'delivery_status': lambda x: (x == 'delivered').mean(),
            'spam_score': 'mean',
            'recipient_email': 'count'
        }).round(3)
        return domain_stats.to_dict()
    
    def _analyze_time_trends(self, df):
        """Analyze delivery trends over time"""
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        time_trends = df.groupby('date').agg({
            'delivery_status': lambda x: (x == 'delivered').mean(),
            'spam_score': 'mean',
            'delivery_time': 'mean'
        }).round(3)
        return time_trends.to_dict()


class DeliverabilityTracker:
    def __init__(self):
        self.reporter = CampaignReporter()
        self.current_campaign_id = None
    
    def start_campaign_tracking(self, campaign_name):
        """Start tracking a new campaign"""
        self.current_campaign_id = f"{campaign_name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"{Fore.CYAN}📊 Campaign tracking started: {self.current_campaign_id}{Style.RESET_ALL}")
    
    def track_email_result(self, recipient, smtp_server, success, **kwargs):
        """Track individual email result"""
        status = 'delivered' if success else 'failed'
        self.reporter.log_email_attempt(
            self.current_campaign_id, recipient, smtp_server, status, **kwargs
        )
    
    def show_live_stats(self):
        """Show live campaign statistics"""
        if self.current_campaign_id:
            return self.reporter.generate_deliverability_report(self.current_campaign_id)