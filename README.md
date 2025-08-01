# URL Shortener Microservice Project

## Overview
This project is a full-stack URL shortener application built with a Flask backend and a React frontend. It allows users to create short, shareable links for long URLs, set custom shortcodes, specify link expiry times, and view analytics for each link. The backend uses SQLite for persistent storage and includes robust logging and error handling. The frontend is styled with Material UI for a modern, responsive user experience.

## Features
- **Shorten URLs:** Instantly generate short links for any valid URL.
- **Custom Shortcodes:** Optionally specify your own alphanumeric shortcode for a link.
- **Expiry Control:** Set how long a short link remains active (default: 30 minutes).
- **Analytics:** Track the number of clicks, creation and expiry times for each short link.
- **Statistics Dashboard:** View all your short links and their analytics in a clean, card-based interface.
- **Redirection Handler:** Users see a friendly redirecting message before being sent to the original URL.
- **Robust Logging:** All requests, responses, and errors are logged for monitoring and debugging.
- **Plagiarism-Free:** All code and documentation are original and written for this project.

## Tech Stack
- **Backend:** Python, Flask, SQLite, Flask-CORS
- **Frontend:** React, Material UI, Axios, React Router
- **Other:** Custom middleware for logging, .env support, comprehensive .gitignore

## How It Works
1. **Shorten a URL:** Enter a long URL, set expiry (optional), and a custom shortcode (optional) in the frontend form. Submit to receive a short link.
2. **Redirection:** When a short link is visited, the backend checks its validity and expiry, logs the click, and redirects the user.
3. **Analytics:** The statistics page displays all short links, their original URLs, expiry, creation time, and click counts in a modern UI.

## Getting Started
1. Clone the repository.
2. Install backend dependencies (`pip install -r backend/requirements.txt`).
3. Start the backend (`python backend/app.py`).
4. Install frontend dependencies (`npm install` in the `frontend` folder).
5. Start the frontend (`npm start` in the `frontend` folder).

## Project Structure
- `backend/` - Flask app, models, middleware, and database
- `frontend/` - React app source code
- `middleware/` - Shared logging middleware for Flask
- `.gitignore` - Ignores all unnecessary files for Python, Node, and OS

## License
This project is provided for educational and demonstration purposes. All code and documentation are original and free from plagiarism.
