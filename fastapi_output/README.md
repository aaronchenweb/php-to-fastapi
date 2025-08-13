# FastAPI Application

This FastAPI application was automatically converted from a PHP web API project.

## Features

- **FastAPI Framework**: Modern, fast, and intuitive API framework
- **Automatic API Documentation**: Interactive docs at `/docs` and `/redoc`
- **Authentication**: JWT-based authentication system
- **Database Integration**: SQLAlchemy ORM with Alembic migrations
- **Docker Support**: Container-ready with Docker and Docker Compose
- **Environment Configuration**: Flexible configuration with environment variables

## Quick Start

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Installation

1. **Clone the repository** (if applicable):
   ```bash
   git clone <repository-url>
   cd fastapi-application
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations** (if using a database):
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**:
   ```bash
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`

## API Documentation

- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and run the application
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Using Docker directly

```bash
# Build the image
docker build -t fastapi-application .

# Run the container
docker run -p 8000:8000 --env-file .env fastapi-application
```

## Configuration

The application uses environment variables for configuration. See `.env.example` for all available options.

### Required Environment Variables

- `SECRET_KEY`: Secret key for security (minimum 32 characters)
- `DATABASE_URL`: Database connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens (if using authentication)

### Optional Environment Variables

- `DEBUG`: Enable debug mode (default: false)
- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `LOG_LEVEL`: Logging level (default: INFO)

## Database

This application uses SQLAlchemy for database operations and Alembic for migrations.

### Running Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migrations
alembic downgrade -1
```

## Development

### Code Style

This project follows Python best practices:

- **Code formatting**: Use `black` for code formatting
- **Linting**: Use `flake8` for linting
- **Type checking**: Use `mypy` for type checking

```bash
# Install development dependencies
pip install black flake8 mypy pytest

# Format code
black .

# Lint code
flake8 .

# Type check
mypy .
```

### Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run tests with coverage
pytest --cov=app
```

## Project Structure

```
fastapi-application/
├── app/
│   ├── core/           # Core configuration and security
│   ├── models/         # Database models
│   ├── routers/        # API route handlers
│   ├── schemas/        # Pydantic schemas
│   └── __init__.py
├── alembic/            # Database migrations
├── uploads/            # File uploads (created at runtime)
├── .env.example        # Environment variables template
├── .gitignore         # Git ignore rules
├── docker-compose.yml # Docker Compose configuration
├── Dockerfile         # Docker configuration
├── main.py            # Application entry point
├── requirements.txt   # Python dependencies
└── README.md          # This file
```

## Migration from PHP

This FastAPI application was converted from a PHP web API. Key changes include:

- **Language**: PHP → Python
- **Framework**: Custom PHP → FastAPI
- **Database**: Direct SQL → SQLAlchemy ORM
- **Authentication**: PHP sessions → JWT tokens
- **Documentation**: Manual → Automatic OpenAPI/Swagger

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions and support, please open an issue in the project repository.