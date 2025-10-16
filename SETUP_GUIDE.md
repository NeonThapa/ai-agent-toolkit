# 🚀 Personalized Learning System - Setup Guide

## 📋 Overview

This system automatically:
1. Analyzes student assessment data
2. Generates personalized study guides using RAG
3. Emails PDFs to students who need support

---

## 🔧 Step 1: Gmail Setup (5 minutes)

### Create App Password for Gmail

1. **Go to Google Account Settings**
   - Visit: https://myaccount.google.com/

2. **Enable 2-Factor Authentication** (if not already enabled)
   - Security → 2-Step Verification → Turn On

3. **Generate App Password**
   - Security → App Passwords
   - Select App: "Mail"
   - Select Device: "Other" (enter "Tata Strive")
   - Click "Generate"
   - Copy the 16-character password

4. **Update .env file**
   ```bash
   EMAIL_SENDER_ADDRESS="your.facilitator.email@gmail.com"
   EMAIL_SENDER_PASSWORD="xxxx xxxx xxxx xxxx"  # 16-char app password
   EMAIL_SENDER_NAME="Tata Strive Learning Team"
   ```

---

## 📦 Step 2: Install Dependencies

```bash
# Activate your conda environment
conda activate rag_env

# Install new packages
pip install pandas openpyxl

# Verify installation
python -c "import pandas; import openpyxl; print('✅ All packages installed')"
```

---

## 🔄 Step 3: Update Files

### 1. Replace `main.py`
```bash
cd ~/rag_api
cp main.py main_backup_old.py  # Backup
# Copy new main.py content from artifact
nano main.py
# Paste the complete new content
# Save: Ctrl+O, Enter, Ctrl+X
```

### 2. Replace `frontend_app.py`
```bash
cp frontend_app.py frontend_backup_old.py  # Backup
nano frontend_app.py
# Paste the complete new content
# Save: Ctrl+O, Enter, Ctrl+X
```

### 3. Update `requirements.txt`
```bash
nano requirements.txt
# Add these lines:
pandas
openpyxl
streamlit
# Save: Ctrl+O, Enter, Ctrl+X
```

---

## ✅ Step 4: Test the System

### 1. Start Backend
```bash
cd ~/rag_api
conda activate rag_env
python main.py
```

You should see:
```
Initializing Pinecone...
✅ Pinecone index connection established.
✅ Metadata loaded successfully.
Starting Tata Strive RAG API Server...
* Running on http://127.0.0.1:8081
```

### 2. Start Frontend (New Terminal)
```bash
conda activate rag_env
cd ~/rag_api
python -m streamlit run frontend_app.py
```

You should see:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### 3. Access from Windows
- Make sure SSH tunnel is running:
  ```bash
  gcloud compute ssh --zone us-central1-a instance-20250905-083402 -- -L 8081:localhost:8081 -L 8501:localhost:8501
  ```
- Open browser: `http://localhost:8501`

---

## 🧪 Step 5: Test Email Sending

### Quick Test (Before processing full CSV)

```bash
# Test email configuration
python -c "
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL = os.getenv('EMAIL_SENDER_ADDRESS')
PASSWORD = os.getenv('EMAIL_SENDER_PASSWORD')

msg = MIMEText('Test from Tata Strive')
msg['Subject'] = 'Test Email'
msg['From'] = EMAIL
msg['To'] = EMAIL  # Send to yourself

with smtplib.SMTP('smtp.gmail.com', 587) as server:
    server.starttls()
    server.login(EMAIL, PASSWORD)
    server.send_message(msg)
    print('✅ Email sent successfully!')
"
```

If successful, you'll receive a test email!

---

## 📊 Step 6: Process Your Assessment CSV

### Using the Web Interface

1. **Go to "Personalized Learning" tab**

2. **Upload your CSV file**
   - File should have columns:
     - `Login ID` (student email)
     - `Question Text`
     - `Answer Status` (Correct/Incorrect)
     - `Obtained Marks`
     - `Attempt ID` (optional)

3. **Click "Process & Send Emails"**
   - Wait 2-3 minutes for processing
   - System will show progress

4. **Check Results**
   - View which students received emails
   - See delivery status for each
   - Download report

### Expected Output

```
📊 Processing Results
─────────────────────────
Total Students:     25
Average Score:      72%
Emails Sent:        8

📧 Email Delivery Status
─────────────────────────
Email                       | Score | Status
500390420@tcit.com         | 4/10  | ✅ Sent
500391552@tcit.com         | 6/10  | ✅ Sent
...
```

---

## 🔍 Troubleshooting

### Issue: "Authentication failed" email error

**Solution:**
```bash
# Check .env file
cat .env | grep EMAIL

# Make sure you're using App Password, not regular password
# App Password format: "xxxx xxxx xxxx xxxx" (16 chars with spaces)
```

### Issue: "Module 'pandas' not found"

**Solution:**
```bash
conda activate rag_env
pip install pandas openpyxl
```

### Issue: Backend not starting

**Solution:**
```bash
# Check for syntax errors
python -m py_compile main.py

# Check logs
python main.py 2>&1 | tee error.log
```

### Issue: Students not receiving emails

**Checklist:**
- ✅ Check student email addresses in CSV are correct
- ✅ Check Gmail spam/junk folder
- ✅ Verify App Password is correct in `.env`
- ✅ Check Gmail sending limits (500/day max)

---

## 📧 Email Format Preview

Students will receive:

```
Subject: 📚 Your Personalized Study Guide - Front Desk Associate

Hi Student,

You recently completed the Front Desk Associate assessment.

📊 YOUR RESULTS:
Score: 4/10 (40%)
Status: Needs Improvement

⚠️ FOCUS AREAS:
• Hotel Definitions and Types
• Restaurant Classifications
• Traditional Indian Accommodations
• Front Office Management

📎 ATTACHED:
Your_Personalized_Study_Guide.pdf

This guide includes:
✓ Clear explanations of each topic
✓ Practical examples for Front Desk work
✓ Memory tips and tricks
✓ Practice questions with answers

Best regards,
Tata Strive Learning Team
```

---

## 🎯 Usage Tips

### For Facilitators

1. **Process one batch at a time** - Don't upload multiple batches simultaneously
2. **Check results before closing** - Wait for "Processing Complete" message
3. **Download report** - Save email delivery report for records
4. **Inform students** - Tell them to check email (including spam folder)

### Best Practices

- Upload CSV within 24 hours of assessment
- Use clear course names in file names
- Test with small batch (5 students) first
- Keep backup of original CSV files

---

## 📊 System Limits

```
Gmail Free Tier:
- 500 emails per day
- 99.9% delivery rate

Processing Speed:
- ~10 seconds per student
- 10 students = ~2 minutes
- 50 students = ~10 minutes

File Size Limits:
- CSV: up to 10 MB
- Generated PDFs: ~500 KB each
```

---

## 🆘 Support

If you encounter issues:

1. **Check logs in terminal** where backend is running
2. **Review this guide** for common solutions
3. **Test email configuration** separately
4. **Contact system administrator** with error messages

---

## ✅ Success Checklist

Before going live:

- [ ] Gmail App Password configured
- [ ] `.env` file updated with credentials
- [ ] Dependencies installed (pandas, openpyxl)
- [ ] Backend starts without errors
- [ ] Frontend loads correctly
- [ ] Test email sent successfully
- [ ] Small batch processed successfully
- [ ] Students confirmed receipt of emails

---

## 🎉 You're All Set!

The system is now ready to automatically process assessments and email personalized content to students. Upload your CSV and let the automation handle the rest!