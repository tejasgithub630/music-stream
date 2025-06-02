# Global Music Streaming Web Application

A full-stack music streaming platform built with Django and modern web technologies.

## Features

- User authentication and authorization
- Music streaming and playback
- Playlist creation and management
- Search functionality across artists and genres
- Admin panel for content management
- Responsive design for all devices

## Tech Stack

- Backend: Django (Python)
- Frontend: HTML, CSS, JavaScript
- Database: MySQL
- Additional: Django REST Framework, CORS Headers

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up MySQL database and update settings.py with your database credentials
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
music_streaming/
├── backend/           # Django backend
│   ├── apps/         # Django applications
│   ├── static/       # Static files
│   └── templates/    # HTML templates
├── frontend/         # Frontend assets
│   ├── css/         # Stylesheets
│   ├── js/          # JavaScript files
│   └── images/      # Image assets
└── media/           # User-uploaded content
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License. 