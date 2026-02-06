# Deployment Guide

This project is set up for easy deployment using **Render** (Backend & Database) and **Vercel** (Frontend).

## 1. Backend & Database (Render)

We have created a `render.yaml` Blueprint file at the root of the project to automate the backend deployment.

1.  Push your code to **GitHub** (or GitLab/Bitbucket).
2.  Log in to [Render](https://dashboard.render.com/).
3.  Click **New +** -> **Blueprint**.
4.  Connect your repository.
5.  Render will detect the `render.yaml` file.
6.  Click **Apply**.
    *   This will create a **PostgreSQL Database** (Free Tier).
    *   This will create a **Python Web Service** (Free Tier).
7.  Wait for the deployment to succeed.
8.  **Copy the Backend URL**. It will look like: `https://financial-health-backend.onrender.com`.

## 2. Frontend (Vercel)

1.  Log in to [Vercel](https://vercel.com).
2.  Click **Add New** -> **Project**.
3.  Import your GitHub repository.
4.  **Important**: Configure the **Project Settings**:
    *   **Root Directory**: Click "Edit" and select `frontend`.
    *   **Framework Preset**: It should auto-detect "Vite".
    *   **Environment Variables**:
        *   Key: `VITE_API_URL`
        *   Value: *Paste your Render Backend URL here* (e.g., `https://financial-health-backend.onrender.com`).
        *   *Note: Do not add a trailing slash `/`.*
5.  Click **Deploy**.

## 3. Verification

1.  Open your Vercel App URL.
2.  Upload a CSV/XLSX file.
3.  The frontend should successfully communicate with the backend, save data to the Render database, and show the dashboard.

## Local Development vs Production

*   **Local**: The app uses `http://localhost:8000` by default (set in `Upload.tsx` fallback).
*   **Production**: The app uses `VITE_API_URL` environment variable.
