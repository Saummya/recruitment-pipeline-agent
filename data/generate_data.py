"""Generate a synthetic recruitment database and fake resumes."""
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

from faker import Faker

fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

BASE = Path(__file__).parent
DB_PATH = BASE / "recruitment.db"
RESUME_DIR = BASE / "resumes"

SKILLS = {
    "backend": ["Python", "Django", "FastAPI", "Java", "Spring Boot", "Node.js", "PostgreSQL", "Kafka", "Redis"],
    "frontend": ["JavaScript", "React", "TypeScript", "CSS", "Next.js", "Vue"],
    "data": ["Python", "SQL", "Pandas", "Spark", "Airflow", "PyTorch", "scikit-learn"],
    "devops": ["Docker", "Kubernetes", "AWS", "Terraform", "CI/CD", "Linux"],
}
COMPANIES = ["Infosys", "TCS", "Flipkart", "Zomato", "Razorpay", "Swiggy", "Freshworks", "Zoho", "Paytm", "Wipro"]
STATUSES = ["new", "screening", "interview", "offer", "rejected"]

SCHEMA = """
DROP TABLE IF EXISTS interviews;
DROP TABLE IF EXISTS applications;
DROP TABLE IF EXISTS skills;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS candidates;

CREATE TABLE candidates (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    domain TEXT NOT NULL,
    current_role TEXT NOT NULL,
    years_experience INTEGER NOT NULL,
    status TEXT NOT NULL,
    contacted_at TEXT,
    resume_path TEXT
);
CREATE TABLE skills (
    candidate_id INTEGER REFERENCES candidates(id),
    skill TEXT NOT NULL
);
CREATE TABLE jobs (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    domain TEXT NOT NULL,
    description TEXT NOT NULL,
    min_experience INTEGER NOT NULL
);
CREATE TABLE applications (
    candidate_id INTEGER REFERENCES candidates(id),
    job_id INTEGER REFERENCES jobs(id),
    match_score REAL,
    stage TEXT NOT NULL
);
CREATE TABLE interviews (
    id INTEGER PRIMARY KEY,
    candidate_id INTEGER REFERENCES candidates(id),
    interviewer TEXT NOT NULL,
    scheduled_at TEXT NOT NULL,
    feedback_summary TEXT
);
"""

JOBS = [
    ("Backend Engineer", "backend", "Build and scale APIs using Python or Java, PostgreSQL, Kafka.", 3),
    ("Senior Backend Engineer", "backend", "Lead design of distributed services; mentor engineers.", 6),
    ("Frontend Engineer", "frontend", "Build responsive UIs with React and TypeScript.", 2),
    ("Data Scientist", "data", "Build ML models and data pipelines with Python and SQL.", 3),
    ("DevOps Engineer", "devops", "Run CI/CD, Kubernetes and AWS infrastructure.", 3),
]


def make_resume(name, domain, role, years, skills, companies):
    return f"""{name}
{role} | {years} years of experience

SUMMARY
{domain.title()} professional with {years} years of experience building production systems.

SKILLS
{", ".join(skills)}

EXPERIENCE
{companies[0]} - {role} ({max(1, years - 2)}+ years)
- Designed and shipped features used by thousands of users.
- Worked with {", ".join(skills[:3])} in a team of {random.randint(4, 12)} engineers.

{companies[1]} - Software Engineer
- Improved performance and reliability of core services.

EDUCATION
B.Tech in Computer Science, {fake.city()}
"""


def main():
    RESUME_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    conn.executemany(
        "INSERT INTO jobs (title, domain, description, min_experience) VALUES (?,?,?,?)", JOBS
    )

    for cid in range(1, 61):
        domain = random.choice(list(SKILLS))
        years = random.randint(0, 10)
        role = f"{'Senior ' if years >= 5 else ''}{domain.title()} Engineer"
        name = fake.name()
        skills = random.sample(SKILLS[domain], k=random.randint(3, 5))
        status = random.choices(STATUSES, weights=[40, 25, 15, 5, 15])[0]
        contacted = None
        if status != "new":
            contacted = (datetime(2026, 10, 1) + timedelta(days=random.randint(0, 20))).date().isoformat()
        resume_path = f"resumes/candidate_{cid:03d}.txt"
        email = f"{name.lower().replace(' ', '.')}@example.com"

        conn.execute(
            "INSERT INTO candidates VALUES (?,?,?,?,?,?,?,?,?)",
            (cid, name, email, domain, role, years, status, contacted, resume_path),
        )
        conn.executemany("INSERT INTO skills VALUES (?,?)", [(cid, s) for s in skills])

        (BASE / resume_path).write_text(
            make_resume(name, domain, role, years, skills, random.sample(COMPANIES, 2))
        )

        # apply to 1-2 jobs in the same domain
        job_ids = [i + 1 for i, j in enumerate(JOBS) if j[1] == domain]
        for job_id in random.sample(job_ids, k=min(len(job_ids), random.randint(1, 2))):
            conn.execute(
                "INSERT INTO applications VALUES (?,?,?,?)", (cid, job_id, None, status)
            )

        if status in ("interview", "offer"):
            when = (datetime(2026, 10, 25) + timedelta(days=random.randint(0, 10))).isoformat(timespec="minutes")
            conn.execute(
                "INSERT INTO interviews (candidate_id, interviewer, scheduled_at, feedback_summary) VALUES (?,?,?,?)",
                (cid, fake.name(), when, None),
            )

    conn.commit()
    conn.close()
    print(f"Created {DB_PATH} and 60 resumes in {RESUME_DIR}")


if __name__ == "__main__":
    main()