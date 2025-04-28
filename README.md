# Moon Calendar

A Django-based web application for tracking and managing calendar events with lunar phase information.

## Prerequisites

- Python 3.x
- pip (Python package manager)
- PostgreSQL 17+ or Docker
- Git

## Setting Up the Development Environment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/tajahreynolds/moon-cal
   cd moon-cal
   ```

2. **Environment Configuration**
   - Copy the `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Update the following variables in `.env`:
     - `PG_USERNAME`: PostgreSQL username
     - `PG_PASSWORD`: PostgreSQL password
     - `PG_DATABASE`: Database name

3. **Database Setup**
   
   Choose one of the following options:

   **Option A: Using Docker**
   - Ensure Docker and Docker Compose are installed
   - Run the database container:
     ```bash
     docker compose up -d
     ```

   **Option B: Local PostgreSQL**
   - Install PostgreSQL 17 or higher
   - Create a database and user with appropriate permissions
   - Update the `.env` file with your database credentials

4. **Database Migration**
   ```bash
   python manage.py migrate
   ```

5. **Python Environment Setup**
   ```bash
   python -m pip install -r requirements.txt
   ```
6. **Start the Development Server**
   ```bash
   python manage.py runserver
   ```
   The application will be available at `http://127.0.0.1:8000/mooncal/`

## Development

- To create a superuser account:
  ```bash
  python manage.py createsuperuser
  ```
- Access the admin interface at `http://127.0.0.1:8000/admin/`

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

