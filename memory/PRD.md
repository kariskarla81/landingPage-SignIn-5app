# Elastech Production — Product Requirements Document

## Original Problem Statement
Build a company portfolio web app "Elastech Production" with a dark-mode (black/dark), professional-tech aesthetic. Landing page shows the company name + tagline (SaaS, IoT, Web App, Mobile App). A permanent left sidebar holds the brand and 3 menus: K-HTT Analyst, Copper Strip ASTM D130, Rating DKA. Each module is a petroleum lab testing tool with sample data input, rating assessment, AI analysis, and PDF report export — shown as an input form + tidy results table in dark mode.

## User Choices
- AI analysis: Claude Sonnet 4.6 via Emergent Universal LLM Key
- Authentication: none (all modules public)
- Persistence: save test history to MongoDB
- Module technical content: based on general petroleum industry standards (ASTM D130, etc.)

## Architecture
- Frontend: React 19 + React Router + Tailwind + shadcn/ui, framer-motion, react-query, jsPDF (client-side PDF export). Dark zinc theme, amber accent, Outfit/Inter/JetBrains Mono fonts.
- Backend: FastAPI + Motor (MongoDB). All routes under /api.
- LLM: emergentintegrations LlmChat -> anthropic/claude-sonnet-4-6.

## Data Model (collection: samples)
id, module (khtt|copper-strip|rating-dka), sample_code, sample_name, product_type, operator, test_date, parameters{}, rating, notes, ai_analysis, ai_analyzed_at, created_at.

## Implemented (2026-06)
- Landing page: hero, tagline chips, 3 module cards, feature strip.
- Permanent left sidebar (desktop) + mobile top-bar menu, active-route amber indicator.
- 3 lab modules (generic ModulePage driven by config/modules.js): sample input form, rating select, per-module parameters, results table.
- Create / list / delete samples (persisted to MongoDB).
- AI analysis endpoint (Claude Sonnet 4.6) returning structured Indonesian report; stored on the sample.
- Detail dialog with parameter table + AI analysis.
- Client-side branded PDF export per sample.
- Verified end-to-end by testing agent: backend 100%, frontend 100%.

## K-HTT Analyst — paritas dengan versi mobile (2026-06, selesai & teruji)
Sumber: github.com/Ilhamfawwaz28/RatingMeasurementKharisma (mobile Expo). Backend /api/kht/* sudah identik
(upload multipart + chunked fallback, AI Vision Gemini 3.1 Pro 2-gambar vs Nikko Color Scale, rating 0–10,
CLEAR ≥7 / TARNISH, edit rating/summary/recommendation, dashboard, trend, color-scale, soft delete, seed 4 demo).
Frontend baru (React):
- Rute: /khtt (Dashboard), /khtt/new (New Test), /khtt/history, /khtt/trend, /khtt/result/:id, /khtt/color-scale.
- New Test: Camera (getUserMedia) / Gallery + CropEditor (drag/resize, USE FULL / USE CROP), form Sample Info & Test Condition
  (default 320°C/16h/10/0.31), Run AI Vision (job polling s/d 6 menit, stage text).
- Result: TubeViewer Heatmap/Original, RatingGauge, KHT scale, edit inline rating/deskripsi/rekomendasi, export PDF, delete.
- History: search backend, chip All/Clear/Tarnish, mode pilih + Pilih Semua, export PDF gabungan (cover + halaman/sampel).
- PDF: layout HTML identik mobile, dicetak via iframe tersembunyi + window.print (Print → Save as PDF).
- Tema global diubah ke navy gelap (#0A1420/#112033) + aksen cyan (#00D2D3), font Barlow Condensed + JetBrains Mono
  (override palet zinc/amber di tailwind.config.js). Sidebar punya sub-nav K-HTT.
- File: frontend/src/lib/kht/{api,format,pdf}.js, components/kht/{ui,viz,capture}.jsx, pages/kht/*.jsx.
- Testing agent: backend 11/11 (tests/test_kht.py), frontend semua alur lolos (test_reports/iteration_2.json).

## Copper Strip ASTM D130 — paritas dengan versi mobile (2026-07, selesai; backend teruji 18/18)
Sumber: github.com/karismswzet-tech/RatingMeasurement3-App (mobile Expo). Copper Strip yang tadinya hanya
manual-entry generik kini dibangun ulang jadi modul AI Vision penuh, meniru pola modul DKA yang sudah ada.
Backend /api/copper/*: upload (pakai /api/kht/upload bersama) + analyze/start job async + polling jobs/{id},
AI Vision Gemini gemini-3.1-pro-preview membandingkan foto sampel vs chart standar ASTM D130/IP 154 (bundled
reference/astm_d130.jpg), klasifikasi 0/1a/1b/2a/2b/2c/2d/3a/3b/3c/4a/4b/4c, status CLEAR (kelas 0/1a/1b) /
TARNISH, severity 0–12, confidence, ai_summary + recommendation (Bahasa Indonesia). CRUD tests (search q,
edit klasifikasi→auto recompute label/group/color/severity/status, edit summary/recommendation, soft delete),
dashboard (total/clear/tarnish), trend, reference-scale (base64 chart + 13 kelas). 4 demo test + reference
di-seed saat startup.
Frontend (React) mirror DKA/KHT:
- Rute: /copper-strip (Dashboard), /new, /history, /trend, /copper-strip/result/:id, /copper-strip/scale.
- New Test: Camera (getUserMedia)/Gallery + form (Sample ID auto CU-YYYY-MM-DD-nnn, Product default
  "Diesel Fuel B30", Batch, Operator, Temp 100°C, Duration 3h, Remark), Run AI Vision (polling s/d 6 menit).
- Result: CopperClassGauge (swatch warna kelas + border CLEAR/TARNISH), CopperClassPicker koreksi manual 0–4c,
  edit inline deskripsi/rekomendasi, export PDF (layout identik mobile via window.print), delete.
- History: search backend + mode pilih (Pilih Semua) + export PDF gabungan (cover + 1 halaman/sampel).
- Trend: severity chart 0–12. Scale: chart standar ASTM D130 + daftar 13 kelas dengan status.
- File: frontend/src/lib/copper/{api,pdf}.js, components/copper/ui.jsx, pages/copper/*.jsx. Sidebar sub-nav Copper.
- Teruji testing agent: backend 18/18 lolos (termasuk analisa AI nyata ±27 dtk).

## Auth — login internal (single admin) (2026-07, selesai; backend teruji 16/16)
Halaman login profesional untuk aplikasi internal. Backend: kredensial dari env (ADMIN_USERNAME,
ADMIN_PASSWORD_HASH_B64 = base64 dari bcrypt hash agar `$` aman di .env; SESSION_TTL_MINUTES=60).
Endpoint /api/auth/login|me|logout; session di Mongo 'sessions' dengan expiry geser (sliding) untuk
timeout inaktivitas. Middleware auth_guard memproteksi SEMUA /api/* kecuali: OPTIONS, /api & /api/
(health), /api/auth/*, /api/kht/files/* (serving gambar untuk <img>). Frontend: AuthProvider + interceptor
(axios + global fetch inject X-Session-Token, tangani 401), RequireAuth guard (redirect ke /login bila
belum login), halaman /login (tema navy/cyan, show/hide password, error inline), tombol Logout di sidebar
& top-bar mobile (hapus session backend + token lokal). Kredensial default admin/Elastech@2026 (di
memory/test_credentials.md). Catatan: preview diakses via host REACT_APP_BACKEND_URL
(web-app-rating.preview.emergentagent.com) — mengakses via host lain memicu CORS.

## Backlog
- P1: Samakan modul Rating DKA dengan versi mobile (sudah ada modul /dka AI Vision + OCR di web).
- P1: Edit existing sample; search/filter & pagination in results table.
- P1: Spec/limit-based auto pass-fail rating suggestions per parameter.
- P2: Dashboard analytics across modules (trend charts).
- P2: Real corporate portfolio sections (about, services, contact) on landing.
- P2: Streaming AI analysis; multi-language reports.
- P2: Authentication + per-operator history if needed later.

## Next Tasks
- Await user feedback on module parameters / rating scales for accuracy to their real lab SOPs.
