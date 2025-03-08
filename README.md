## Project Overview

This project is a web application built using Django. It includes a wiki module for managing content.
The CTF Book web application is a Capture The Flag (CTF) writeup management system. It allows users to create, manage, and share writeups for various CTF challenges. The application provides a structured way to document solutions and strategies used to solve CTF challenges, making it easier for users to reference and learn from past experiences.

## Deployment

To deploy this project, follow these steps:

1. Build and start the Docker containers:
    ```sh
    docker-compose up --build
    ```

2. Create and apply database migrations:
    ```sh
    docker-compose exec web python manage.py makemigrations wiki
    docker-compose exec web python manage.py migrate
    ```

3. Create a superuser to access the Django admin:
    ```sh
    docker-compose exec web python manage.py createsuperuser
    ```

4. Collect static files:
    ```sh
    docker-compose exec web python manage.py collectstatic
    ```

5. Access the application at `http://localhost:8000`.

## Database Migration

To handle database migrations, use the following commands:

- Create new migrations based on the changes detected in your models:
    ```sh
    docker-compose exec web python manage.py makemigrations
    ```

- Apply the migrations to the database:
    ```sh
    docker-compose exec web python manage.py migrate
    ```

## Additional Commands

- To run tests:
    ```sh
    docker-compose exec web python manage.py test
    ```

- To start a Django shell:
    ```sh
    docker-compose exec web python manage.py shell
    ```

- To view the logs:
    ```sh
    docker-compose logs
    ```

For more detailed information, refer to the official Django and Docker documentation.