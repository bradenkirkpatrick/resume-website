# Resume Website

A full-stack resume website with a **Python (FastAPI) backend** and **React frontend**, managed by Node.js scripts, with CI/CD, automated testing, and AWS EC2 deployment support.

## Features

- 📄 Display and download your resume
- 🔄 Auto-populate from Google Docs (optional)
- 🐍 Python FastAPI backend with RESTful API
- ⚛️ React frontend with modern UI
- 🧪 90%+ test coverage (backend & frontend)
- 🔧 Makefile automation for testing, linting, and dev commands
- 🚀 CI/CD pipeline with GitHub Actions
- ☁️ AWS EC2 deployment ready

## Quick Start

```bash
# Install dependencies
make install

# Start local development (with restart prompt if running)
make start-local

# Force restart
make start-local ARGS="-f"

# Stop servers
make stop-local

# Run tests (requires 90% coverage)
make test

# Lint code
make lint
```

## Google Docs Integration

Your resume can be auto-populated from a Google Doc:
[Resume Google Doc](https://docs.google.com/document/d/1IvKov91tVgnB4mHLVjz1s18q9OJnNeWyh3mNsmG3n84/edit?usp=sharing)

To set up the integration, configure `GOOGLE_DOCS_ID` and `GOOGLE_APPLICATION_CREDENTIALS` in `.env`. See `deploy-ec2.md` for detailed instructions.

## Project Structure

```
resumewebsite/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # FastAPI application setup
│   │   ├── models.py          # Pydantic data models
│   │   ├── routes/resume.py   # Resume API endpoints
│   │   └── services/          # Google Docs integration
│   ├── tests/                 # Backend test suite (52 tests)
│   ├── requirements.txt
│   └── pyproject.toml
├── frontend/                  # React + Vite frontend
│   ├── src/
│   │   ├── App.jsx            # Main application
│   │   ├── components/        # Resume display components
│   │   └── services/api.js    # API client
│   ├── tests/                 # Frontend test suite (24 tests)
│   └── package.json
├── scripts/                   # Start/stop scripts
│   ├── start-local.sh         # Local dev server startup
│   ├── stop-local.sh          # Local dev server shutdown
│   ├── start-prod.sh          # Production server startup
│   └── stop-prod.sh           # Production server shutdown
├── .github/workflows/         # CI/CD pipeline
├── deploy-ec2.md              # EC2 deployment guide
├── Makefile                   # Automation
└── .env.example               # Environment template
```

## Available Commands

| Command | Description |
|---------|-------------|
| `make install` | Install all dependencies |
| `make test` | Run all tests (backend + frontend) |
| `make test-backend` | Run backend tests with coverage |
| `make test-frontend` | Run frontend tests with coverage |
| `make lint` | Lint all code |
| `make lint-fix` | Auto-fix lint issues |
| `make start-local` | Start local dev servers |
| `make stop-local` | Stop local dev servers |
| `make start-prod` | Start production servers |
| `make stop-prod` | Stop production servers |
| `make clean` | Remove build artifacts |
| `make setup` | Full clean install |

## Scripts Behavior

All start scripts (`start-local.sh`, `start-prod.sh`) check if servers are already running:
- **Default**: Prompts "Do you want to restart the servers?" (y/N)
- **With `-f` flag**: Automatically restarts without prompting

## Deployment

See [deploy-ec2.md](./deploy-ec2.md) for the complete AWS EC2 deployment guide, including:
- EC2 instance setup
- Nginx reverse proxy configuration
- SSL with Let's Encrypt
- PM2 process management
- One-line deploy command

## CI/CD

The project includes a GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) that:
1. **Lints** both backend and frontend code
2. **Runs tests** with 90% coverage threshold
3. **Builds** the frontend
4. **Deploys** to EC2 automatically on main branch pushes
