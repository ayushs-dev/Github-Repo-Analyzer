# GitHub Repo Analyzer

Ever wondered what's really going on inside a GitHub repository? How many people 
actually contribute? What languages is it built with? How fast is it growing?

This app answers all of that. Type in any GitHub repository and get a clean 
breakdown of its stats in seconds.

![GitHub Repo Analyzer](https://img.shields.io/badge/built_with-FastAPI_+_React_+_PostgreSQL-blue)

## What it does

- Search any public GitHub repository by typing `owner/repo`
- See stars, forks, open issues, and watchers at a glance
- Visual language breakdown showing what the codebase is built with
- Top contributors with their avatars and commit counts
- Results are cached — so repeat searches are instant

## How it's built

This is a full stack project built with four technologies that are used 
heavily in real production systems:

**Backend — FastAPI (Python)**  
Handles all the API requests, talks to GitHub, and manages the database. 
FastAPI was chosen because it's fast, modern, and generates API documentation 
automatically.

**Database — PostgreSQL**  
Stores analyzed repo data so we don't hammer the GitHub API on every request. 
Results are cached for 1 hour. After that, fresh data is fetched automatically.

**Frontend — React + Vite + Tailwind CSS**  
The UI you interact with. Built as reusable components — search bar, stats card, 
language bar, contributor list. Vite makes development fast with instant hot reload.

**Infrastructure — Docker Compose**  
All three services (frontend, backend, database) run in containers. One command 
starts the entire stack. No "it works on my machine" problems.

## Running it locally

You'll need two things installed:
- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- A GitHub Personal Access Token

### Getting a GitHub token

1. Go to GitHub → Settings → Developer Settings
2. Personal access tokens → Tokens (classic)
3. Generate new token → check `read:public_repo` → copy it

### Setup

Clone the repo:
```bash
git clone https://github.com/ayushs-dev/Github-Repo-Analyzer.git
cd Github-Repo-Analyzer
```

Create the backend environment file:
```bash
touch backend/.env
```

Open `backend/.env` and add these three lines:
```
GITHUB_TOKEN=your_token_here
GITHUB_API_BASE=https://api.github.com
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/repoanalyzer
```

Start everything:
```bash
docker compose up --build
```

Open your browser and go to:
```
http://localhost:5173
```

Type any repo in `owner/repo` format — like `facebook/react` or `torvalds/linux` 
— and hit Analyze.

## Project structure
```
github-repo-analyzer/
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── main.py          # App entry point
│   │   ├── database.py      # Database connection
│   │   ├── models/          # Database table definitions
│   │   ├── schemas/         # API request/response shapes
│   │   ├── routers/         # API endpoints
│   │   └── services/        # GitHub API client + config
│   ├── alembic/             # Database migrations
│   └── requirements.txt
├── frontend/                # React application
│   └── src/
│       ├── App.jsx          # Root component
│       └── components/      # SearchBar, RepoCard, etc.
├── docker-compose.yml       # Runs everything together
└── README.md
```

## Things I learned building this

- How to build an async REST API with FastAPI
- How database caching works and why it matters
- How React components talk to a backend
- How Docker Compose connects multiple services together
- How to debug real errors in a real stack (there were many)

## What's next

- Add a history page showing all previously analyzed repos
- Add charts showing star growth over time
- Deploy it to a real server
