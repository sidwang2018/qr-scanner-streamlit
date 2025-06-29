# QR Code Scanner - Streamlit Cloud Deployment Guide

This guide will walk you through deploying the QR Code Scanner app to Streamlit Cloud.

## Prerequisites

1. **GitHub Account**: You need a GitHub account to host your code
2. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **Google Service Account**: You need the `service_account.json` file for Google Sheets integration

## Step-by-Step Deployment Instructions

### Step 1: Prepare Your Repository

1. **Create a GitHub Repository**:
   - Go to [github.com](https://github.com)
   - Click "New repository"
   - Name it something like `qr-scanner-streamlit`
   - Make it public (required for free Streamlit Cloud)
   - Don't initialize with README (we'll upload our files)

2. **Upload Your Files**:
   - Upload these files to your GitHub repository:
     - `web_qr_scanner_advanced.py` (rename to `streamlit_app.py`)
     - `requirements.txt`
     - `service_account.json`
     - `.streamlit/config.toml`
     - `README.md`

### Step 2: Configure Google Service Account

1. **Set up Google Cloud Project** (if not already done):
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create a new project or select existing one
   - Enable Google Sheets API and Google Drive API

2. **Create Service Account**:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Download the JSON key file
   - Rename it to `service_account.json`

3. **Share Google Sheet**:
   - Open your Google Sheet
   - Share it with the service account email (found in the JSON file)
   - Give it "Editor" permissions

### Step 3: Deploy to Streamlit Cloud

1. **Sign in to Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account

2. **Deploy Your App**:
   - Click "New app"
   - Select your GitHub repository
   - Set the main file path to: `streamlit_app.py`
   - Click "Deploy!"

3. **Configure Secrets** (if needed):
   - In your Streamlit Cloud app settings
   - Go to "Secrets" tab
   - Add your Google service account credentials if needed

### Step 4: Test Your Deployment

1. **Access Your App**:
   - Your app will be available at: `https://your-app-name.streamlit.app`

2. **Test QR Scanning**:
   - Use the QR scanner to test functionality
   - Check if data is being posted to Google Sheets
   - Verify the log file is working

## File Structure for Deployment

```
your-repo/
├── streamlit_app.py          # Main app file (renamed from web_qr_scanner_advanced.py)
├── requirements.txt          # Python dependencies
├── service_account.json      # Google service account credentials
├── .streamlit/
│   └── config.toml          # Streamlit configuration
└── README.md                # Project documentation
```

## Important Notes

1. **Security**: Never commit sensitive credentials to public repositories
2. **Google Sheet ID**: Make sure the `SHEET_ID` in your code is correct
3. **Service Account**: Ensure the service account has proper permissions
4. **CORS**: The app is configured to handle CORS issues in Streamlit Cloud

## Troubleshooting

### Common Issues:

1. **Import Errors**: Check that all dependencies are in `requirements.txt`
2. **Google Sheets Access**: Verify service account permissions
3. **CORS Issues**: The config.toml should handle this
4. **Camera Access**: Users need to allow camera permissions in their browser

### Getting Help:

- Check Streamlit Cloud logs for error messages
- Verify your Google Sheets API is enabled
- Test locally first with `streamlit run streamlit_app.py`

## Local Testing

Before deploying, test locally:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Your app should be available at `http://localhost:8501` 