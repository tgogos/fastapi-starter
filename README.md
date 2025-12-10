# FastAPI Starter

A production-ready FastAPI starter template with MongoDB integration, comprehensive testing, and modern development tooling.

## 🚀 Features

- **RESTful API**: Complete CRUD operations with pagination and search
  - In-memory storage (`/items`)
  - MongoDB persistent storage (`/db-items`)
- **Configuration Management**: Pydantic Settings with environment variable validation
- **Database Integration**: Async MongoDB with Motor driver
- **Testing**: Comprehensive pytest test suite with fixtures
- **Development Tools**: Docker Compose setup with hot reload
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

## 📁 Project Structure

```
fastapi-starter/
├── app/
│   ├── core/           # Configuration management (Pydantic Settings)
│   ├── models/         # Pydantic models and schemas
│   ├── routes/         # API route handlers
│   ├── utils/          # Database utilities and helpers
│   └── main.py         # FastAPI application entry point
├── tests/              # Test suite
├── docker-compose.yml      # Production Docker Compose configuration
├── docker-compose.dev.yml  # Development Docker Compose configuration
├── Dockerfile             # Container image definition
├── Makefile               # Development commands
└── requirements.txt        # Python dependencies
```

## 🛠️ Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional, for convenience commands)

### Development

```bash
# Start development environment (with hot reload)
make upd

# Access the application
# API: http://localhost:8000
# Interactive docs: http://localhost:8000/docs
# Alternative docs: http://localhost:8000/redoc
```

### Available Commands

| Command | Description |
|---------|-------------|
| `make dotenv` | Create `.env` file from template |
| `make build` | Build Docker images |
| `make up` | Start development environment (foreground) |
| `make upd` | Start development environment (detached) |
| `make down` | Stop development environment |
| `make downv` | Stop and remove volumes |
| `make test` | Run test suite |

## 🔧 Configuration

### Environment Variables

The application uses **Pydantic Settings** for configuration management, providing type validation and clear source tracking. Configuration values are loaded with the following priority:

1. **OS environment variables** (highest priority)
2. **`.env` file** (project root)
3. **Default values** (lowest priority)

#### Available Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VERSION` | `0.1.0` | Application version |
| `ENVIRONMENT` | `development` | Runtime environment |
| `DEBUG` | `false` | Enable debug mode |
| `PUBLISH_PORT` | `8000` | API server port |
| `MONGO_USER` | `root` | MongoDB username |
| `MONGO_PASS` | `pass` | MongoDB password |
| `MONGO_HOST` | `mongodb` | MongoDB hostname |
| `MONGO_PORT` | `27017` | MongoDB port |
| `MONGO_AUTH_SOURCE` | `admin` | MongoDB authentication database |
| `MONGO_DATABASE` | `fastapi_starter` | MongoDB database name |

#### Docker Compose Integration

When using Docker Compose, environment variables are automatically loaded from:
- Host environment variables
- `.env` file in the project root (via `env_file` directive)
- Default values in `docker-compose.yml`

The application prints configuration values with their sources on startup when `DEBUG=true`:

```
=== Configuration Values (with sources) ===
             VERSION: '0.1.0' [OS]
             MONGO_HOST: 'mongodb' [.env]
             MONGO_DATABASE: 'fastapi_starter' [default]
             ...
```

## 🚦 Application Bootstrap

### Startup Sequence

1. **Configuration Loading**: Pydantic Settings loads environment variables and validates types
2. **FastAPI Initialization**: Application instance is created with metadata
3. **Database Connection**: MongoDB connection is established via `startup_event` hook
4. **Route Registration**: API routes are registered with their respective prefixes
5. **Server Start**: FastAPI development server starts listening on configured port

### Startup Event

The application uses FastAPI's `@app.on_event("startup")` hook to initialize MongoDB:

```python
@app.on_event("startup")
async def startup_event():
    from app.utils.mongo import connect_to_mongo
    await connect_to_mongo()
```

This ensures the database connection is established before handling any requests. Connection failures are logged and will prevent the application from starting.

## 🧪 Testing

The project includes a comprehensive test suite covering:

- **CRUD Operations**: Create, read, update, delete workflows
- **Error Handling**: 404 errors, validation errors, invalid inputs
- **Pagination**: Page navigation, size limits, edge cases
- **Search**: Case-insensitive search with pagination
- **Data Validation**: Required fields, type validation, constraints

### Running Tests

```bash
# Run all tests
make test

# Run tests directly
docker compose -f docker-compose.dev.yml exec fastapi-starter pytest

# Run with verbose output
docker compose -f docker-compose.dev.yml exec fastapi-starter pytest -v
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures and configuration
└── test_items.py        # Comprehensive endpoint tests
```

## 📦 Dependencies

### Core

- **FastAPI** `0.122.0` - Modern web framework
- **Starlette** `0.50.0` - ASGI framework
- **Pydantic Settings** `2.5.0` - Configuration management

### Database

- **Motor** `3.3.2` - Async MongoDB driver
- **PyMongo** `4.6.0` - MongoDB Python driver

### Development

- **pytest** `7.4.4` - Testing framework
- **pytest-asyncio** `0.23.2` - Async test support
- **httpx** `0.27.0` - HTTP client for testing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
