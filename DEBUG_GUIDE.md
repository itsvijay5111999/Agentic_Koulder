# 🔍 Debugging Guide: Why Your Chatbot Isn't Responding on Render

## The Issue You're Facing

**Local:** Works perfectly ✅  
**Render:** No response, no error message ❌

---

## Root Cause

Your `.env` file is **NOT deployed to Render**. The code works locally because `python-dotenv` loads the `.env` file, but Render doesn't have it.

### What's Happening:

```
LOCAL ENVIRONMENT (Works):
├─ .env file exists
├─ python-dotenv loads it
├─ API keys are available
└─ Everything works ✓

RENDER ENVIRONMENT (Fails):
├─ No .env file (not deployed)
├─ No environment variables set in dashboard
├─ API keys are undefined
└─ Silent failure - hangs with no error ✗
```

---

## Solution: Two Parts

### Part 1: Don't Deploy `.env` to Render

1. Add to `.gitignore`:
```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Ignore .env file"
git push
```

2. If `.env` was already pushed, remove it:
```bash
git rm --cached .env
git commit -m "Remove .env from git"
git push
```

### Part 2: Add Environment Variables to Render Dashboard

1. Go to your Render service
2. Click **Environment** (in left sidebar)
3. Add these **exactly** (copy from your `.env`):

```
GROQ_API_KEY=your_actual_groq_api_key_here
SERPAPI_API_KEY=your_actual_serpapi_key_here
TAVILY_API_KEY=your_actual_tavily_key_here
YOUTUBE_API_KEY=your_actual_youtube_key_here
HUGGINGFACE_TOKEN=your_actual_huggingface_token_here
STABILITY_API_KEY=your_actual_stability_key_here
```

4. Click **Save**
5. Go to **Deploy** → **Manual Deploy**
6. Wait 3-5 minutes

---

## How to Debug: Check Render Logs

I've added detailed logging to help you debug. Here's what to look for:

### Step 1: Redeploy with New Code
```bash
git push  # Deploy the updated code with logging
```

### Step 2: Open Render Logs
1. Go to your Render service
2. Click **Logs** (top right)
3. Watch as the app starts

### Step 3: Look for These Lines

**If environment variables are set:**
```
[INIT] GROQ_API_KEY set: ✓
[INIT] SERPAPI_API_KEY set: ✓
```

**If environment variables are MISSING:**
```
[INIT] GROQ_API_KEY set: ✗ MISSING
[INIT] SERPAPI_API_KEY set: ✗ MISSING
```

### Step 4: Ask a Question and Watch Logs

When you ask a question on the Render app, look for:

```
[DEBUG] Starting stream for prompt: What is AI?...
[DEBUG] Using thread_id: abc123...
[DEBUG] Calling chatbot.stream()...
[DEBUG] Received chunk from: tools_node
[DEBUG] Received chunk from: chat_node
```

If it says `[ERROR]` instead, copy that error message.

---

## Common Debug Scenarios

### Scenario 1: Environment Variables Missing
```
[INIT] GROQ_API_KEY set: ✗ MISSING
[INIT] SERPAPI_API_KEY set: ✗ MISSING
```
**Fix:** Add them to Render Environment dashboard

### Scenario 2: Import Error
```
[INIT] Import failed: ModuleNotFoundError: No module named 'langgraph'
```
**Fix:** Check `requirements.txt` has all dependencies

### Scenario 3: API Key Invalid
```
[ERROR] Stream failed!
[ERROR] Error type: AuthenticationError
[ERROR] Error message: Invalid API key
```
**Fix:** Regenerate API keys from provider websites

### Scenario 4: Hangs (Nothing in Logs)
```
[INIT] ✓ All imports successful
[DEBUG] Starting stream...
(nothing after this)
```
**Possible fixes:**
- Wait 60 seconds (Render free tier cold start is slow)
- Check if Render free tier ran out of compute hours
- Restart the service

---

## Quick Checklist

- [ ] Added environment variables to Render dashboard
- [ ] Removed `.env` from git (or added to `.gitignore`)
- [ ] Redeployed the app
- [ ] Waited 5+ minutes for deployment
- [ ] Checked Render logs for `[INIT]` messages
- [ ] Asked a test question and watched logs
- [ ] Looked for `[ERROR]` or `[DEBUG]` messages

---

## After Redeploying

1. Give it **5 minutes** to fully deploy
2. Open the Render app URL
3. Ask: "What is AI?" (simple test)
4. Wait up to **60 seconds** for response
5. Check logs for errors

---

## If Still Not Working

1. Copy the **exact error message** from Render logs
2. Check if `[INIT]` shows API keys are set
3. Verify API keys are correct (no typos, no extra spaces)
4. Try regenerating the API keys
5. Restart the Render service (Manual Deploy)

Good luck! The logs will tell you exactly what's wrong. 🚀
