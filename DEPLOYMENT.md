# 🚀 Deployment Guide

This guide will help you deploy the Community Feed application to production.

## 📋 Prerequisites

1. **GitHub Account** (already done ✅)
2. **Railway Account** - Sign up at https://railway.app
3. **Vercel Account** - Sign up at https://vercel.com

---

## 🔧 Backend Deployment (Railway)

Railway is perfect for Django + PostgreSQL deployment.

### Step 1: Create Railway Project

1. Go to https://railway.app
2. Click "Start a New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository: `gayathri-1911/Community-Feed`
5. Railway will auto-detect Django

### Step 2: Add PostgreSQL Database

1. In your Railway project, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create a PostgreSQL instance
4. The `DATABASE_URL` environment variable will be set automatically

### Step 3: Configure Environment Variables

In Railway project settings, add these environment variables:

```
SECRET_KEY=your-secret-key-here-generate-a-strong-one
DEBUG=False
ALLOWED_HOSTS=your-railway-domain.railway.app
CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-railway-domain.railway.app,https://your-vercel-app.vercel.app
DJANGO_SETTINGS_MODULE=config.settings
```

### Step 4: Deploy

1. Railway will automatically deploy when you push to GitHub
2. Your backend will be available at: `https://your-app.railway.app`
3. Create a superuser:
   ```bash
   railway run python backend/manage.py createsuperuser
   ```

---

## 🎨 Frontend Deployment (Vercel)

### Step 1: Update API URL

Before deploying, update the API URL in `frontend/src/api.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
```

### Step 2: Deploy to Vercel

1. Go to https://vercel.com
2. Click "Add New" → "Project"
3. Import your GitHub repository: `gayathri-1911/Community-Feed`
4. Configure:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Step 3: Add Environment Variables

In Vercel project settings, add:

```
VITE_API_URL=https://your-railway-domain.railway.app/api
```

### Step 4: Deploy

1. Click "Deploy"
2. Vercel will build and deploy your frontend
3. Your app will be available at: `https://your-app.vercel.app`

---

## 🔄 Update Backend CORS Settings

After deploying frontend, update Railway environment variables:

```
CORS_ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
CSRF_TRUSTED_ORIGINS=https://your-railway-domain.railway.app,https://your-vercel-app.vercel.app
```

Then redeploy the backend.

---

## ✅ Post-Deployment Checklist

- [ ] Backend is running on Railway
- [ ] PostgreSQL database is connected
- [ ] Frontend is deployed on Vercel
- [ ] CORS settings are configured correctly
- [ ] CSRF settings allow frontend domain
- [ ] Superuser account created
- [ ] Sample data populated (optional)
- [ ] Test login functionality
- [ ] Test creating posts and comments
- [ ] Test like functionality
- [ ] Verify leaderboard updates

---

## 🐛 Troubleshooting

### CORS Errors
- Ensure `CORS_ALLOWED_ORIGINS` includes your Vercel URL
- Check that `CORS_ALLOW_CREDENTIALS = True` in settings

### CSRF Errors
- Add your Railway and Vercel domains to `CSRF_TRUSTED_ORIGINS`
- Ensure frontend is sending CSRF tokens

### Database Connection Issues
- Verify `DATABASE_URL` is set in Railway
- Check PostgreSQL service is running

### Static Files Not Loading
- Run `python manage.py collectstatic` in Railway
- Ensure `STATIC_ROOT` is configured

---

## 🔐 Security Notes

1. **Never commit** `.env` files or secrets to GitHub
2. **Generate a strong** `SECRET_KEY` for production
3. **Set** `DEBUG=False` in production
4. **Use HTTPS** for all production URLs
5. **Regularly update** dependencies for security patches

---

## 📊 Monitoring

- **Railway**: Check logs in Railway dashboard
- **Vercel**: Check deployment logs in Vercel dashboard
- **Database**: Monitor PostgreSQL usage in Railway

---

## 🎉 You're Done!

Your Community Feed application is now live!

- **Frontend**: https://your-app.vercel.app
- **Backend API**: https://your-railway-domain.railway.app/api
- **Admin Panel**: https://your-railway-domain.railway.app/admin

Share your deployed app and enjoy! 🚀
