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

## Backlog
- P1: Edit existing sample; search/filter & pagination in results table.
- P1: Spec/limit-based auto pass-fail rating suggestions per parameter.
- P2: Dashboard analytics across modules (trend charts).
- P2: Real corporate portfolio sections (about, services, contact) on landing.
- P2: Streaming AI analysis; multi-language reports.
- P2: Authentication + per-operator history if needed later.

## Next Tasks
- Await user feedback on module parameters / rating scales for accuracy to their real lab SOPs.
