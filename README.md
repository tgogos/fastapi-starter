# FastAPI Starter

A minimal FastAPI "starter" template for new projects...

## 🚀 Features

- **Example endpoints**: Complete CRUD functionality for
  - `items` (stored in-memory) and
  - `db-items` (stored in a Mongo database)
- **Pagination & Search**: Built-in pagination and simple search functionality
- **Environment Configuration**: Flexible environment variable management with a `.env` and `docker compose`
- **Makefile**: Convenient commands for various tasks
- **MongoDB Integration**: Persistent data storage with Motor async driver

## 📁 Project Structure

```
fastapi-starter/
├── app/
│   ├── core/           # Configuration & core utilities
│   ├── models/         # Data models & schemas
│   ├── routes/         # API route handlers
│   ├── utils/          # Utility functions
│   └── main.py         # FastAPI application entry point
├── docker-compose.yml      # "Production" setup
├── docker-compose.dev.yml  # "Development" setup
├── Dockerfile              # Container configuration
└── requirements.txt        # Python dependencies
```

## 🛠️ Quick Start

### Prerequisites

- Docker and Docker Compose
- Make (optional, for using Makefile commands)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd fastapi-starter
   ```

2. **Set up environment variables**
   ```bash
   make dotenv  # Creates .env file from .env.example
   ```

3. **Start the development environment**
   ```bash
   make up  # Starts with hot reload
   # or
   make upd  # Starts in detached mode
   ```

4. **Access the application**
   - API: http://localhost:8000
   - Interactive API docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### Available Make Commands

- `make dotenv` - Create .env file from template
- `make build` - Build Docker images
- `make up` - Start development environment
- `make upd` - Start development environment (detached)
- `make down` - Stop development environment
- `make downv` - Stop and remove volumes



## 🔧 Configuration

Key environment variables (set in `.env` file):

```env
# Application
APP_NAME=fastapi-starter
PUBLISH_PORT=8000

# Docker
DOCKER_REG=
DOCKER_REPO=
DOCKER_TAG=latest

# MongoDB
MONGO_USER=root
MONGO_PASS=pass
```

## 📦 Dependencies

- **FastAPI**: Modern web framework for APIs
- **Motor**: Async MongoDB driver
- **PyMongo**: MongoDB Python driver
- **Python 3.12**: Latest Python version

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test your changes
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
