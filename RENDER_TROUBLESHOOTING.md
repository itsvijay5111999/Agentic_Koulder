# 🚀 Render Deployment Troubleshooting Guide

## Problem: Chatbot Not Responding on Render

Your app is deployed, but when you ask a question, **nothing happens**. Here's the fix:

---

## ✅ STEP 1: Check Environment Variables in Render Dashboard

Go to your Render service → **Environment** → Add these variables:

### Required Variables (Without these, nothing will work):

```
GROQ_API_KEY = gsk_xxxxxxxxxxxxxx
SERPAPI_API_KEY = xxxxxxxxxxxxxxxxxxxx
```

### Optional Variables (For full features):

```
YOUTUBE_API_KEY = xxxxxxxxxxxxxxxxxxxx
TAVILY_API_KEY = xxxxxxxxxxxxxxxxxxxx
```

---

## 🔑 How to Get API Keys:

### 1. **GROQ_API_KEY** (Required)
   - Go to https://console.groq.com/keys
   - Create an API key
   - Copy and paste it

### 2. **SERPAPI_API_KEY** (Required)
   - Go to https://serpapi.com/dashboard
   - Copy your API key

### 3. **YOUTUBE_API_KEY** (Optional - for YouTube search)
   - Go to https://developers.google.com/youtube/registering_an_application
   - Create a project and API key

### 4. **TAVILY_API_KEY** (Optional - for advanced search)
   - Go to https://app.tavily.com/home
   - Get your API key

---

## 🔍 STEP 2: Check Render Logs

1. Go to your Render service dashboard
2. Click **Logs** (top right)
3. Look for error messages
4. If you see `[ERROR]`, scroll up to see the full message

---

## 📝 STEP 3: Common Errors & Fixes

### Error: "Could not import backend"
- Check that `backend.py` and `langgraph_chatbot.py` are in the root directory
- Check Render logs for import errors

### Error: "API key not found" or "401 Unauthorized"
- Verify the API key in Render Environment Variables is correct
- Make sure there are no extra spaces
- Try regenerating the API key

### Error: "Network error" or "timeout"
- Render's free tier is slow - first response may take 30+ seconds
- Wait longer before assuming it failed
- Check Render logs to see if it's processing

### Error: "Model not found"
- Check `langgraph_chatbot.py` - verify the model name is correct
- The model `meta-llama/llama-4-scout-17b-16e-instruct` might not be available
- Try using `groq/mixtral-8x7b-32768` instead

---

## ⚡ STEP 4: Enable Better Debugging (Optional)

Add this to Render environment variables:

```
LANGCHAIN_DEBUG=true
LANGCHAIN_VERBOSE=true
```

This will show detailed logs (helps identify the problem).

---

## 🧪 STEP 5: Test Locally First

Before deploying to Render again, test locally:

```bash
python -m pip install -r requirements.txt
streamlit run stream_resume_bot_test.py
```

If it doesn't work locally, it won't work on Render.

---

## 📋 Final Checklist

- [ ] All API keys are added to Render environment variables
- [ ] API keys are valid (not expired)
- [ ] No extra spaces in API keys
- [ ] `backend.py` exists in root directory
- [ ] `langgraph_chatbot.py` exists in root directory
- [ ] `requirements.txt` has all dependencies
- [ ] Tested locally first

---

## 💡 Quick Fix Checklist

If the app still doesn't respond:

1. **Restart the Render service** (Deploy tab → Manual Deploy)
2. **Wait 30+ seconds** for first response (Render free tier is slow)
3. **Check the logs** carefully for error messages
4. **Verify all 2 required API keys** are in Environment Variables
5. **Ask with a simple question** like "hello" to test

---

## Still Not Working?

1. Check Render logs for exact error message
2. Copy the error and search GitHub issues
3. Verify `backend.py` and `langgraph_chatbot.py` have no errors
4. Test the backend locally: `python -c "from backend import chatbot; print('OK')"`

Good luck! 🚀
