# url-shortener-with-analytics

This is a Python-based URL shortener system that provides:

Shortened URLs with expiry.

Usage analytics (access count and logs).

A REST API for interaction.

Setup
Install Python 3.x and Flask.

Run python app.py to start the server.

Use the API endpoints to create, access, and analyze shortened URLs.

API Documentation
POST /shorten: Create a shortened URL.

GET /<short_url>: Redirect to the original URL.

GET /analytics/<short_url>: Retrieve analytics for a shortened URL.

Database
The SQLite database (url_shortener.db) will be created automatically. It contains two tables: urls and access_logs.

This implementation is modular and can be extended with additional features like password protection or a web interface.

# Working of the endpoints:

<img width="772" alt="Screenshot 2025-01-26 at 7 47 38 PM" src="https://github.com/user-attachments/assets/30d583ec-1c41-4b65-a6d1-cd3630e9e3a4" />

<img width="790" alt="Screenshot 2025-01-26 at 8 05 00 PM" src="https://github.com/user-attachments/assets/7710ed18-546f-44de-a630-69bd23ed56d9" />

<img width="784" alt="Screenshot 2025-01-26 at 8 06 52 PM" src="https://github.com/user-attachments/assets/8b741bef-f9c9-41d4-9d14-341c62f15263" />

Author: Suyash Dubey


