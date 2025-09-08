import re
import requests
from urllib.parse import urlparse
import dns.resolver
import hashlib
from datetime import datetime
import random

class ContentBestPractices:
    PROFESSIONAL_SUBJECTS = [
        "Important Account Update",
        "Your Account Verification Required", 
        "Security Alert - Action Required",
        "Account Status Notification",
        "Important Information Regarding Your Account",
        "Urgent: Please Verify Your Details",
        "Account Security Notice",
        "Action Required: Account Verification",
        "Important Update for Your Records",
        "Please Confirm Your Account Details"
    ]
    def __init__(self):
        self.spam_keywords = [
            'free money', 'click here', 'urgent', 'act now', 'limited time',
            'guarantee', 'no obligation', 'risk free', 'cash bonus',
            'make money fast', 'work from home', 'urgent response required',
            'congratulations', 'you have won', 'claim now', 'call now',
            'dont delete', 'increase sales', 'million dollars', 'prize',
            '100% free', 'accept credit cards', 'additional income',
            'be your own boss', 'best price', 'big bucks', 'billing',
            'cancel at any time', 'cant live without', 'consolidate debt',
            'credit bureaus', 'dear friend', 'eliminate bad credit',
            'fantastic deal', 'financial freedom', 'get out of debt',
            'home based', 'incredible deal', 'investment decision',
            'make $', 'marketing solutions', 'money back', 'once in lifetime',
            'order today', 'pure profit', 'refinance home', 'remove debt',
            'serious cash', 'stop snoring', 'university diplomas',
            'while you sleep', 'winner', 'work at home'
        ]
        
        self.image_text_ratio_threshold = 0.6  # 60% text minimum
        self.professional_subjects = self.PROFESSIONAL_SUBJECTS
        
    def analyze_content_quality(self, html_content, subject):
        """Comprehensive content analysis for deliverability"""
        score = 100
        issues = []
        
    
        subject_score, subject_issues = self._analyze_subject_line(subject)
        score += subject_score
        issues.extend(subject_issues)
        
    
        content_score, content_issues = self._analyze_html_content(html_content)
        score += content_score
        issues.extend(content_issues)
        
      
        score = max(0, min(100, score))
        
        return {
            'score': score,
            'grade': self._get_grade(score),
            'issues': issues,
            'recommendations': self._get_recommendations(issues)
        }
    
    def _analyze_subject_line(self, subject):
        """Analyze subject line for spam indicators"""
        score = 0
        issues = []
        
        
        if len(subject) < 20:
            score -= 10
            issues.append("Subject too short (under 20 chars)")
        elif len(subject) > 70:
            score -= 15
            issues.append("Subject too long (over 70 chars)")
        
       
        if subject.count('!') > 1:
            score -= 20
            issues.append("Multiple exclamation marks in subject")
        
     
        if subject.isupper() and len(subject) > 5:
            score -= 25
            issues.append("Subject line is all caps")
        
    
        subject_lower = subject.lower()
        spam_found = [word for word in self.spam_keywords if word in subject_lower]
        if spam_found:
            score -= len(spam_found) * 15
            issues.append(f"Spam keywords in subject: {', '.join(spam_found[:3])}")
        
 
        if re.search(r'[0-9]{4,}', subject):
            score -= 10
            issues.append("Long number sequences in subject")
        
        return score, issues
    
    def _analyze_html_content(self, html_content):
        """Analyze HTML content for deliverability issues"""
        score = 0
        issues = []
        
     
        text_content = re.sub(r'<[^>]+>', '', html_content)
        text_length = len(text_content.strip())
        html_length = len(html_content)
        
        if html_length > 0:
            text_ratio = text_length / html_length
            if text_ratio < 0.1:
                score -= 30
                issues.append("Very low text-to-HTML ratio")
            elif text_ratio < 0.3:
                score -= 15
                issues.append("Low text-to-HTML ratio")
        
       
        img_tags = re.findall(r'<img[^>]*>', html_content, re.IGNORECASE)
        if len(img_tags) > 10:
            score -= 20
            issues.append("Too many images (over 10)")
        
    
        missing_alt = len(re.findall(r'<img(?![^>]*alt=)[^>]*>', html_content, re.IGNORECASE))
        if missing_alt > 0:
            score -= 10
            issues.append(f"{missing_alt} images missing alt text")
        
   
        links = re.findall(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>', html_content, re.IGNORECASE)
        
      
        suspicious_domains = 0
        for link in links:
            if self._is_suspicious_url(link):
                suspicious_domains += 1
        
        if suspicious_domains > 0:
            score -= suspicious_domains * 15
            issues.append(f"{suspicious_domains} suspicious URLs detected")
     
        shorteners = ['bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'short.link']
        shortener_count = sum(1 for link in links if any(shortener in link for shortener in shorteners))
        if shortener_count > 0:
            score -= shortener_count * 10
            issues.append(f"{shortener_count} URL shorteners found")
        

        content_lower = html_content.lower()
        spam_found = [word for word in self.spam_keywords if word in content_lower]
        if spam_found:
            score -= len(spam_found) * 5
            issues.append(f"Spam keywords in content: {len(spam_found)} found")
        
     
        unsubscribe_patterns = [
            r'unsubscribe',
            r'opt.out',
            r'remove.*list',
            r'update.*preferences'
        ]
        
        has_unsubscribe = any(re.search(pattern, html_content, re.IGNORECASE) 
                             for pattern in unsubscribe_patterns)
        
        if not has_unsubscribe:
            score -= 25
            issues.append("No unsubscribe mechanism found")
        
        return score, issues
    
    def _is_suspicious_url(self, url):
        """Check if URL appears suspicious"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
         
            if re.match(r'\d+\.\d+\.\d+\.\d+', domain):
                return True
            
       
            suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.cc', '.ws', '.info']
            if any(domain.endswith(tld) for tld in suspicious_tlds):
                return True
            

            if domain.count('.') > 3:
                return True
            
            return False
        except:
            return True
    
    def optimize_content(self, html_content, subject):
        """Apply automatic optimizations to improve deliverability"""
        optimized_html = html_content
        optimized_subject = subject
        
 
        def add_alt_text(match):
            img_tag = match.group(0)
            if 'alt=' not in img_tag.lower():
                return img_tag[:-1] + ' alt="Image">'
            return img_tag
        
        optimized_html = re.sub(r'<img[^>]*>', add_alt_text, optimized_html, flags=re.IGNORECASE)
        

        if not re.search(r'unsubscribe', optimized_html, re.IGNORECASE):
            unsubscribe_html = '''
            <div style="font-size: 12px; color: #666; margin-top: 20px; text-align: center;">
                <a href="##UNSUBSCRIBE_URL##" style="color: #666;">Unsubscribe</a> | 
                <a href="##PREFERENCES_URL##" style="color: #666;">Update Preferences</a>
            </div>
            '''
            optimized_html += unsubscribe_html
        

        text_content = re.sub(r'<[^>]+>', '', optimized_html)
        if len(text_content.strip()) < 100:
            additional_text = '''
            <div style="font-size: 14px; line-height: 1.6; margin: 20px 0;">
                <p>This message was sent to you because you opted in to receive updates from our service. 
                We respect your privacy and will never share your information with third parties.</p>
            </div>
            '''
            optimized_html += additional_text
        
        return optimized_html, optimized_subject
    
    def _get_grade(self, score):
        """Convert score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def _get_recommendations(self, issues):
        """Generate recommendations based on issues found"""
        recommendations = []
        
        if any('subject' in issue.lower() for issue in issues):
            recommendations.append("Optimize subject line: Keep 30-50 chars, avoid spam words, limit punctuation")
        
        if any('image' in issue.lower() for issue in issues):
            recommendations.append("Add alt text to all images and reduce image count if excessive")
        
        if any('ratio' in issue.lower() for issue in issues):
            recommendations.append("Increase text content to improve text-to-HTML ratio")
        
        if any('unsubscribe' in issue.lower() for issue in issues):
            recommendations.append("Add clear unsubscribe link in footer")
        
        if any('spam' in issue.lower() or 'keyword' in issue.lower() for issue in issues):
            recommendations.append("Remove or replace spam trigger words with alternatives")
        
        if any('url' in issue.lower() or 'link' in issue.lower() for issue in issues):
            recommendations.append("Use reputable domains and avoid URL shorteners")
        
        return recommendations
    
    def generate_content_variations(self, base_content, variations_count=3):
        """Generate content variations to avoid content fingerprinting"""
        variations = []
        
        for i in range(variations_count):
            varied_content = base_content
            

            varied_content = self._vary_formatting(varied_content, i)
            

            varied_content = self._add_invisible_variations(varied_content, i)
            
            variations.append(varied_content)
        
        return variations
    
    def _vary_formatting(self, content, variation_num):
        """Slightly vary HTML formatting"""
    
        content = re.sub(r'(<[^>]+>)', lambda m: self._add_random_spaces(m.group(1)), content)
        

        content = re.sub(r'<(\w+)([^>]*)>', self._randomize_attributes, content)
        
        return content
    
    def _add_random_spaces(self, tag):
        """Add random spaces in HTML tags"""
        if random.random() < 0.3:  
            return tag.replace('>', ' >')
        return tag
    
    def _randomize_attributes(self, match):
        """Randomize attribute order in HTML tags"""
        tag_name = match.group(1)
        attrs = match.group(2).strip()
        
        if not attrs:
            return f'<{tag_name}>'
        

        return f'<{tag_name}{attrs}>'
    
    def _add_invisible_variations(self, content, variation_num):
        """Add invisible HTML comments for variation"""
        comments = [
            f'<!-- v{variation_num} -->',
            f'<!-- generated: {datetime.now().strftime("%Y%m%d%H%M%S")} -->',
            f'<!-- hash: {hashlib.md5(str(variation_num).encode()).hexdigest()[:8]} -->'
        ]
        

        comment = random.choice(comments)
        insert_pos = content.find('<body')
        if insert_pos != -1:
            insert_pos = content.find('>', insert_pos) + 1
            content = content[:insert_pos] + comment + content[insert_pos:]
        
        return content

ContentOptimizer = ContentBestPractices
