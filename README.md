# LostLink

LostLink is a campus lost-and-found management system built for the Asian School of Management and Technology (ASMT), Kathmandu. The project provides students, staff, and administrators with a centralized place to report missing items, locate found belongings, review claims, and manage status workflows.

## Features

- Lost and found item reporting
- Search and filtering across item records
- Responsive item listing pages
- Database-backed statistics and recent reports
- Item detail views
- Modular Flask application structure
- Foundation for user accounts, claims, admin workflows, and notifications

## Technology Stack

- Python
- Flask
- SQLAlchemy
- SQLite for local development by default
- SQL Server compatible configuration via environment variable
- Jinja2 templates
- HTML, CSS, and JavaScript

## Requirements

- Python 3.10+
- pip
- Virtual environment tool (optional but recommended)

## Installation

1. Clone or open the project folder.
2. Create and activate a virtual environment.
3. Install the dependencies.
4. Configure environment variables.
5. Initialize the database.
6. Run the app.

### Virtual environment setup

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Dependency installation

```bash
pip install -r requirements.txt
```

### Environment configuration

Copy the sample environment file and update it as needed:

```bash
copy .env.example .env
```

Set your configuration values in `.env`.

By default, the project uses a local SQLite database file stored in `database/lostlink.db`.
For a SQL Server setup, update `DATABASE_URL` to a valid SQL Server connection string.

### Database initialization

The app will automatically create database tables on startup. For development, the seed script adds sample categories and example items if the database is empty.

For local development, a staff account is seeded automatically: `admin@lostlink.edu` with password `Admin123!`. Set `DEMO_ADMIN_EMAIL` and `DEMO_ADMIN_PASSWORD` before starting the app to use different credentials. Change these development defaults before exposing the application to other users.

### Running the application

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in a browser.

## Free deployment on PythonAnywhere

PythonAnywhere's free Beginner account supports one Python web app at `YOUR_USERNAME.pythonanywhere.com`. The app's SQLite database and uploaded photos live in your account's persistent home directory, so they survive web-app reloads. The free tier has restricted outbound internet, a 512 MB private-storage limit, and limited CPU; this app does not need outbound services at runtime. Check [current plan details](https://www.pythonanywhere.com/pricing/).

1. Create a free Beginner account on [PythonAnywhere](https://www.pythonanywhere.com/registration/register/beginner/).
2. In a PythonAnywhere Bash console, create an SSH key with `ssh-keygen -t ed25519`, then display the public key with `cat ~/.ssh/id_ed25519.pub`. Add that public key to GitHub under **Settings → SSH and GPG keys**. Never share the private key file.
3. Clone the private repository and install its dependencies:

	```bash
	git clone git@github.com:SARBESH-DHAKAL/lostlink.git ~/lostlink
	mkvirtualenv --python=/usr/bin/python3.11 lostlink-venv
	pip install -r ~/lostlink/requirements.txt
	```

4. In PythonAnywhere's **Web** tab, add a web app using **Manual configuration** and Python 3.11. Set its virtualenv to `/home/YOUR_USERNAME/.virtualenvs/lostlink-venv`.
5. Open the WSGI configuration file linked from the Web tab. Replace its contents with [deploy/pythonanywhere_wsgi.py](deploy/pythonanywhere_wsgi.py), replacing `YOUR_USERNAME` and both secret placeholders. Generate the Flask secret in the PythonAnywhere Bash console with `python -c "import secrets; print(secrets.token_hex(32))"`; choose a different strong password for the admin account.
6. Save the WSGI file and reload the web app. Visit `https://YOUR_USERNAME.pythonanywhere.com` and sign in as `admin@lostlink.edu`.

This option is free but intended for demos and small projects, not production workloads. Keep the repository private, and do not put real secrets in files committed to GitHub.

## Deploying to Render

The included `render.yaml` Blueprint provisions the Flask web service, PostgreSQL database, and persistent storage for uploaded photos. At current published rates, this smallest durable setup is approximately $13.25/month: $7 for the web service, $6 for PostgreSQL, and $0.25 for the 1 GB upload disk. Prices and usage charges can change; review [Render pricing](https://render.com/pricing) before provisioning.

1. Create an empty, private GitHub repository.
2. From this project folder, add and push the files:

	```powershell
	git add .
	git commit -m "Prepare LostLink for Render deployment"
	git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
	git push -u origin main
	```

	`.gitignore` excludes `.env`, the virtual environment, local database, and uploaded files.
3. In Render, choose **New +** then **Blueprint**, connect the GitHub repository, and select `render.yaml`.
4. When prompted, set a strong, unique `DEMO_ADMIN_PASSWORD`. Render generates `SECRET_KEY` automatically.
5. Review the resource charges and create the resources. When deployment finishes, open the service's `onrender.com` URL and sign in as `admin@lostlink.edu` to review claims.

The deployed database and uploaded photos persist across restarts and deploys. Do not commit secrets, local database files, or user uploads to GitHub.

## Project structure

```text
LostLink/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── README.md
├── database/
│   ├── lostlink.db
│   └── schema.sql
├── models/
│   ├── __init__.py
│   ├── category.py
│   ├── claim.py
│   ├── item_report.py
│   ├── notification.py
│   └── user.py
├── routes/
│   ├── __init__.py
│   └── main.py
├── services/
│   └── seed.py
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── errors/
│   │   ├── 404.html
│   │   ├── 403.html
│   │   └── 500.html
│   └── partials/
├── uploads/
└── .env
```

## Notes

This project is intentionally structured for incremental development. The current phase implements the project foundation, base layout, and working database-backed homepage.

## Demo / sample data

Sample records are inserted only when the database is empty so the app has realistic categories and example items for local testing.
