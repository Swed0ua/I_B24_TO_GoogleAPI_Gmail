# I_B24_TO_GoogleAPI_Gmail - Setup and Autostart Guide

## Overview
Integration service for SmartKasa connecting Gmail, Bitrix24, and Google Sheets. Processes emails from banks (Oschadbank, A-Bank, SmartKasa) and creates deals in Bitrix24 CRM.

## Files
- Main entry point: `main.py`
- Configuration: `config.py` (reads from `.env`)
- Gmail API: `connect_to_gapi.py`
- Bitrix24 API: `connect_to_crm.py`
- Google Sheets: `connect_to_gsheets.py`
- Email parsing: `functions.py`

---

## Linux/Unix Autostart Setup

### 1. Create systemd service file

```bash
sudo nano /etc/systemd/system/AC_Gmail_B24_Integration.service
```

### 2. Service file content

**Note**: Update paths below with your actual project directory.

```ini
[Unit]
Description=Gmail to Bitrix24 Integration Service
After=network.target
Wants=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/path/to/I_B24_TO_GoogleAPI_Gmail
Environment=PATH=/path/to/I_B24_TO_GoogleAPI_Gmail/venv/bin
Environment=PYTHONPATH=/path/to/I_B24_TO_GoogleAPI_Gmail
ExecStart=/path/to/I_B24_TO_GoogleAPI_Gmail/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=AC_Gmail_B24_Integration

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=/path/to/I_B24_TO_GoogleAPI_Gmail

[Install]
WantedBy=multi-user.target
```

### 3. Initialize and enable service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable autostart
sudo systemctl enable AC_Gmail_B24_Integration

# Start service
sudo systemctl start AC_Gmail_B24_Integration

# Check status
sudo systemctl status AC_Gmail_B24_Integration
```

---

## Service Management Commands

### Start service
```bash
sudo systemctl start AC_Gmail_B24_Integration
```

### Stop service
```bash
sudo systemctl stop AC_Gmail_B24_Integration
```

### Restart service
```bash
sudo systemctl restart AC_Gmail_B24_Integration
```

### Check status
```bash
sudo systemctl status AC_Gmail_B24_Integration
```

### View logs
```bash
# Follow logs in real-time
sudo journalctl -u AC_Gmail_B24_Integration -f

# View last 50 log entries
sudo journalctl -u AC_Gmail_B24_Integration -n 50

# View all logs
sudo journalctl -u AC_Gmail_B24_Integration
```

---

## Verification

### Check if process is running
```bash
ps aux | grep "python main.py"
```

### Check process status
```bash
systemctl is-active AC_Gmail_B24_Integration
```

### List all services
```bash
sudo systemctl list-units --type=service
```

---

## Manual Start (Development)

```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Ensure .env file exists with proper configuration
# Copy from env_template.txt if needed

# Run the service
python main.py
```

---

## Environment Configuration

Create `.env` file with the following variables (copy from `env_template.txt`):

```env
BITRIX24_WEBHOOK_URL=your_b24_webhook
BITRIX24_PROFILE_URL=your_b24_profile_url

TG_BOT_TOKEN=your_telegram_bot_token
TG_BOT2_TOKEN=your_telegram_bot2_token

GROUP_ID=your_telegram_group_id
GROUP2_ID=your_telegram_group2_id
GROUP2_THREAD_ID=your_thread_id
GROUP_CASH_REGISTER_ID=your_cash_register_group_id
GROUP_THAYAVKA_ID=your_thayavka_group_id

GROUP_PUMB_ID=your_pumb_group_id
GROUP_RAIFF_ID=your_raiff_group_id
GROUP_OKSI_ID=your_oksi_group_id
GROUP_PIVDENNUY_ID=your_pivdennuY_group_id
GROUP_OSCHAD_ID=your_oschad_group_id
GROUP_ABANK_ID=your_abank_group_id
GROUP_VOSTOK_ID=your_vostok_group_id

GOOGLE_SHEETS_OSCHAD_ID=your_oschad_sheet_id
GOOGLE_SHEETS_OSCHAD_RANGE=Лист1
GOOGLE_SHEETS_ABANK_ID=your_abank_sheet_id
GOOGLE_SHEETS_ABANK_RANGE=Лист1
```

---

## Required Files

- `client_secret.json` - Google OAuth credentials for Gmail API access
- `cred.json` - Google Service Account credentials for Google Sheets API
- `token.pickle` - Generated after first Gmail OAuth authentication
- `.env` - Environment variables configuration

---

## How It Works

1. Connects to Gmail API and checks for unread emails
2. Parses emails from different sources (banks, SmartKasa)
3. Creates contacts in Bitrix24 if not exist
4. Creates deals in Bitrix24 with parsed information
5. Appends data to Google Sheets for reporting !!! temporarily stoped
6. Sends notifications to Telegram channels
7. Marks emails as read
8. Runs in loop with 60 seconds interval

