# ⛰️ TrekManager Pro - Trekking Management Application

TrekManager Pro is a comprehensive, role-based web application designed for adventure organizations to efficiently manage trekking routes, staff assignments, and participant bookings. It replaces manual spreadsheet coordination with a secure, centralized system that programmatically enforces operational boundaries and prevents slot overbooking.

## 🚀 Technical Framework Stack
This project has been built strictly adhering to the mandated framework specifications:
*   **Back-end:** Flask (Python 3 Web Framework)
*   **Front-end:** HTML5, CSS3, Bootstrap 5, and Jinja2 Templates
*   **Database:** SQLite via Flask-SQLAlchemy (No cloud or external DB engines used)
*   **Core Restriction:** 100% JavaScript-free implementation for all core features (all routing, forms, validations, and cascading logic run strictly on the server side).

---

## 📂 Project Directory Architecture
Ensure your local files follow this exact structural layout:
```text
trekking_app/
│
├── app.py                     # Core Application Entrypoint & Controllers
├── models.py                  # Database Models & Programmatic Seeding
├── static/
│   └── style.css              # Custom Global CSS Stylesheet (Safe Reset)
├── templates/                 # Jinja2 Layout Templates
│   ├── base.html              # Shared Shell Structure
│   ├── login.html             # Unified Sign-In Interface
│   ├── register.html          # Registration Portal
│   ├── admin_dashboard.html   # Admin Operations Panel
│   ├── staff_dashboard.html   # Trek Staff Coordination Panel
│   └── user_dashboard.html    # Trekker Booking Interface
└── instance/                  # (Auto-generated) Local SQLite Storage Folder
```
---

## 🛠️ Local Environment Setup & Execution

Follow these step-by-step instructions to boot up and test the application locally:

### 1. Initialize the Working Workspace
Open your terminal inside the root project folder and configure a clean Python virtual environment:
```bash
# Create the virtual environment
python3 -m venv venv

# Activate the environment
# On macOS/Linux:
source venv/bin/activate
# On Windows (Command Prompt):
venv\Scripts\activate
```
### Install Dependencies
Install the required micro-framework components:
```bash
pip install Flask Flask-SQLAlchemy
```
### Run the Web App Engine
Launch the Flask development server. The application will programmatically create the SQLite database file (instance/trekking.db) and auto-seed the default administrator profile:
```bash
python app.py
```
Open your web browser and navigate to: ```http://127.0.0.1:5000/```
## 🔐 Default Admin Authentication Credentials
The superuser account is injected into the relational tables programmatically upon your very first system boot. Use these credentials to log in as the Administrator:
*   **Username:** `admin`
*   **Password:** `adminpassword`

---

## ✨ System Features Implemented

### 1. Admin Oversight
*   **Real-time Metrics:** Live numerical indicators tracking total users, staff, treks, and active bookings.
*   **Route Creation:** Full capability to initialize new trek entries with dates, duration, capacity, and difficulty parameters.
*   **Staff Assignment:** Direct drop-down routing tools to appoint certified field guides to pending routes.
*   **Security Controls:** Global privilege to approve or permanently blacklist user and guide accounts.
*   **Global Audit Ledger:** A complete tracking list displays all historical and current bookings across the system.

### 2. Trek Staff / Guide Functionalities
*   **Self-Registration:** Staff can self-register, moving into a secure `Pending` validation loop until verified by the Admin.
*   **Operational Control:** Guides can update slot availability limits and change trek states (*Open, Closed, Completed*).
*   **Roster Review:** Dynamically displays lists containing customer names and vital contact metadata for their assigned treks.

### 3. User / Trekker Flow
*   **Dynamic Search Engine:** Trekkers can filter active routes by direct text location match or difficulty grade.
*   **One-Click Booking Pass:** Secure slot validation rules prevent overbooking beyond capacity limits.
*   **Persistent User Profile & History:** Users can update their basic details and access a chronological tracking ledger of all their personal bookings.

### ⚡ Additional Features (Automated Cascading Ledger)
*   When an authorized Admin or Staff member sets a Trek's status indicator to **"Completed"**, a backend cascading loop automatically traverses related datasets. It converts all associated active user bookings from `Booked` to `Completed` simultaneously, maintaining perfect database consistency.
