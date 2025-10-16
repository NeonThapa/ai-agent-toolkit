# ⚡ Quick Start - 15 Minute Setup

## 🎯 Goal
Get personalized learning system running with automated emails in 15 minutes.

---

## ✅ Pre-Implementation Checklist

Before starting, you should have:
- [ ] VM with backend running (main.py works)
- [ ] Streamlit frontend accessible
- [ ] Gmail account for sending emails
- [ ] Sample assessment CSV ready for testing

---

## 📝 Step-by-Step (15 minutes)

### **Step 1: Gmail Setup** (5 mins)

```bash
1. Go to: https://myaccount.google.com/security
2. Enable 2-Factor Authentication (if not enabled)
3. Go to: https://myaccount.google.com/apppasswords
4. Generate app password for "Mail"
5. Copy the 16-character password
```

### **Step 2: Update .env File** (1 min)

```bash
cd ~/rag_api
nano .env
```

Add these lines:
```bash
EMAIL_SENDER_ADDRESS="facilitator@gmail.com"
EMAIL_SENDER_PASSWORD="xxxx xxxx xxxx xxxx"
EMAIL_SENDER_NAME="Tata Strive Learning Team"
```

Save and exit (Ctrl+O, Enter, Ctrl+X)

### **Step 3: Install Dependencies** (2 mins)

```bash
conda activate rag_env
pip install pandas openpyxl
```

### **Step 4: Backup Old Files** (1 min)

```bash
cd ~/rag_api
cp main.py main_OLD.py
cp frontend_app.py frontend_OLD.py
```

### **Step 5: Update main.py** (3 mins)

```bash
nano main.py
```

- Delete all content (Ctrl+K repeatedly)
- Copy complete content from artifact "main.py - Complete with Email Automation"
- Paste into nano
- Save (Ctrl+O, Enter, Ctrl+X)

### **Step 6: Update frontend_app.py** (3 mins)

```bash
nano frontend_app.py
```

- Delete all content
- Copy complete content from artifact "frontend_app.py - Complete with Automated Email System"
- Paste into nano
- Save (Ctrl+O, Enter, Ctrl+X)

### **Step 7: Restart Services** (2 mins)

**Terminal 1 - Backend:**
```bash
# Stop old backend (Ctrl+C if running)
conda activate rag_env
cd ~/rag_api
python main.py
```

Wait for:
```
✅ Pinecone index connection established.
✅ Metadata loaded successfully.
* Running on http://127.0.0.1:8081
```

**Terminal 2 - Frontend:**
```bash
# Stop old frontend (Ctrl+C if running)
conda activate rag_env
cd ~/rag_api
python -m streamlit run frontend_app.py
```

Wait for:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

---

## 🧪 Testing (5 minutes)

### **Test 1: Email Configuration**

```bash
python3 << 'EOF'
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os

load_dotenv()
EMAIL = os.getenv('EMAIL_SENDER_ADDRESS')
PASSWORD = os.getenv('EMAIL_SENDER_PASSWORD')

try:
    msg = MIMEText('System test successful!')
    msg['Subject'] = 'Test - Tata Strive System'
    msg['From'] = EMAIL
    msg['To'] = EMAIL
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)
    print('✅ SUCCESS: Email configuration works!')
except Exception as e:
    print(f'❌ ERROR: {e}')
EOF
```

**Expected:** You receive test email in your inbox

### **Test 2: Upload CSV**

1. Open browser: `http://localhost:8501`
2. Go to "Personalized Learning" tab
3. Upload your assessment CSV (the one you sent me earlier works!)
4. Click "Process & Send Emails"
5. Wait 2-3 minutes

**Expected Output:**
```
✅ Processing Complete!
- 8 students received personalized study guides
- Each email contains a PDF
```

---

## ✅ Verification

After testing, verify:

- [ ] Backend shows no errors
- [ ] Frontend loads "Personalized Learning" tab
- [ ] Test email received successfully
- [ ] CSV uploads without errors
- [ ] Progress shows during processing
- [ ] Results dashboard displays correctly
- [ ] Students receive emails with PDFs
- [ ] PDFs contain relevant content

---

## 🚨 If Something Goes Wrong

### Backend won't start
```bash
# Check for errors
python main.py 2>&1 | head -20

# Common fix: reinstall packages
pip install --upgrade flask pandas openpyxl
```

### Email not sending
```bash
# Verify .env
cat .env | grep EMAIL

# Common issues:
# - Using regular password instead of app password
# - Spaces in password not preserved
# - Wrong email address
```

### CSV upload fails
```bash
# Check CSV format
python -c "import pandas as pd; df = pd.read_csv('your_file.csv'); print(df.columns)"

# Required columns:
# - Login ID
# - Question Text  
# - Answer Status
# - Obtained Marks
```

---

## 📞 Quick Fixes

| Problem | Quick Fix |
|---------|-----------|
| "Module not found" | `pip install pandas openpyxl` |
| "Email auth failed" | Check app password in `.env` |
| "File format error" | Ensure CSV has correct columns |
| "Timeout error" | Reduce batch size (< 20 students) |
| Backend crash | Check logs: `python main.py 2>&1` |

---

## 🎉 Success! What Next?

Once everything works:

1. **Process real batch** - Upload full assessment data
2. **Monitor delivery** - Check email delivery report
3. **Get feedback** - Ask students if they received content
4. **Iterate** - Improve based on feedback

---

## 📚 Full Documentation

For detailed information:
- **Setup Guide**: SETUP_GUIDE.md (complete instructions)
- **Architecture**: See artifacts for system design
- **API Docs**: Check `/health` endpoint for status

---

## ⏱️ Timeline Recap

```
✓ Gmail setup:        5 minutes
✓ Update .env:        1 minute
✓ Install packages:   2 minutes
✓ Update files:       6 minutes
✓ Test system:        5 minutes
─────────────────────────────────
  TOTAL:             19 minutes
```

You're ready to go! 🚀