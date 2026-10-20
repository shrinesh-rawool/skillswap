# SkillSwap 🎓

SkillSwap is a student-to-student skill exchange platform. It allows users to trade knowledge—whether it's teaching Python, tutoring calculus, or giving guitar lessons—without any money changing hands. Teach what you know, and learn what you don't.

## ✨ Features

* **User Profiles:** Custom avatars, university affiliations, and personal bios.
* **Skill Marketplace:** Post skills you want to "Teach" or "Learn".
* **Advanced Search:** Filter skills by category, level (Beginner/Intermediate/Advanced), and type.
* **Matchmaking:** Send, accept, or decline skill exchange requests.
* **Direct Messaging:** Built-in chat to coordinate sessions and share meeting links.
* **Review System:** Rate and review learning partners after a successful exchange.
* **Cloud-Ready:** Fully containerized with Docker and ready for deployment on platforms like Render, Railway, or Google Cloud Run.

## 🛠️ Tech Stack

* **Backend:** Python 3.12, Flask, Gunicorn
* **Database:** SQLite3
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, Bootstrap 5
* **Deployment:** Docker, Docker Compose

---

## 🚀 Getting Started

You can run SkillSwap locally using either standard Python or Docker.

### Option 1: Run with Docker (Recommended)

Make sure you have [Docker](https://docs.docker.com/get-docker/) and Docker Compose installed.

1. Clone the repository and navigate to the project directory:
```bash
git clone https://github.com/yourusername/skillswap.git
cd skillswap

```


2. Build and start the container:
```bash
docker compose up --build

```


3. Open your browser and navigate to `http://localhost:8080`.

*Note: The Docker setup automatically runs the database seed script on the first launch and mounts a persistent volume for your SQLite database.*

### Option 2: Run Locally (Python Virtual Environment)

Ensure you have Python 3.12+ installed.

1. Clone the repository:
```bash
git clone https://github.com/yourusername/skillswap.git
cd skillswap

```


2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate

```


3. Install dependencies:
```bash
pip install -r requirements.txt

```


4. Seed the database with demo data:
```bash
python seed.py

```


5. Run the application:
```bash
python app.py

```


6. Open your browser and navigate to `http://localhost:5050`.

---

## 🧪 Demo Accounts

If you ran `seed.py` (or started via Docker), the database is pre-populated with several demo accounts you can use to test the application.

* **Email:** `alex@demo.com`
* **Password:** `demo123`

Other demo emails include `priya@demo.com`, `jordan@demo.com`, `sam@demo.com`, and `maria@demo.com` (all using the password `demo123`).

## 📂 Project Structure

```text
skillswap/
├── app.py                # Main Flask application and routes
├── seed.py               # Database initialization and demo data
├── requirements.txt      # Python dependencies
├── Dockerfile            # Container image build instructions
├── docker-compose.yml    # Multi-container orchestration
├── .gitignore            # Git untracked files
├── .dockerignore         # Docker context exclusions
├── static/
│   ├── css/style.css     # Custom application styling
│   └── js/main.js        # Frontend interactions (alerts, char counters)
└── templates/            # Jinja2 HTML templates (auth, dashboard, messages, etc.)

```

## ☁️ Deployment

SkillSwap is configured to run behind `gunicorn` on port `$PORT` inside its Docker container, making it instantly compatible with modern PaaS providers.

To deploy to production:

1. Connect your GitHub repository to Render, Railway, or Fly.io.
2. The platform will automatically detect the `Dockerfile`.
3. Add a persistent storage volume mounted to `/app/data` to ensure your SQLite database survives redeployments.
4. Set a strong, random `SECRET_KEY` in your environment variables.

---
