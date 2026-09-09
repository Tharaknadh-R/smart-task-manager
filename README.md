# Smart Task Manager API

A RESTful backend API for managing users, projects, tasks, task assignments, and file attachments.

The project is built with **Python, FastAPI, PostgreSQL, SQLAlchemy, JWT authentication, and Pydantic**. It focuses on clean backend architecture, authentication, authorization, database relationships, business rules, and secure file handling.

---

## Features

- User registration and login
- JWT-based authentication
- Password hashing using Argon2
- Role-based access control
- USER and ADMIN roles
- User activation/deactivation
- Automatic task reset when a user is deactivated
- Project CRUD operations
- Task CRUD operations
- Task assignment
- Task status workflow validation
- Project ownership-based authorization
- Admin access across projects
- Project deletion safety rules
- Local file uploads
- File type validation
- File size validation
- Secure file downloads
- Attachment deletion
- PostgreSQL database
- Async SQLAlchemy database operations
- Pydantic request validation
- Swagger/OpenAPI documentation
- Environment-based configuration

---

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- asyncpg
- Pydantic
- PyJWT
- pwdlib
- Uvicorn

## Architecture
```text
Client
   |
   v
FastAPI Router
   |
   v
Pydantic Validation
   |
   v
Authentication / Authorization
   |
   v
Service Layer
   |
   v
SQLAlchemy
   |
   v
PostgreSQL
```

## Project Structure

app/
├── core/
├── database/
├── models/
├── schemas/
├── routers/
├── services/
└── main.py

uploads/


