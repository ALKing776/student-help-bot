# Enhanced Student Help Bot - Professional Edition

## 🚀 Overview

A professional, enterprise-grade Telegram bot system for automated student help request detection and management. Features multi-account support, real-time analytics dashboard, advanced NLP processing, and comprehensive admin controls.

## ✨ Key Features

### 🤖 Core Functionality
- **Multi-Account Management**: Support for 20+ worker accounts with automatic load balancing
- **Advanced Message Analysis**: AI-powered NLP for detecting 10+ service types
- **Smart Routing**: Automatic forwarding of help requests to designated groups
- **Rate Limit Protection**: Built-in flood protection and account rotation

### 📊 Professional Dashboard
- **Real-time Monitoring**: Live statistics and performance metrics
- **Account Management**: View and control all worker accounts
- **User Analytics**: Track user behavior and engagement patterns
- **Service Insights**: Detailed analytics on service demand and trends
- **Configurable Alerts**: Automated alerting for system issues

### 🔧 Administration
- **Telegram Commands**: Full admin control through Telegram chat
- **Web Interface**: Professional dashboard for system management
- **User Management**: Blacklist/whitelist users with reason tracking
- **Configuration Management**: Dynamic configuration updates without restart

### 🛡️ Enterprise Features
- **Structured Logging**: Comprehensive logging with performance metrics
- **Database Persistence**: SQLite backend for all data storage
- **Security Controls**: Password-protected admin access
- **Scalable Architecture**: Designed for high-volume operations

## 🏗️ System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │   Main Bot       │    │   Dashboard     │
│   Network       │◄──►│   Controller     │◄──►│   Interface     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│ Account Manager │    │ Message Analyzer │    │ Analytics       │
│ (20+ accounts)  │    │ (AI/NLP Engine)  │    │ (Statistics)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
        │                     │                     │
        ▼                     ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                         Database Layer                          │
│                    (SQLite with ORM Models)                     │
└─────────────────────────────────────────────────────────────────┘
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- Telegram API credentials
- Target group for forwarding

### Quick Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. **Required Configuration**
```env
# Telegram API (from https://my.telegram.org)
API_ID=your_api_id
API_HASH=your_api_hash
PHONE=+1234567890

# Target group for forwarding
TARGET_GROUP_ID=-1001234567890

# Admin users (comma-separated Telegram IDs)
ADMIN_USER_IDS=123456789,987654321

# Dashboard settings
DASHBOARD_PASSWORD=admin123
DASHBOARD_PORT=5000
```

4. **Run the Bot**
```bash
python enhanced_bot.py
```

5. **Access Dashboard**
- Open `http://localhost:5000` in your browser
- Login with your dashboard password

## 🎯 Usage Guide

### Telegram Admin Commands

| Command | Description | Usage |
|---------|-------------|-------|
| `/stats` | System statistics | `/stats` |
| `/accounts` | Account management | `/accounts` |
| `/users` | User management | `/users` |
| `/blacklist <user_id>` | Block user | `/blacklist 123456789` |
| `/whitelist <user_id>` | Allow user | `/whitelist 123456789` |
| `/config` | View configuration | `/config` |
| `/config <key> <value>` | Update setting | `/config min_delay 1.0` |
| `/analyze <text>` | Test message analysis | `/analyze Need help with math homework` |
| `/addaccount <phone> <api_id> <api_hash>` | Add worker account | `/addaccount +1234567890 1234567 abcdef123456` |
| `/help` | Show all commands | `/help` |

### Web Dashboard Features

1. **Dashboard Tab**: Real-time system overview
2. **Accounts Tab**: Manage worker accounts
3. **Users Tab**: Monitor user activity
4. **Services Tab**: Service analytics and trends
5. **Reports Tab**: Generate exportable reports
6. **Config Tab**: Update system settings

## 📊 Supported Services

The bot detects requests for these student services:

- 📚 **شرح** - Explanation and tutoring
- 📝 **تقارير** - Reports and summaries  
- 📖 **واجبات** - Homework and assignments
- 📊 **عروض** - Presentations and slides
- 🎨 **تصاميم** - Designs and graphics
- 🗺️ **خرائط** - Mind maps and diagrams
- 🎓 **ماجستير** - Master's theses
- 🎯 **تخرج** - Graduation projects
- 🏥 **طبي** - Medical reports
- 📄 **ريبورت** - Various reports

## 🔧 Configuration Options

### Core Settings
- `MIN_DELAY` / `MAX_DELAY`: Random delay range (seconds)
- `CONFIDENCE_THRESHOLD`: Minimum confidence to forward (0-100)
- `MESSAGES_PER_HOUR_LIMIT`: Rate limiting per account
- `BLACKLIST_ENABLED`: Enable user blacklisting
- `WHITELIST_ENABLED`: Enable user whitelisting

### Dashboard Settings
- `DASHBOARD_PORT`: Web interface port
- `DASHBOARD_HOST`: Binding address
- `DASHBOARD_PASSWORD`: Admin password

### Account Management
- `ACCOUNT_ROTATION_DELAY`: Delay between account switches
- `FLOOD_WAIT_MULTIPLIER`: Flood wait handling multiplier

## 🛡️ Security Features

- **Password Protection**: Dashboard access control
- **Admin Authorization**: Whitelisted Telegram user IDs
- **Rate Limiting**: Automatic flood protection
- **Session Management**: Secure session handling
- **Audit Logging**: Complete activity tracking

## 📈 Performance Monitoring

### Real-time Metrics
- Messages processed per minute
- Account utilization rates
- Success/error ratios
- Response time measurements
- Service popularity trends

### Alert System
- High error rate detection
- Account connectivity issues
- Performance degradation alerts
- Configuration change notifications

## 🚀 Scaling Guide

### For 20+ Accounts:
1. **Hardware Requirements**: 4GB RAM minimum
2. **Network**: Stable internet connection
3. **Storage**: 10GB+ for database growth
4. **Monitoring**: Regular performance checks

### Best Practices:
- Distribute accounts across different phone numbers
- Monitor rate limits and adjust delays
- Regular database maintenance
- Backup configuration regularly

## 🔧 Troubleshooting

### Common Issues:

**Bot won't start:**
- Check API credentials in `.env`
- Verify phone number format (+country code)
- Ensure target group ID is correct

**Dashboard not accessible:**
- Check if port 5000 is available
- Verify firewall settings
- Confirm dashboard password

**Accounts disconnecting:**
- Check internet connectivity
- Review rate limiting settings
- Monitor Telegram API limits

**Low detection accuracy:**
- Adjust confidence threshold
- Review service keywords
- Check message quality filters

## 📚 API Documentation

### Internal APIs:
- **Analytics API**: `/api/stats`, `/api/services`
- **Account API**: `/api/accounts`
- **User API**: `/api/users`
- **Config API**: `/api/config`

### WebSocket Events:
- `stats_update`: Real-time statistics
- `accounts_update`: Account status changes
- `alerts`: System alerts and notifications

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the documentation
- Review logs in `bot.log`
- Contact system administrator

---

**Enhanced Student Help Bot v2.0** - Professional Automation Solution