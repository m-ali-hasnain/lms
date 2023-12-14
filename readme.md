# University Management System

## Description
This project is a University Management System that includes user registration, authentication, course management, and scheduling functionality. The backend is built with Django, Django REST Framework, and PostgreSQL, while the frontend uses Next.js with Bootstrap for styling.

## Features
- User registration and authentication with email and password.
- Admin and Student roles with different permissions.
- Course management (add, update, delete).
- Schedule management for students.
- Token-based authentication using JWT.

## Technologies Used
- **Backend:**
  - Django
  - Django REST Framework
  - PostgreSQL

- **Frontend:**
  - Next.js
  - Bootstrap

## Setup Instructions
1. Clone the repository:
   ```bash
        git clone <repository-url>
        cd lms
        # Set up a virtual environment (recommended)
        python -m venv venv
        source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
        pip install -r requirements.txt
        python manage.py migrate
        python manage.py runserver
   ```

## API ENDPOINTS
1. /auth/users/register # For registering User(default as Student)
2. /auth/users/login # For login 
3. /auth/token/obtain # For obtaining token
4. /auth/token/refresh # For refreshing jwt token