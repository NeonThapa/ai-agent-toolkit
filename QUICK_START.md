# ⚡ Quick Start – Tata Strive AI Agent Toolkit (React)

Launch the personalised learning stack (Flask API + React UI) in ~10 minutes.

---

## 1. Prerequisites

- Python environment with access to the existing Flask backend (`main.py`).
- Node.js 18+ (for the React app).
- Gmail App Password configured (see `SETUP_GUIDE.md`).

---

## 2. Backend

```bash
conda activate rag_env
pip install -r requirements.txt
python main.py
```

Keep the server running; it listens on `http://localhost:8081`.

> **PDF reminder:** Ensure `assets/fonts/` travels with the project—those bundled Noto Sans families power Indic language PDFs. Optional GTK/WeasyPrint packages can be added later if you prefer HTML rendering; otherwise the themed ReportLab fallback is already active.

---

## 3. Frontend

```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8081" > .env
npm run dev
```

Open the displayed URL (default `http://localhost:5173`). The interface is pre-branded for Tata Strive.

---

## 4. First-Time Data Loads

Inside the React app:

1. **System Configuration** → upload course durations, holiday calendar, and assessment guidelines.
2. Confirm status pills switch to ✅ after each upload.
3. Document selector should list Pinecone knowledge-base titles.

---

## 5. Generate Something!

1. **Assessment Creator** – choose a topic, pick documents, and generate JSON/PDF/DOCX.
2. **Lesson Planner** – supply start date + state to see holidays excluded automatically.
3. **Personalized Learning** – upload a test CSV and confirm email summary metrics.

Downloads trigger automatically for DOCX/PDF outputs; JSON results render inline.

---

## 6. Production Build (Optional)

```bash
cd frontend
npm run build
npm run preview
```

Serve `frontend/dist/` behind your preferred web server once validated.

---

## 7. Troubleshooting

- **No documents listed?** Ensure `main.py` can reach Pinecone and the metadata file in Cloud Storage.
- **Uploads failing?** Check backend logs; API responses are surfaced as toasts in the UI.
- **Emails not sending?** Re-run the Gmail App Password test in `SETUP_GUIDE.md`.
- **PDF export failing?** Install the system GTK stack (`libgobject-2.0-0` and friends) if you want WeasyPrint rendering. Without it the service now falls back to the bundled ReportLab theme, which still produces branded PDFs but logs a warning.
- **Boxes in regional-language PDFs?** Confirm the `assets/fonts/` directory remains alongside `main.py`; it ships with Noto Sans families for Indic scripts. Re-run the quick font download step if those files were removed.

You're all set to demo the Tata Strive AI Agent Toolkit with a clean, modern experience.
