 Core Email Sending Features

**SMTP Management:**
- Multiple SMTP server support with automatic rotation
- SMTP server authentication and verification
- Support for both SSL (port 465) and TLS (port 587) connections
- Configuration loading from `smtp.txt` file with format validation

**Email Composition:**
- HTML email template support (.html, .htm, .svg files)
- Dynamic placeholder processing in email content
- Countdown timer placeholders (##COUNTDOWN[hours]##) 
- Professional email headers (Message-ID, Reply-To, Date formatting)
- MIME multipart message creation
- Subject line randomization from predefined options

**Campaign Management:**
- Sequential email sending (one at a time)
- Mass email campaigns with progress tracking
- Email list loading from text files
- Template selection (random or specific)
- Real-time campaign statistics and success rate tracking

## Advanced Features

**Email Validation & Quality Control:**
- Email format validation before sending
- Content spam risk analysis and scoring
- Automatic subject line optimization for high-risk content
- Domain reputation checking capabilities

**Delivery Optimization:**
- Intelligent sending delays between emails
- SMTP throttling management based on server performance
- Retry logic for failed sends with recommended delays
- Response time monitoring and optimization

**Authentication & Security:**
- DKIM message signing support
- Email authentication management
- Robust error handling and troubleshooting

**Monitoring & Analytics:**
- Real-time delivery monitoring
- Bounce rate tracking
- SMTP server performance analytics
- Alert system for delivery issues
- Detailed error reporting with categorization

**User Experience:**
- Colorized console output with status indicators
- Real-time countdown timer before sending
- Detailed sending progress with email-by-email breakdown
- Campaign completion summaries with statistics
- Professional banner and branding

**Configuration Options:**
- Customizable countdown timers (default 3.8 seconds)
- Directory structure auto-creation
- Advanced configuration loading
- Support contact integration

This is a comprehensive bulk email sender designed for marketing campaigns with enterprise-level features for deliverability, monitoring, and campaign management.
