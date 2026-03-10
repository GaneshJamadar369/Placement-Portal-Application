# IITM BS Degree Placement Portal

A comprehensive, full-stack placement management system designed specifically for the IIT Madras BS Degree program. This portal streamlines the entire recruitment lifecycle by uniquely connecting Students, Companies, and Administrators under one unified platform.

## 🚀 Features

### For Students
* **Dynamic Profiles:** Manage personal information, CGPA, branch, and upload secure resumes (PDF/DOC) with UUID parsing.
* **Cover Letters:** Maintain and dynamically attach custom cover letter templates to active applications.
* **Browse Drives:** Discover active placement opportunities using advanced filtering (salary range, company sector, job type).
* **Application Tracking:** Monitor application statuses (Applied → Shortlisted → Interview Scheduled → Selected/Rejected) in real-time.

### For Companies
* **Recruitment Dashboard:** Post new placement drives, specify job roles, position count, and minimum CGPA criteria.
* **Application Lifecycle Management:** View incoming applications, safely download student resumes, read cover letters, and efficiently move candidates through the hiring pipeline.
* **Automated Notifications:** Automatically trigger native in-app notifications and email dispatches when updating candidate statuses.

### For Administrators
* **Centralized Analytics:** Interactive `Chart.js` dashboard visualizing placement trends (12-month series), branch distribution, salary brackets, and active candidate funnels.
* **Drive Verification:** Review and approve/reject pending company profiles and placement drives to ensure platform integrity.
* **Data Export:** Instantly generate and download CSV reports containing successfully placed student metrics for institutional records.

## 🛠️ Technology Stack

* **Backend Framework:** Python Flask
* **Database:** SQLite & SQLAlchemy (ORM)
* **Frontend Languages:** Vanilla HTML5, CSS3, JavaScript
* **Styling Library:** Tailwind CSS (via CDN)
* **Animations:** AOS (Animate On Scroll)
* **Forms & Security:** Flask-WTF, Werkzeug (Secure File Uploads), Flask-Login, bcrypt hashing
* **Email Dispatching:** Flask-Mail

## 📥 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/GaneshJamadar369/Placement-Portal-Application.git
   cd Placement-Portal-Application
   ```

2. **Create and activate a virtual environment**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the Database**
   ```bash
   # Start a Python shell
   python
   
   >>> from app import db, create_app
   >>> app = create_app()
   >>> app.app_context().push()
   >>> db.create_all()
   >>> exit()
   ```

5. **Run the Application**
   ```bash
   python app.py
   ```
   *The server will start locally on `http://127.0.0.1:5000`*

## 📁 Architecture Overview

* `app.py` – Core logic, application factory, and routing functions.
* `/models/` – SQLAlchemy schemas defining `User` polymorphism (`Student`, `Company`, `Admin`), `PlacementDrive`, `Application`, and `Notification`.
* `/templates/` – Jinja2 HTML templates broken into functional blueprints.
* `/uploads/` – Secure local storage directory for student resumes.
* `instance/placement.db` – The relational SQLite database.

## 📜 License
This project was built for the IITM BS Degree S-Grade Evaluation. All rights reserved.
