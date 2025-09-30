# Microblog Backend

![Demo Screenshot](image.png)

Backend for a corporate microblogging service, similar to Twitter.  
Built with FastAPI, PostgreSQL + SQLAlchemy, and Docker — ready for production.

- 🔥 **Live Demo**: [http://31.57.27.122:8080](http://31.57.27.122:8080)
- 📚 **Swagger Docs**: [http://31.57.27.122:8000/docs](http://31.57.27.122:8000/docs)

---

## ✨ Features

- ✍️ Create/delete tweets
- ❤️ Like/unlike tweets
- 👥 Follow/unfollow users
- 🖼️ Upload files (JPG, PNG, GIF, WebP, MP4, MOV, BIN)
- 📰 Feed sorted by popularity (likes)
- 🔐 Authentication via `api-key` header
- 🐳 One-command deploy with Docker Compose
- 🧪 90%+ test coverage
- 📄 Full Swagger documentation

---

## 🛠 Tech Stack

| Layer | Technology |
|------|------------|
| **Backend** | FastAPI (Python 3.13) |
| **Database** | PostgreSQL 16 |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Containerization** | Docker & Docker Compose |
| **CI/CD** | GitHub Actions |
| **Frontend** | Vanilla JS + Nginx |

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/lonely-crab/microblog-backend-fastapi.git
cd microblog-backend-fastapi
```

### 2. Create .env file:
```bash
echo "POSTGRES_DB=microblog" > .env
echo "POSTGRES_USER=user" >> .env
echo "POSTGRES_PASSWORD=password" >> .env
echo "DATABASE_URL=postgresql+asyncpg://user:password@db:5432/microblog" >> .env
```

### 3. Run with Docker

```bash
docker-compose up -d --build
```


### 4. Open in browser

Frontend: http://localhost:8080

Swagger: http://localhost:8000/docs

✅ That's it! The app is running.

#### 4.1. To test it properly - you need to create test users
- Log in your DB docker-container:
    ```bash
    docker exec -it microblog-backend-fastapi-db-1 bash
    ````
- Connect to your DB:
    ```bash
    psql -U user -d microblog
    ```
- Create users:
    ```sql
    INSERT INTO users (name, api_key) VALUES ('user1', 'key1') ('user2', 'key2');
    ```
#### 4.2. All ready!
✅ Now everything is ready. Go test those buttons on the website!


---




## 🔄 CI/CD Pipeline

Automatically runs on every push to dev/master/hotfix or release:

1. Linting (black, flake8, mypy)
2. Unit & integration tests
3. Build Docker image
4. Deploy to server via SSH

## 📂 Project Structure

microblog-backend/
├── app/                      # Core application
│   ├── api/v1/               # API routes
│   ├── services/             # Business logic
│   ├── schemas/              # Pydantic models
│   ├── db/                   # Database models & setup
│   └── main.py               # FastAPI entry point
│
├── tests/                    # Test suite
│   ├── unit/                 # Unit tests
│   └── integration/          # Integration tests
│
├── frontend/                 # Static frontend files
│   ├── index.html            # Built HTML + JS 
│   └── nginx.conf            # Reverse proxy config
│
├── alembic/                  # Database migrations
│   └── versions/             # Generated migration scripts
│
├── .github/workflows/        # CI/CD pipelines
│
├── docker-compose.yml        # Container orchestration
├── Dockerfile                # Backend image build
└── README.md                 # This file


## 🗃 Database Schema

Tables:

- users: id, name, api_key
- tweets: id, content, author_id
- media: id, file_path, tweet_id
- likes: user_id, tweet_id (composite PK)
- followers: follower_id, following_id (composite PK)

Migrations managed by **Alembic**.

## 📋 Notes

- Authentication: Uses api-key header. No registration.
- Data Persistence: All data saved via Docker volumes.
- CORS: Disabled (nginx reverse proxy handles same-origin).
- Logging: Structured logs in stdout (for Docker).
- Error Handling: All exceptions return {result: false, ...}.

## 🏁 Credits

 - Backend: **Ivan Bolshakov** ([lonely-crab](https://github.com/lonely-crab))
- Frontend: AI-generated
- Design: AI-generated

 Built for Python Advanced Diploma SkillBox.

## 📬 Feedback

Found a bug? Want a feature?
Open an issue or contact me:

📧 is.bolshakov@mail.ru