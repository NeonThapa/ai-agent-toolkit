# Tata Strive AI Agent Toolkit  
## Project Handover Dossier  

**Prepared:** 23 October 2025  
**Prepared for:** Successor developer  

---

### 1. Purpose & Current Capability
- Generates assessments, lesson plans, and facilitator content grounded in Tata Strive documents (RAG + LLM).  
- Outputs: Interactive JSON (API), DOCX, and polished PDF (ReportLab fallback with optional WeasyPrint).  
- Translation coverage: English + Hindi, Bengali, Marathi, Tamil, Telugu, Gujarati, Kannada.  
- Personalised learning flow can email remediation PDFs to students.  

All core user journeys work end-to-end on the current branch.

---

### 2. High-Level Architecture
```
React (Vite + MUI) SPA  →  Flask API (main.py)
                                     ├─ Pinecone index "tata-strive-rag"
                                     ├─ GCS bucket rag-source-documents/metadata_lookup.json
                                     ├─ Google Vertex AI embeddings (text-embedding-005)
                                     ├─ OpenRouter LLM + translation (model env-configurable)
                                     └─ ReportLab / WeasyPrint (PDF) + python-docx (DOCX)
```

---

### 3. Repository Map
```
ai-agent-toolkit/
├─ main.py                     # Flask API, RAG, PDF/DOCX generators
├─ frontend/                   # React client (Vite)
│  ├─ src/App.tsx              # Root layout & dashboard
│  └─ src/sections/...         # Feature-specific components
├─ assets/fonts/*.ttf          # Noto Sans families for Indic PDFs
├─ QUICK_START.md              # 10‑minute environment spin-up
├─ SETUP_GUIDE.md              # Detailed dependency & credential setup
├─ requirements.txt            # Python deps (WeasyPrint optional)
└─ complete-project-handover.md# (this document)
```

`complete_implementation_main.py` / Streamlit artifacts are historical; the live code path is `main.py` + `/frontend`.

---

### 4. Environment & Secrets
Create `.env` alongside `main.py`:

```
GOOGLE_CLOUD_PROJECT="tatastrive-269409"
PINECONE_API_KEY="pcsk_..."
PINECONE_INDEX_NAME="tata-strive-rag"     # optional; defaults to same
OPENROUTER_API_KEY="sk-or-v1-..."
RAG_MODEL="tngtech/deepseek-r1t2-chimera:free"
TRANSLATION_MODEL="z-ai/glm-4.5-air:free"
EMAIL_SENDER_ADDRESS="..."
EMAIL_SENDER_PASSWORD="..."               # Gmail App Password
EMAIL_SENDER_NAME="Tata Strive Learning Team"
FRONTEND_ORIGINS="http://localhost:5173"
```

Also provide a Google service account key file for Vertex AI / GCS access and set `GOOGLE_APPLICATION_CREDENTIALS`.

---

### 5. External Services
| Service | Usage | Notes |
|---------|-------|-------|
| Google Cloud Storage `rag-source-documents` | metadata + source PDFs | read-only in prod |
| Pinecone index `tata-strive-rag` | RAG retrieval | 768-d cosine vectors |
| Google Vertex AI | text-embedding-005 | paid quotas; monitor usage |
| OpenRouter | LLM + translation | models configured via env |
| Gmail SMTP | transactional emails | TLS 587 using app password |

Hand over access/credentials securely.

---

### 6. Local Runbook
1. `conda activate rag_env` (or equivalent).  
2. `pip install -r requirements.txt` (WeasyPrint will attempt GTK libs; optional).  
3. `npm install` inside `frontend/`.  
4. Start backend: `python main.py` (runs on `http://0.0.0.0:8081`).  
5. Start frontend: `npm run dev` (Vite default `http://localhost:5173`).  
6. Upload CSV/TXT data from the dashboard if running in a fresh environment (course durations, holidays, guidelines).  

For production builds, run `npm run build && npm run preview`.

---

### 7. Document Generation Details
- `main.py::_register_pdf_fonts` loads Noto Sans families from `assets/fonts/`. Fonts for Hindi/Bengali/Tamil/Telugu/Gujarati/Kannada are pre-downloaded; add more scripts by dropping the relevant Noto Sans TTFs and updating the map.  
- Primary PDFs render with ReportLab. If WeasyPrint + GTK libs are installed the HTML renderer is used automatically.  
- Numbered list artefacts were removed by rendering staged paragraphs; translation fallback returns source text if the translation model responds with an empty string.  
- DOCX exports keep markdown emphasis via `_add_markdown_runs`. No further action required.  

When handing off, include sample PDFs in each language to demonstrate baseline output.

---

### 8. Known Issues & Backlog
| Category | Status / Mitigation |
|----------|--------------------|
| WeasyPrint GTK dependency | Optional; ReportLab fallback now styled. Documented in QUICK_START. |
| API keys in `.env` | Never commit; rotate if shared externally. |
| Pinecone quota | Monitor monthly query/ingest limits. |
| Tests | No automated tests. Manual regression: generate assessment/lesson/content PDF & DOCX in English + one regional language. |
| Auth / RBAC | None. Reverse proxy or identity provider should gate access if deployed publicly. |

Potential roadmap: add caching, persistent storage of generated artefacts, admin analytics, CI/CD.

---

### 9. Verification Checklist Before Handover
1. Backend boots without missing-module errors (`pip install` complete).  
2. `/health` returns `200` with counts > 0 after data upload.  
3. Assessment Creator can output PDF + DOCX in English and a regional language (e.g., Hindi).  
4. Lesson Planner respects holidays (verify sample CSV).  
5. Email flow (`/process/assessment_and_email`) sends successfully with Gmail credentials.  
6. Frontend hero section readable (lighter backdrop implemented).  
7. Fonts directory contains the following files:  
   - `NotoSans-Regular.ttf`, `NotoSans-Bold.ttf`  
   - `NotoSansDevanagari-Regular.ttf`, `NotoSansDevanagari-Bold.ttf`  
   - `NotoSansBengali-Regular.ttf`, `NotoSansBengali-Bold.ttf`  
   - `NotoSansTamil-Regular.ttf`, `NotoSansTamil-Bold.ttf`  
   - `NotoSansTelugu-Regular.ttf`, `NotoSansTelugu-Bold.ttf`  
   - `NotoSansGujarati-Regular.ttf`, `NotoSansGujarati-Bold.ttf`  
   - `NotoSansKannada-Regular.ttf`, `NotoSansKannada-Bold.ttf`  

---

### 10. Suggested First Tasks for Successor
1. Stand up the environment using the runbook above.  
2. Regenerate sample artefacts and compare against provided reference PDFs/DOCX.  
3. Review `main.py` (PDF/DOCX utilities around lines 190–1550) and `frontend/src/App.tsx` to understand styling/layout.  
4. Align with stakeholders on next milestone (e.g., additional languages, scheduling, authentication).  

---

### 11. Supporting Documents
- `QUICK_START.md` – concise setup.  
- `SETUP_GUIDE.md` – extended instructions, troubleshooting.  
- Sample outputs folder (add before delivery).  
- This handover file can be exported as PDF via any Markdown → PDF tool (e.g., VS Code print, WeasyPrint).  

---

### 12. Final Notes
- The system is stable for demonstrations and pilot use.  
- Fonts + translation models are the most common points of regression—retain bundled assets when zipping the project.  
- Keep communication channels open with operations for API key rotation and Pinecone index health.  

**Handover complete.** Feel free to reach out if any clarifications are required during onboarding.
