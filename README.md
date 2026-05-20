# Django Student Management System (SMS)

A professional, production-ready Django project implementing a complete Student Management System. Built with Clean Code principles, modern UI, and robust backend architecture.

## Features Included

- **Complete Authentication:** Login, Register, Logout, and full Password Reset flow via email.
- **Student CRUD:** Add, view, edit, and delete student records.
- **Media Handling:** Profile image uploads with dynamic file paths.
- **Dashboard:** Statistical overview, demographics, and recent activity.
- **Search System:** Case-insensitive search by name, email, or admission number.
- **Pagination:** Built-in Django pagination for large datasets.
- **Clean UI:** Bootstrap 5, responsive sidebar layout, and custom CSS.
- **Form Validation:** Both backend (Django forms) and frontend validation.
- **Custom Error Pages:** User-friendly 404 and 500 pages.

## Quick Start (Local Development)

1. **Activate Virtual Environment** (if you have one).
2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Environment Variables:**
   Copy the existing `.env` file (if you have it) or create one based on the template inside it. You must have `SECRET_KEY` and `DEBUG=True`.
4. **Apply Database Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
5. **Create an Admin User:**
   ```bash
   python manage.py createsuperuser
   ```
6. **Run the Development Server:**
   ```bash
   python manage.py runserver
   ```
7. **Access the Application:**
   Open `http://127.0.0.1:8000` in your web browser.

## Project Structure Overview

- `config/` - Root Django project directory containing settings and root URLs.
- `apps/` - Contains decoupled Django applications (`accounts` and `students`).
- `templates/` - Global template directory holding HTML for all apps and components.
- `static/` - Global CSS, JS, and Images.
- `media/` - Directory where user-uploaded files (like student images) are stored.

## Learning Resources
Please check `EXPLANATION.md` in the root folder for a comprehensive architectural and Django MVT workflow explanation.
