class DeliveryabilityMonitor:
    """Monitor email deliverability metrics"""
    def __init__(self):
        self.metrics = {
            'sent': 0,
            'delivered': 0,
            'bounced': 0,
            'opens': 0,
            'clicks': 0
        }
    
    def track_delivery(self, email_data):
        """Track email delivery status"""
        self.metrics['sent'] += 1
        return True
    
    def get_metrics(self):
        """Get deliverability metrics"""
        return self.metrics.copy()
    
    def record_bounce(self, email):
        """Record email bounce"""
        self.metrics['bounced'] += 1
    
    def record_delivery(self, email):
        """Record successful delivery"""
        self.metrics['delivered'] += 1

class RealTimeAlerts:
    """Handle real-time email alerts"""
    def __init__(self, monitor=None):
        self.monitor = monitor
        self.alert_thresholds = {
            'bounce_rate': 0.05,  # 5%
            'spam_rate': 0.01     # 1%
        }
    
    def send_alert(self, message):
        """Send real-time alert"""
        print(f"ALERT: {message}")
    
    def configure_alerts(self, settings):
        """Configure alert settings"""
        self.alert_thresholds.update(settings)
    
    def check_thresholds(self):
        """Check if metrics exceed thresholds"""
        if not self.monitor:
            return
        
        metrics = self.monitor.get_metrics()
        if metrics['sent'] > 0:
            bounce_rate = metrics['bounced'] / metrics['sent']
            if bounce_rate > self.alert_thresholds['bounce_rate']:
                self.send_alert(f"High bounce rate detected: {bounce_rate:.2%}")
