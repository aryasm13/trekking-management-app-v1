# Trekking Management Application

A web-based Trekking Management Application developed as part of the IIT Madras Modern Application Development I (MAD-1) Project.

## Project Description

This application manages trekking activities involving administrators, trek staff, and trekkers.

## Technologies Used

- Flask
- Jinja2
- HTML
- CSS
- Bootstrap
- SQLite

## How to Run the Project (Step-by-Step)

### 1. Prerequisites
- Python 3.8 or above installed on your system.

### 2. Extract & Open Project
Unzip the files and open the project directory in your terminal:
```bash
cd "23f3002123/trekking-management-app-v1"
```

### 3. Setup Virtual Environment
* **Windows (PowerShell)**:
  ```powershell
  python -m venv venv
  .\venv\Scripts\activate
  ```
* **macOS / Linux**:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```

### 4. Install Requirements
Run this command to install Flask and other dependencies:
```bash
pip install -r requirements.txt
```

### 5. Running the Application
Run the python app:
```bash
python app.py
```
This automatically initializes the database schema and seeds the default admin user.

Now open your browser and go to:
**http://127.0.0.1:5000**

---

## 🔑 Login Accounts for Demo

Run `python seed.py` to populate the database with demo accounts:

- **Admin Account (Pre-seeded)**:
  - Email: `admintrek@gmail.com`
  - Password: `Admin123`

- **Trek Staff Account (Seeded)**:
  - Email: `rohan.joshi@gmail.com` (Approved)
  - Email: `neha.gupta@gmail.com` (Approved)
  - Email: `vikram.singh@gmail.com` (Approved)
  - Email: `anjali.desai@gmail.com` (Approved)
  - Email: `sandeep.patil@gmail.com` (Pending)
  - Password: `Staff123` for all staff accounts.

- **Trekker Account (Seeded)**:
  - Email: `amit.sharma@gmail.com`
  - Email: `priya.patel@gmail.com`
  - Email: `rahul.verma@gmail.com`
  - Password: `Trekker123` for all trekker accounts.

---

## Troubleshooting

If you get `sqlalchemy.exc.OperationalError` (no such column):
1. Stop the server (`Ctrl + C`).
2. Delete the database file `instance/trek.db`.
3. Start the server again (`python app.py`).
This drops the old tables and builds a clean database.
