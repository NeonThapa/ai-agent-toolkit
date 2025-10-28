# Tata Strive AI Agent Toolkit – Frontend

This directory hosts the modern React interface that replaces the previous Streamlit UI. It is built with Vite, React 19, and Material UI 7 with custom Tata Strive styling.

## Requirements

- Node.js 18+
- Backend API from `main.py` running (defaults to `http://localhost:8081`)

## Getting Started

```bash
npm install
echo "VITE_API_BASE_URL=http://localhost:8081" > .env   # adjust the URL as needed
npm run dev
```

Vite serves the app on `http://localhost:5173` by default.

## Scripts

| Command             | Purpose                                    |
|---------------------|--------------------------------------------|
| `npm run dev`       | Start the dev server with hot reload        |
| `npm run build`     | Production build in `dist/`                 |
| `npm run preview`   | Preview the production build locally        |
| `npm run lint`      | Run ESLint over the project                 |

## Project Structure

```
src/
  api/                # API helpers (fetch wrappers, error handling)
  components/         # Reusable UI building blocks (cards, selectors)
  constants.ts        # UI constants (languages, tone options, etc.)
  sections/           # Major screens: assessments, lessons, content, email
  theme.ts            # Custom Material UI theme tuned to Tata Strive
  utils/              # Utility helpers (downloads, etc.)
```

## Connecting to Other Environments

Create `.env` with the appropriate API base:

```bash
VITE_API_BASE_URL=https://your-api-hostname:8081
```

Restart `npm run dev` after changes. The React app automatically proxies requests to the configured backend.

## Branding Notes

- Primary colour mirrors the Tata Strive neon blue from the supplied logo.
- Cards, gradients, and metric tiles are tuned for presentation demos.
- Update `src/assets/tata-strive-logo.png` if the brand team provides a higher fidelity asset.

## Deployment

1. `npm run build`
2. Serve the `dist/` folder using Nginx, Firebase Hosting, Cloud Run static, etc.
3. Remember to expose the backend API to the same origin or configure CORS appropriately.

## Troubleshooting

- Ensure the backend is reachable from the browser (check network tab for 404/500 errors).
- JSON downloads appear inline; DOCX/PDF responses trigger automatic file downloads.
- Status pills in **System Configuration** reflect the last successful upload—use them to confirm data readiness.

For deeper setup instructions, see `../SETUP_GUIDE.md`.
