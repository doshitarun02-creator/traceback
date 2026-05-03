# TraceBack 🛡️

> **India's first AI-powered cybercrime fund recovery platform.**
> Fraud hit you. We trace it back.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask)](https://flask.palletsprojects.com)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?logo=mongodb)](https://mongodb.com/atlas)
[![Gemini](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-orange?logo=google)](https://aistudio.google.com)
[![Deploy](https://img.shields.io/badge/Deploy-Render-purple?logo=render)](https://render.com)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## What is TraceBack?

India recorded **3.24 crore cybercrime complaints in 2025** — one every second. ₹22,495 crore was lost. Yet **59.1% of defrauded funds are never recovered**, largely because victims don't know how to structure their case for the government's I4C-NPCI API within the critical Golden Hour.

**TraceBack fills that gap.**

- 🤖 **AI Triage in 60 seconds** — Gemini 1.5 Flash classifies fraud type, scores urgency, and structures your data to match the I4C API schema
- ⚡ **Golden Hour optimized** — every workflow is designed to maximize bank-freeze probability before funds move
- 👨‍💼 **Expert Marketplace** — verified CEH/CHFI-certified specialists for FIR drafting, bank escalation, and forensic evidence
- ⚖️ **Legally compliant** — built on BNSS 2023, BSA 2023, DPDP Act 2023, and RBI Zero Liability guidelines
- 💰 **Success-fee model** — pay only when funds are recovered (5–10%)

---

## Live Stats (I4C Data 2025)

| Metric | Value |
|--------|-------|
| Annual complaints (2025) | 3.24 Crore |
| Daily complaints | 88,976 |
| Financial losses | ₹22,495 Crore |
| Govt recovery rate | 40.9% |
| Funds never recovered | ₹13,306 Crore |
| Maharashtra losses | ₹3,203 Crore |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5 + CSS3 + Vanilla JS (single file) |
| Backend | Python Flask 3.0 |
| Database | MongoDB Atlas (PyMongo) |
| AI Triage | Google Gemini 1.5 Flash |
| Auth | JWT (PyJWT) + bcrypt |
| File Storage | Cloudinary |
| Email | Flask-Mail (SMTP) |
| Rate Limiting | Flask-Limiter |
| Validation | Pydantic v2 |
| Deployment | Render (Gunicorn) |

---

## Project Structure

```
traceback/
├── static/
│   └── traceback_v1.html       # Frontend — complete single-file site
│
├── app/
│   ├── __init__.py             # Flask app factory
│   ├── config.py               # Dev/Prod/Test config
│   ├── extensions.py           # DB, mail, limiter instances
│   │
│   ├── models/
│   │   ├── user.py             # User schema + MongoDB helpers
│   │   ├── complaint.py        # Complaint schema + case ID generator
│   │   └── expert.py           # Expert marketplace schema
│   │
│   ├── routes/
│   │   ├── auth.py             # /api/auth/* — register, login, refresh
│   │   ├── complaints.py       # /api/complaints/* — intake + tracking
│   │   ├── triage.py           # /api/triage/* — AI analysis
│   │   ├── experts.py          # /api/experts/* — marketplace + booking
│   │   ├── cases.py            # /api/cases/* — timeline + live stats
│   │   └── admin.py            # /api/admin/* — dashboard
│   │
│   ├── services/
│   │   ├── gemini_service.py   # Gemini API triage + rule-based fallback
│   │   ├── i4c_formatter.py    # I4C API schema formatter
│   │   ├── file_service.py     # Cloudinary evidence upload
│   │   └── email_service.py    # Victim + expert notifications
│   │
│   ├── middleware/
│   │   └── auth_middleware.py  # JWT decorators (@token_required etc.)
│   │
│   └── utils/
│       ├── constants.py        # Fraud types, states, tiers, banks
│       ├── validators.py       # Indian phone, UPI, PAN, IFSC validators
│       └── response.py         # Standardized API response helpers
│
├── run.py                      # Entry point
├── seed.py                     # Populates MongoDB with demo data
├── test_all.py                 # End-to-end API test suite (11 tests)
├── Procfile                    # Render/Heroku deploy command
├── gunicorn.conf.py            # Production server config
├── requirements.txt            # All dependencies pinned
├── .env.example                # Environment variable template
└── DEPLOY_CHECKLIST.md         # Step-by-step production deployment guide
```

---

## Quick Start (Local)

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/traceback.git
cd traceback
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```env
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/traceback
GEMINI_API_KEY=your-gemini-key-from-aistudio.google.com
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-key
CLOUDINARY_API_SECRET=your-secret
SECRET_KEY=run: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET_KEY=run: python -c "import secrets; print(secrets.token_hex(32))"
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

### 3. Seed Database

```bash
python seed.py
```

Expected output:
```
✅ Users seeded: 4 documents
✅ Experts seeded: 6 documents
✅ Complaints seeded: 5 documents
✅ Counter initialized: complaint_counter = 5
🚀 TraceBack seed complete.
```

### 4. Run

```bash
python run.py
```

Open `http://localhost:5000` → full TraceBack site loads.

### 5. Test All Endpoints

```bash
python test_all.py
```

Expected:
```
[1/11] GET  /health                    ✅ PASS
[2/11] POST /api/auth/register         ✅ PASS
[3/11] POST /api/auth/login            ✅ PASS
[4/11] POST /api/triage/analyze        ✅ PASS
[5/11] POST /api/complaints/submit     ✅ PASS
[6/11] GET  /api/complaints/{id}       ✅ PASS
[7/11] GET  /api/experts               ✅ PASS
[8/11] GET  /api/experts?category=...  ✅ PASS
[9/11] GET  /api/cases/stats/live      ✅ PASS
[10/11] POST /api/auth/login (admin)   ✅ PASS
[11/11] GET  /api/admin/dashboard      ✅ PASS

11/11 tests passed. TraceBack is ready to deploy. 🚀
```

---

## API Reference

### Auth

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | None | Register new victim user |
| POST | `/api/auth/login` | None | Login, get JWT tokens |
| POST | `/api/auth/refresh` | None | Refresh access token |
| GET | `/api/auth/verify/:token` | None | Email verification |
| GET | `/api/auth/me` | JWT | Get current user profile |

### Complaints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/complaints/submit` | Optional | Submit fraud complaint + get AI triage |
| GET | `/api/complaints/:case_id` | JWT | Get complaint by case ID |
| GET | `/api/complaints/user/all` | JWT | Get all complaints for current user |
| PATCH | `/api/complaints/:case_id/status` | Expert/Admin | Update case status |

### Triage

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/triage/analyze` | None | Run AI triage on fraud data |

### Experts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/experts` | None | List experts (filter by ?category=) |
| GET | `/api/experts/:id` | None | Get expert profile |
| POST | `/api/experts/book` | JWT | Book expert for a case |

### Cases

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/cases/:case_id/timeline` | JWT | Get full case timeline |
| POST | `/api/cases/:case_id/update` | Expert/Admin | Add timeline event |
| GET | `/api/cases/stats/live` | None | Live platform stats (cached 60s) |

### Admin

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/admin/dashboard` | Admin JWT | Aggregated platform stats |
| GET | `/api/admin/complaints` | Admin JWT | All complaints with filters |
| PATCH | `/api/admin/complaints/:id/assign` | Admin JWT | Assign expert to case |

---

## Pricing Tiers

| Tier | Price | For | Key Features |
|------|-------|-----|-------------|
| **Scout** | Free | Fraud up to ₹50,000 | AI triage, 1930/NCRP guidance, bank dispute templates |
| **Trace** | ₹1,999 | Fraud ₹50K–₹10L | 2 expert sessions, FIR draft, RBI escalation, case dashboard |
| **Forge** | ₹24,999 + 5–10% success fee | Fraud ₹10L+ | Full device forensics, court-admissible BSA §63(4) reports, dedicated manager |

---

## Legal Compliance

TraceBack is built on India's post-2023 legal stack:

- **BNSS 2023 §173** — Zero FIR, e-FIR structured drafting
- **BSA 2023 §63(4)** — Court-admissible digital evidence with MD5/SHA-256 hash preservation
- **DPDP Act 2023** — Data Fiduciary model, explicit consent, India-hosted data
- **RBI Zero Liability Rule** — Shadow reversal within 10 days, zero liability if reported in 3 working days
- **Success Fees** — Legal for technical consultants (not advocates); Bar Council rules don't apply
- **BNSS §106** — Bank freeze support via structured I4C API data submission

> TraceBack is a private advisory platform. Not a law firm. Not affiliated with any government body.

---

## Fraud Types Supported

| Type | % of Losses | TraceBack Response |
|------|------------|-------------------|
| Investment Scams | 76–77% | OSINT + Blockchain tracing + Fake platform analysis |
| Digital Arrest Scams | 8–9% | CBI/ED impersonation evidence + FIR drafting |
| UPI/Bank Fraud | 7% | UTR tracing + Bank escalation + RBI notice |
| Sextortion | 4% | SOCMINT + Evidence preservation + Victim support |
| E-Commerce Fraud | 3% | Merchant dispute + Phishing analysis |
| Credit Card Fraud | 1% | Card forensics + Bank ombudsman |

---

## Deploy to Render

```bash
# 1. Push to GitHub
git push origin main

# 2. Create Web Service on render.com
#    Build Command:  pip install -r requirements.txt
#    Start Command:  gunicorn --config gunicorn.conf.py run:app

# 3. Add environment variables in Render dashboard
#    (see DEPLOY_CHECKLIST.md for full list)

# 4. Verify deployment
curl https://your-app.onrender.com/health
# → {"status": "ok", "platform": "TraceBack"}
```

See [DEPLOY_CHECKLIST.md](DEPLOY_CHECKLIST.md) for the full step-by-step checklist.

---

## Expert Marketplace

TraceBack connects victims with verified cybercrime specialists:

| Expert | Certifications | Specialization | Rate |
|--------|---------------|----------------|------|
| Aditya Kumar | CHFI, CEH | Investment Fraud (IIT Kanpur) | ₹3,500/hr |
| Priya Sharma | CHFI | Digital Arrest (Ex-Cybercell) | ₹4,200/hr |
| Rahul Joshi | CEH | UPI/Mobile Forensics | ₹2,800/hr |
| Sneha Nair | CHFI, CEH | Sextortion & Social Media | ₹3,100/hr |
| Vikram Desai | CEH | Credit Card & Banking | ₹2,600/hr |
| Ananya Reddy | CHFI | E-Commerce & OTP Fraud | ₹2,400/hr |

---

## Business Model

| Stream | Revenue | Description |
|--------|---------|-------------|
| Consultation + Success Fees | ₹1,999–₹24,999 + 5–10% | Primary B2C |
| B2B SME Retainers | ₹15K–₹40K/mo | Incident response |
| Cyber Insurance Partner | Referral fees | Tata AIG (98.1%), ICICI Lombard (97.6%) |
| Scam Intelligence Feed | SaaS B2B API | Anonymised fraud pattern data |

---

## Contributing

This project is currently in active development by **Team Strawhats**.

If you'd like to contribute:
1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit: `git commit -m "feat: your feature"`
4. Push: `git push origin feat/your-feature`
5. Open a Pull Request

---

## Data Sources

All statistics are sourced from:
- Indian Cyber Crime Coordination Centre (I4C) — Annual Report 2025
- National Cyber Crime Reporting Portal (NCRP) — 2025 data
- Reserve Bank of India (RBI) — Fraud reporting circulars
- Ministry of Home Affairs — Cybercrime statistics

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Built By

**Team Strawhats** | WIT Solapur

> *"59.1% of fraud funds are never recovered. We're fixing that."*

---

<p align="center">
  <strong>TraceBack</strong> — Private advisory platform · Not a law firm · Not affiliated with any government body<br>
  © 2026 TraceBack. Built for India's 3.24 crore cybercrime victims.
</p>
