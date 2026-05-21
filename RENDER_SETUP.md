# ✅ Render Deployment Checklist

## Before Deploying

### 1. **Test Locally** ✓
```bash
# Install dependencies
pip install -r requirements.txt

# Run diagnosis
python diagnose.py

# Test the app
streamlit run stream_resume_bot_test.py
```

**❌ If it fails locally → It will fail on Render**

---

## Deploying to Render

### Step 1: Prepare Your Repository
- [ ] All files committed to Git (GitHub, GitLab, etc.)
- [ ] `.gitignore` includes `.env` and `*.db3`
- [ ] `requirements.txt` is up to date
- [ ] No hardcoded API keys in code

### Step 2: Create Render Service
1. Go to https://render.com
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Fill in:
   - **Name**: `chatbot` (or any name)
   - **Environment**: `Python 3.10`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run stream_resume_bot_test.py --server.port=10000 --server.address=0.0.0.0`

### Step 3: Add Environment Variables ⚠️ **IMPORTANT**
1. In Render dashboard, go to **Environment**
2. Add these variables:

```
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxx
SERPAPI_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
YOUTUBE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx (optional)
TAVILY_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxx (optional)
```

**⚠️ DO NOT include these in git** - Always use Render's Environment Variables dashboard

### Step 4: Deploy
1. Click **Create Web Service**
2. Wait for build to complete (2-5 minutes)
3. Check logs for errors

---

## If It Still Doesn't Work

### 1. **Check Logs** 🔍
   - Click **Logs** button in Render dashboard
   - Look for red error messages
   - Copy the error and search for solutions

### 2. **Check Environment Variables** 🔑
   - Go to **Environment** in Render
   - Verify all keys are there
   - Verify no extra spaces
   - Try regenerating the API keys

### 3. **Restart the Service** 🔄
   - Go to **Deploy** → **Manual Deploy**
   - Wait 30+ seconds for startup

### 4. **Check Streamlit Config** ⚙️
   - Verify `--server.port=10000` and `--server.address=0.0.0.0`
   - These are required for Render

---

## Common Issues & Fixes

| Problem | Fix |
|---------|-----|
| "Could not import backend" | Check backend.py exists in root. Check Render logs. |
| "API key not found" | Add keys to Render Environment Variables (not code) |
| "ModuleNotFoundError" | Update requirements.txt and redeploy |
| "Timeout" | Render free tier is slow. Wait 30+ seconds. |
| "No response when typing" | Check Render logs. API key issue likely. |
| "Error building" | Check build command. Requirements.txt might have issues. |

---

## Free vs Paid Tiers

**Render Free Tier:**
- First response takes 30-60 seconds ⏱️
- Auto-spins down after 15 min inactivity
- Limited compute power
- **Good for testing only**

**Render Paid Tier ($7/month+):**
- Instant responses ⚡
- Always running
- Better performance

---

## Getting Help

1. **Check Render logs** - Most issues are explained there
2. **Run diagnosis locally** - `python diagnose.py`
3. **Verify API keys** - Use fresh API keys from providers
4. **Check GitHub Issues** - Similar problems might be solved

---

## Next Steps

✅ Once deployed successfully:
- Share the Render URL with others
- Monitor logs for errors
- Add better error tracking (optional: Sentry, LogRocket)
- Consider upgrading to paid tier for production use
