# 🚀 Quick Start Guide - Enhanced Student Help Bot

## 📋 5-Minute Setup

### Step 1: Install Dependencies (2 minutes)
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 minute)
Edit your `.env` file with these essential settings:
```env
API_ID=35642926
API_HASH=0cd70e1767672f72c3a1c612e87fdabc
PHONE=+966599909300
TARGET_GROUP_ID=5777020145
ADMIN_USER_IDS=8533481274
```

### Step 3: Run the Bot (1 minute)
```bash
python enhanced_bot.py
```

### Step 4: Access Dashboard (1 minute)
Open your browser to: `http://localhost:5000`

## 🎯 Immediate Usage

### Telegram Commands (Available now):
- `/stats` - View system statistics
- `/help` - Show all available commands
- `/analyze <message>` - Test message detection

### Web Dashboard Features:
- Real-time monitoring
- Account management
- User analytics
- Configuration updates

## 📱 Getting Required IDs

### Target Group ID:
1. Add `@userinfobot` to your group
2. Send `/start`
3. Copy the Chat ID

### Your User ID:
1. Message `@userinfobot` directly
2. Send `/start`
3. Copy your User ID

## ⚡ Quick Tips

- **First Run**: The bot will ask for Telegram verification code
- **Dashboard**: Default password is `admin123`
- **Logs**: Check `bot.log` for detailed information
- **Support**: See `DEPLOYMENT_GUIDE.md` for comprehensive documentation

## 🛠️ Troubleshooting

**Common Issues:**
- Module not found → `pip install -r requirements.txt`
- Authentication failed → Check `.env` credentials
- Port busy → Change `DASHBOARD_PORT` in `.env`

**Need Help?**
- Check `bot.log` file
- Review `DEPLOYMENT_GUIDE.md`
- Run `python test_enhanced.py` for diagnostics

---

**Your enhanced bot is ready to automate student help requests! 🎉**