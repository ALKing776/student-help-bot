# 🚀 Enhanced Student Help Bot - Complete Deployment Guide

## 📋 System Requirements

### Minimum Requirements:
- **Operating System**: Windows 10/11, Linux, macOS
- **Python Version**: 3.8 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 10GB free space
- **Internet**: Stable broadband connection

### Recommended Specifications:
- **RAM**: 8GB or more
- **CPU**: Dual-core processor or better
- **Storage**: SSD drive for better performance
- **Network**: High-speed internet connection

## 🔧 Installation Steps

### Step 1: Python Environment Setup

```bash
# Check Python version
python --version

# If Python < 3.8, download from python.org
# Make sure to check "Add Python to PATH" during installation
```

### Step 2: Clone/Download Project Files

```bash
# If using git:
git clone <repository_url>
cd student-help-bot

# Or extract downloaded files to a folder
```

### Step 3: Install Dependencies

```bash
# Navigate to project directory
cd path/to/project_review

# Install all required packages
pip install -r requirements.txt

# If you encounter issues, try:
pip install --upgrade pip
pip install -r requirements.txt --user
```

### Step 4: Telegram API Configuration

1. **Visit** [https://my.telegram.org](https://my.telegram.org)
2. **Login** with your phone number
3. **Navigate** to "API development tools"
4. **Create** new application:
   - App title: Student Help Bot
   - Short name: studenthelp
   - Platform: Desktop
   - Description: (optional)
5. **Copy** the following credentials:
   - `API_ID`
   - `API_HASH`

### Step 5: Environment Configuration

Create a `.env` file in the project root:

```env
# Telegram API Credentials (REQUIRED)
API_ID=35642926
API_HASH=0cd70e1767672f72c3a1c612e87fdabc
PHONE=+966599909300

# Target Group Configuration (REQUIRED)
TARGET_GROUP_ID=5777020145

# Admin Configuration (REQUIRED)
ADMIN_USER_IDS=8533481274

# Dashboard Settings
DASHBOARD_PASSWORD=admin123
DASHBOARD_PORT=5000
DASHBOARD_HOST=0.0.0.0

# Processing Settings
CONFIDENCE_THRESHOLD=70.0
MESSAGES_PER_HOUR_LIMIT=100
BLACKLIST_ENABLED=true
WHITELIST_ENABLED=false

# Multi-Account Settings
ACCOUNT_ROTATION_DELAY=5.0
FLOOD_WAIT_MULTIPLIER=1.5

# Timing Configuration
MIN_DELAY=0.5
MAX_DELAY=3.0
ENABLE_LOGGING=true
```

### Step 6: Get Required IDs

#### Target Group ID:
1. Add `@userinfobot` to your target group
2. Send `/start` in the group
3. Copy the Chat ID (should be negative number like `-1001234567890`)

#### Your User ID:
1. Message `@userinfobot` directly
2. Send `/start`
3. Copy your User ID

## ▶️ Running the Bot

### Method 1: Direct Execution
```bash
# Windows
python enhanced_bot.py

# Linux/macOS
python3 enhanced_bot.py
```

### Method 2: Using Startup Scripts
```bash
# Windows
start.bat

# Linux/macOS
chmod +x start.sh
./start.sh
```

### Method 3: Background Process
```bash
# Windows (using PowerShell)
Start-Process python -ArgumentList "enhanced_bot.py" -WindowStyle Hidden

# Linux/macOS (using screen)
screen -S help_bot
python enhanced_bot.py
# Press Ctrl+A, then D to detach

# Linux/macOS (using nohup)
nohup python enhanced_bot.py > bot.log 2>&1 &
```

## 🖥️ Accessing the Dashboard

Once the bot is running:

1. **Open Browser**: Navigate to `http://localhost:5000`
2. **Login**: Enter your `DASHBOARD_PASSWORD` (default: `admin123`)
3. **Features Available**:
   - Real-time statistics
   - Account management
   - User analytics
   - Service trends
   - Configuration updates

## 📱 Telegram Admin Commands

In any chat with the bot, use these commands:

| Command | Description | Usage |
|---------|-------------|-------|
| `/stats` | System statistics | `/stats` |
| `/accounts` | Account management | `/accounts` |
| `/users` | User activity | `/users` |
| `/blacklist <user_id>` | Block user | `/blacklist 123456789` |
| `/whitelist <user_id>` | Allow user | `/whitelist 123456789` |
| `/config` | View configuration | `/config` |
| `/config <key> <value>` | Update setting | `/config min_delay 1.0` |
| `/analyze <text>` | Test message analysis | `/analyze Need help with math` |
| `/addaccount <phone> <api_id> <api_hash>` | Add worker account | `/addaccount +1234567890 1234567 abcdef123456` |
| `/help` | Show all commands | `/help` |

## 🛠️ Multi-Account Setup

To add additional worker accounts:

### Method 1: Through Telegram Commands
```
/addaccount +1234567890 1234567 abcdef1234567890 worker1
```

### Method 2: Manual Database Entry
```sql
INSERT INTO accounts (username, phone, api_id, api_hash, session_file)
VALUES ('worker1', '+1234567890', 1234567, 'abcdef1234567890', 'sessions/worker1');
```

## 🔍 Monitoring and Maintenance

### Log Files
```bash
# Main log file
cat bot.log

# Real-time monitoring
tail -f bot.log

# Error filtering
grep "ERROR" bot.log
```

### Database Management
```bash
# Check database size
du -h bot_database.db

# Database backup
cp bot_database.db bot_database_backup.db

# Database inspection
sqlite3 bot_database.db ".tables"
```

### Performance Monitoring
```bash
# Check system resources
htop  # or top on macOS
ps aux | grep python

# Network monitoring
netstat -tulpn | grep :5000
```

## 🚨 Troubleshooting Guide

### Common Issues and Solutions

#### 1. "Module not found" Errors
```bash
# Solution:
pip install -r requirements.txt --upgrade
pip install --force-reinstall package_name
```

#### 2. Telegram Authentication Issues
```bash
# Solution:
# - Verify API_ID and API_HASH in .env
# - Check phone number format (+country code)
# - Delete session files and re-authenticate
rm *.session*
```

#### 3. Database Connection Problems
```bash
# Solution:
# - Check disk space
# - Verify file permissions
# - Recreate database: rm bot_database.db
```

#### 4. Dashboard Not Accessible
```bash
# Solution:
# - Check if port 5000 is available
# - Verify DASHBOARD_HOST setting
# - Check firewall settings
netstat -tulpn | grep :5000
```

#### 5. Unicode Encoding Issues (Windows)
```bash
# Solution:
# Add to .env file:
PYTHONIOENCODING=utf-8
```

#### 6. Rate Limiting Problems
```bash
# Solution:
# - Increase delays in config
# - Reduce MESSAGES_PER_HOUR_LIMIT
# - Add more worker accounts
```

## 🔒 Security Best Practices

### 1. Credential Security
- Never share your `.env` file
- Use strong dashboard passwords
- Regular credential rotation
- Enable two-factor authentication on Telegram

### 2. Network Security
- Use VPN for sensitive operations
- Restrict dashboard access by IP
- Keep software updated
- Monitor for suspicious activity

### 3. Data Protection
- Regular database backups
- Encrypt sensitive data
- Implement access logging
- Review permissions regularly

## 📊 Performance Optimization

### 1. Resource Management
```bash
# Optimize database
sqlite3 bot_database.db "VACUUM;"
sqlite3 bot_database.db "ANALYZE;"

# Clean old logs
find . -name "*.log" -mtime +7 -delete
```

### 2. Configuration Tuning
```env
# For high-volume operations:
MESSAGES_PER_HOUR_LIMIT=200
MIN_DELAY=1.0
MAX_DELAY=5.0
ACCOUNT_ROTATION_DELAY=10.0
```

### 3. Scaling Recommendations
- **Small scale** (1-5 accounts): Current setup sufficient
- **Medium scale** (6-20 accounts): Add more RAM (8GB+)
- **Large scale** (20+ accounts): Consider dedicated server/VPS

## ☁️ Cloud Deployment Options

### Option 1: DigitalOcean Droplet
```bash
# Create Ubuntu 20.04 droplet
# SSH into server
ssh root@your_droplet_ip

# Install dependencies
apt update && apt upgrade -y
apt install python3 python3-pip git -y

# Deploy bot
git clone your_repository
cd student-help-bot
pip3 install -r requirements.txt
```

### Option 2: AWS EC2
```bash
# Launch EC2 instance (t3.medium recommended)
# Connect via SSH
# Follow same installation steps as above
```

### Option 3: Heroku (Limited)
```bash
# Create Heroku account
# Install Heroku CLI
heroku create your-bot-name
git push heroku main
```

## 🔄 Update and Maintenance

### Regular Maintenance Tasks
```bash
# Weekly:
# - Check logs for errors
# - Backup database
# - Update dependencies
pip install -r requirements.txt --upgrade

# Monthly:
# - Review user activity
# - Optimize database
# - Update Telegram sessions
# - Check system resources
```

### Updating the Bot
```bash
# Backup current installation
cp -r project_review project_review_backup

# Update code
git pull origin main
# or download new version

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart bot
pkill -f enhanced_bot.py
python enhanced_bot.py
```

## 📞 Support Resources

### Documentation Files:
- `README_ENHANCED.md` - Enhanced features documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical implementation details
- `FINAL_PROJECT_SUMMARY.md` - Complete project overview
- `test_enhanced.py` - Integration test suite

### Community Support:
- Check GitHub issues
- Review project documentation
- Contact system administrator

---

**🎉 Congratulations! Your Enhanced Student Help Bot is ready for deployment!**

Remember to:
1. Keep your credentials secure
2. Monitor system performance
3. Regular maintenance and updates
4. Backup important data regularly