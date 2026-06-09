# 🔗 LinkSnip – URL Shortener & Analytics Dashboard

A full-stack URL shortener built with **Python, Flask, SQLite, and JavaScript** — featuring a live analytics dashboard with real-time click tracking.

## Features
- ✂️ Shorten any long URL instantly
- 🏷️ Custom aliases / slugs
- ⏰ Link expiry dates
- 📷 QR code export for every link
- 📊 Live analytics dashboard (click counts, charts)
- 🔁 Real-time chart updates every 10 seconds

## Tech Stack
- **Backend:** Python, Flask, SQLite
- **Frontend:** HTML5, CSS3, JavaScript, Chart.js
- **Other:** qrcode library for QR generation

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
python app.py

# 3. Open in browser
http://127.0.0.1:5000
```

## Project Structure
```
url-shortener/
├── app.py               # Flask backend & REST API
├── requirements.txt     # Python dependencies
├── urls.db              # SQLite database (auto-created)
└── templates/
    ├── index.html       # Main shortener UI
    └── analytics.html   # Analytics dashboard
```

## Screenshots
> Home page lets you shorten URLs, add custom slugs, set expiry, and download QR codes.  
> Analytics page shows bar + doughnut charts with per-link click counts updated live.
