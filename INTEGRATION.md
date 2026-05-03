# INTEGRATION.md — TraceBack Backend Setup

> Flask + MongoDB + Gemini backend integration guide for developers.

---

## 1. First-Time Setup

```bash
# Clone the repository
git clone https://github.com/your-org/traceback-backend.git
cd traceback-backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # macOS/Linux
# venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

Edit `.env` with your credentials (see Section 2).

---

## 2. Fill Your .env

| Variable | Where to Get It | Example |
|---|---|---|
| `MONGODB_URI` | MongoDB Atlas → Your Cluster → Connect → Drivers | `mongodb+srv://user:pass@cluster0.abc12.mongodb.net/traceback` |
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) → Get API Key | `AIzaSyAbc123XYZ...` |
| `CLOUDINARY_CLOUD_NAME` | [cloudinary.com](https://cloudinary.com) → Dashboard → Account Details | `my-cloud-name` |
| `CLOUDINARY_API_KEY` | cloudinary.com → Dashboard → API Keys | `123456789012345` |
| `CLOUDINARY_API_SECRET` | cloudinary.com → Dashboard → API Keys | `abcDEFghiJKL_mno-PQR` |
| `MAIL_USERNAME` | Your Gmail address | `yourapp@gmail.com` |
| `MAIL_PASSWORD` | Gmail → Google Account → Security → 2-Step Verification → App Passwords | `abcd efgh ijkl mnop` |
| `SECRET_KEY` | Generate locally (see below) | `3f8a2c1d...64-char hex` |
| `JWT_SECRET_KEY` | Generate locally (see below) | `9b4e7d2f...64-char hex` |

**Generate SECRET_KEY and JWT_SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
# Run twice — use one value for SECRET_KEY, another for JWT_SECRET_KEY
```

---

## 3. MongoDB Atlas Setup

1. Go to [cloud.mongodb.com](https://cloud.mongodb.com) → **Create a new project**
2. Click **Build a Database** → choose **M0 Free Tier** → select your region
3. Under **Database Access** → **Add New Database User**:
   - Username: `traceback_user`
   - Password: a strong password (save it)
   - Role: **Read and write to any database**
4. Under **Network Access** → **Add IP Address** → enter `0.0.0.0/0` *(allows all IPs — for development only)*
5. Go to your cluster → **Connect** → **Drivers** → copy the URI

Your URI format:
```
mongodb+srv://traceback_user:<password>@cluster0.xxxxx.mongodb.net/traceback?retryWrites=true&w=majority
```

Replace `<password>` with your actual DB user password and paste into `MONGODB_URI` in `.env`.

---

## 4. Run Seed Data

```bash
python seed.py
```

**Expected output:**

```
[+] Connected to MongoDB: traceback
[+] Seeding experts...     OK (12 records inserted)
[+] Seeding categories...  OK (8 records inserted)
[+] Seeding sample cases...OK (5 records inserted)
[+] Seed complete.
```

If you see `MongoServerError`, verify your `MONGODB_URI` in `.env` (see Section 8).

---

## 5. Run Locally

```bash
python run.py
```

Server starts at `http://localhost:5000`.

**Test endpoints:**

| Method | URL | Expected Response |
|---|---|---|
| `GET` | `/health` | `{"status": "ok"}` |
| `POST` | `/api/auth/register` | `{"success": true, "user_id": "<id>"}` |
| `POST` | `/api/triage/analyze` | `{"triage_result": {...}}` |
| `GET` | `/api/experts` | `{"experts": [...]}` |
| `GET` | `/api/cases/stats/live` | `{"total_complaints_today": N, ...}` |

Quick health check:
```bash
curl http://localhost:5000/health
```

---

## 6. Connect Frontend to Backend

### Replace Mock Form Submit in `traceback_v1.html`

Find your mock form submit handler and replace it with:

```js
// Replace mock form submit
document.getElementById('complaint-form').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData(e.target);

  const res = await fetch('http://localhost:5000/api/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(Object.fromEntries(formData)),
  });

  const data = await res.json();

  if (data.success) {
    console.log('Registered. User ID:', data.user_id);
    // redirect or show success UI
  } else {
    console.error('Registration failed:', data.message);
  }
});
```

### Load Live Stats from `/api/cases/stats/live`

```js
// Load live stats on page load
async function loadLiveStats() {
  const res = await fetch('http://localhost:5000/api/cases/stats/live');
  const data = await res.json();

  document.getElementById('stat-today').textContent = data.total_complaints_today ?? 0;
  document.getElementById('stat-resolved').textContent = data.resolved_today ?? 0;
  document.getElementById('stat-pending').textContent = data.pending ?? 0;
}

document.addEventListener('DOMContentLoaded', loadLiveStats);
```

> **Note:** Update the base URL to your deployed Render URL once deployed (Section 7).

---

## 7. Deploy to Render

1. **Push to GitHub** — ensure `.env` is in `.gitignore` (never commit secrets)
2. Go to [render.com](https://render.com) → **New** → **Web Service**
3. **Connect your GitHub repo** and select the `traceback-backend` repository
4. Set **Build Command**:
   ```
   pip install -r requirements.txt
   ```
5. Set **Start Command**:
   ```
   gunicorn run:app
   ```
6. Under **Environment** → **Add Environment Variables** — add every key from Section 2
7. Click **Create Web Service** → Render builds and deploys automatically

Your live URL will be: `https://traceback-backend.onrender.com`

Update `fetch()` calls in your frontend to use this URL instead of `localhost:5000`.

---

## 8. Common Errors + Fixes

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'flask'` | Dependencies not installed | Run `pip install -r requirements.txt` inside your virtualenv |
| `MongoServerError: Authentication failed` | Wrong URI or bad credentials | Check `MONGODB_URI` in `.env` — verify username, password, and cluster URL |
| `401 Unauthorized` | Missing or invalid JWT token | Add header: `Authorization: Bearer <token>` — get token from `/api/auth/login` first |
| `Gemini quota error / 429 Too Many Requests` | API rate limit hit | Check usage at [aistudio.google.com](https://aistudio.google.com) → usage dashboard; wait or upgrade plan |
| `413 Request Entity Too Large` | File upload exceeds limit | Max file size is **10MB** — compress or resize before uploading |
