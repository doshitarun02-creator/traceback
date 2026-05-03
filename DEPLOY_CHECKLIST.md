# TraceBack Production Deployment Checklist (Render + MongoDB Atlas)
================================================================

Follow these steps to deploy the TraceBack backend and frontend to Render.

## 1. Database Setup (MongoDB Atlas)
- [ ] Create a new Cluster on MongoDB Atlas.
- [ ] Network Access: Add `0.0.0.0/0` (Allow all IP addresses) to the IP Whitelist.
- [ ] Database Access: Create a user with `readWriteAnyDatabase` privileges.
- [ ] Connection String: Copy the SRV string (e.g., `mongodb+srv://<user>:<password>@cluster.mongodb.net/traceback`).

## 2. External Services
- [ ] **Google Gemini API**: Obtain API key from Google AI Studio.
- [ ] **Cloudinary**: Create account and get `CLOUDINARY_URL` or individual API keys.
- [ ] **Flask-Mail**: Set up an SMTP server (e.g., SendGrid, Gmail App Password).

## 3. Environment Variables (Render Dashboard)
Set these in the Render "Environment" tab:
- `FLASK_APP`: `run.py`
- `FLASK_ENV`: `production`
- `MONGO_URI`: `mongodb+srv://...`
- `JWT_SECRET_KEY`: `(generate a long random string)`
- `GEMINI_API_KEY`: `(your gemini key)`
- `CLOUDINARY_CLOUD_NAME`: `...`
- `CLOUDINARY_API_KEY`: `...`
- `CLOUDINARY_API_SECRET`: `...`
- `MAIL_SERVER`: `...`
- `MAIL_PORT`: `587`
- `MAIL_USERNAME`: `...`
- `MAIL_PASSWORD`: `...`
- `MAIL_DEFAULT_SENDER`: `noreply@traceback.in`

## 4. Render Web Service Configuration
- [ ] **Build Command**: `pip install -r requirements.txt`
- [ ] **Start Command**: `gunicorn --config gunicorn.conf.py run:app`
- [ ] **Plan**: Recommended Starter plan (512MB RAM minimum for Gemini/Cloudinary processing).

## 5. Post-Deployment Verification
- [ ] Run `python seed.py` locally (pointing to production MONGO_URI) to populate experts and admin.
- [ ] Visit `https://your-app.onrender.com/health` to verify connectivity.
- [ ] Perform a test complaint submission via the frontend.

## 6. Performance & Security (Post-Launch)
- [ ] Configure `REDIS_URL` for `flask-limiter` if traffic scales.
- [ ] Set `SESSION_COOKIE_SECURE=True` in production config.
- [ ] Monitor logs for `AI Triage` failures or timeout errors.
