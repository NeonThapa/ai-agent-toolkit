# 🚀 Personalized Learning System – Setup Guide (React Frontend)

The Tata Strive AI Agent Toolkit now ships with a modern React interface instead of Streamlit. This guide walks you through the end-to-end setup: backend services, branding-friendly frontend, and email automation.

---

## 📬 Step 1: Gmail App Password (5 minutes)

Used for sending personalised study packs.

1. Visit [https://myaccount.google.com/](https://myaccount.google.com/) and enable **2-Step Verification**.
2. Navigate to **Security → App Passwords**.
3. Choose App: `Mail`, Device: `Other (Tata Strive)` and generate the password.
4. Capture the 16-character password and update `.env` in the project root:

```bash
EMAIL_SENDER_ADDRESS="your.facilitator.email@gmail.com"
EMAIL_SENDER_PASSWORD="xxxx xxxx xxxx xxxx"  # 16-character app password
EMAIL_SENDER_NAME="Tata Strive Learning Team"
```

---

## 🛠️ Step 2: Backend Dependencies

```bash
conda activate rag_env
pip install -r requirements.txt
```

If you only need the email workflow, ensure `pandas` and `openpyxl` are present:

```bash
pip install pandas openpyxl
```

### Optional: Install GTK libraries for WeasyPrint
If you want HTML-to-PDF rendering via WeasyPrint (instead of the built-in ReportLab theme), install the GTK dependencies listed in [WeasyPrint’s installation guide](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html#installation). The backend automatically switches renderers when WeasyPrint imports successfully.

---

## 🗂️ Step 2½: Verify PDF Font Assets

Multilingual PDFs depend on the bundled **Noto Sans** families under `assets/fonts/`. Confirm the directory contains:

- `NotoSans-Regular.ttf`, `NotoSans-Bold.ttf`
- `NotoSansDevanagari-Regular.ttf`, `NotoSansDevanagari-Bold.ttf`
- `NotoSansBengali-Regular.ttf`, `NotoSansBengali-Bold.ttf`
- `NotoSansTamil-Regular.ttf`, `NotoSansTamil-Bold.ttf`
- `NotoSansTelugu-Regular.ttf`, `NotoSansTelugu-Bold.ttf`
- `NotoSansGujarati-Regular.ttf`, `NotoSansGujarati-Bold.ttf`
- `NotoSansKannada-Regular.ttf`, `NotoSansKannada-Bold.ttf`

Missing files can be re-downloaded from the Noto fonts repository or copied from the handoff package. Add new Indic scripts by placing the appropriate TTF files here and registering them in `main.py`.

---

## ⚙️ Step 3: Start the Backend API

```bash
conda activate rag_env
python main.py
```

You should see logs similar to:

```
Initializing Pinecone...
✅ Pinecone index connection established.
✅ Metadata loaded successfully.
Starting Tata Strive RAG API Server...
* Running on http://127.0.0.1:8081
```

Keep this terminal running.

---

## 🎨 Step 4: React Frontend Setup

The new interface lives in `frontend/`. It uses Vite + React + Material UI with Tata Strive styling.

1. **Install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Configure the API base URL**

   Create `frontend/.env` (or copy `.env.example` if you add one) with:

   ```bash
   VITE_API_BASE_URL="http://localhost:8081"
   ```

   Adjust the value if the backend is exposed on a different host/port.

3. **Run the development server**

   ```bash
   npm run dev
   ```

   Vite prints a URL (default `http://localhost:5173`). Open it in your browser.

4. **Production build (optional)**

   ```bash
   npm run build
   npm run preview  # serve the built files locally
   ```

---

## 🧭 Step 5: Touring the Interface

The React UI mirrors all Streamlit flows with a polished Tata Strive look:

- **System Configuration** (left column) – upload course durations, holiday calendars, and assessment guidelines. Status pills show which datasets are active.
- **Assessment Creator** – generate JSON/Docx/PDF assessments grounded in selected knowledge-base documents.
- **Lesson Planner** – respects course duration, holidays, and suggested languages based on IP detection.
- **Content Generator** – produce facilitator notes, learner handouts, and more with tone, audience, and depth controls.
- **Personalized Learning** – upload assessment CSV/Excel files, auto-email learners scoring below 70 %, and review delivery analytics.

Document selectors and forms all talk to the existing Flask endpoints; no backend changes are required.

---

## ✅ Step 6: Smoke Tests

1. **Health check** – visit `http://localhost:8081/health` to confirm backend readiness.
2. **Document discovery** – in the UI, confirm that the document multiselect loads Pinecone titles.
3. **Email test** – use the Personalized Learning tab with a small CSV and verify emails are sent (use a test cohort first).

---

## 🌐 Remote Access Tips

If hosting on GCP or another VM, tunnel both ports:

```bash
gcloud compute ssh <instance> -- -L 8081:localhost:8081 -L 5173:localhost:5173
```

Then open `http://localhost:5173` locally.

---

## 📎 Useful Commands

```bash
# From project root
python main.py                     # Backend API

# From ai-agent-toolkit/frontend
npm run dev                        # React dev server
npm run build && npm run preview   # Production preview
```

You're ready to demo the Tata Strive AI Agent Toolkit with a modern user experience.
