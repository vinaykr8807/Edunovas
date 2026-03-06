import re
from collections import Counter
from datetime import datetime, timedelta
from typing import Dict, List
from urllib.parse import urlparse

from ddgs import DDGS


ROLE_SKILLS = {
    "Frontend Engineer": ["HTML", "CSS", "JavaScript", "TypeScript", "React", "Redux", "Testing"],
    "Fullstack Developer": ["React", "Node", "SQL", "API Design", "Docker", "System Design"],
    "Data Scientist": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization", "Pandas"],
    "DevOps Engineer": ["Linux", "Cloud", "Docker", "Kubernetes", "CI/CD", "Terraform"],
}

SKILL_KEYWORDS = [
    "Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue", "Node", "FastAPI",
    "Django", "Spring", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
    "AWS", "Azure", "GCP", "CI/CD", "Jenkins", "Terraform", "Linux", "Machine Learning", "Deep Learning",
    "Data Visualization", "Pandas", "NumPy", "Scikit-Learn", "Power BI", "Tableau", "System Design",
    "REST", "GraphQL", "Testing", "Git", "Microservices", "Spark", "Airflow",
]

ALLOWED_JOB_DOMAINS = [
    "linkedin.com",
    "glassdoor.co.in",
    "glassdoor.com",
    "wellfound.com",
    "naukri.com",
    "indeed.co.in",
    "foundit.in",
    "instahyre.com",
]

JOB_INTENT_KEYWORDS = [
    "job", "jobs", "hiring", "vacancy", "opening", "apply", "career",
    "developer", "engineer", "scientist", "devops", "full stack", "frontend",
]

MAX_POST_AGE_DAYS = 21


def _extract_skills_from_text(text: str) -> List[str]:
    if not text:
        return []
    corpus = f" {text.lower()} "
    found = {skill for skill in SKILL_KEYWORDS if skill.lower() in corpus}
    return sorted(found)


def _city_jobs_query(role: str, level: str, city: str) -> str:
    return f"{role} {level} jobs in {city}, India skills requirements hiring"


def _find_result_skills(text: str) -> List[str]:
    corpus = f" {text.lower()} "
    return sorted({skill for skill in SKILL_KEYWORDS if skill.lower() in corpus})


def _extract_domain(link: str) -> str:
    try:
        domain = urlparse(link).netloc.lower().replace("www.", "")
        return domain
    except Exception:
        return "unknown"


def _parse_days_ago(text: str) -> int:
    if not text:
        return -1

    content = text.lower()
    if any(k in content for k in ["today", "just posted", "few hours ago", "an hour ago"]):
        return 0
    if "yesterday" in content:
        return 1

    m_day = re.search(r"(\d+)\s+day[s]?\s+ago", content)
    if m_day:
        return int(m_day.group(1))

    m_week = re.search(r"(\d+)\s+week[s]?\s+ago", content)
    if m_week:
        return int(m_week.group(1)) * 7

    m_month = re.search(r"(\d+)\s+month[s]?\s+ago", content)
    if m_month:
        return int(m_month.group(1)) * 30

    return -1


def _parse_absolute_date_to_days_ago(date_text: str) -> int:
    if not date_text:
        return -1

    date_text = date_text.strip()
    now = datetime.utcnow()
    formats = [
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%b %d, %Y",
        "%B %d, %Y",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_text, fmt)
            return max((now - dt).days, 0)
        except Exception:
            continue
    return -1


def _is_recent_posting(title: str, snippet: str, date_text: str) -> bool:
    combined = f"{title} {snippet}"
    days_ago = _parse_days_ago(combined)
    if days_ago < 0:
        days_ago = _parse_days_ago(date_text)
    if days_ago < 0:
        days_ago = _parse_absolute_date_to_days_ago(date_text)
    if days_ago < 0:
        # Unknown posting age; ignore to keep results fresh.
        return False
    return days_ago <= MAX_POST_AGE_DAYS


def _is_allowed_job_result(title: str, snippet: str, link: str, city: str, date_text: str) -> bool:
    source = _extract_domain(link)
    if not any(source == d or source.endswith(f".{d}") for d in ALLOWED_JOB_DOMAINS):
        return False

    content = f"{title} {snippet}".lower()
    if not any(k in content for k in JOB_INTENT_KEYWORDS):
        return False

    city_l = city.lower().strip()
    if city_l and city_l not in content and "india" not in content:
        return False

    if not _is_recent_posting(title, snippet, date_text):
        return False

    return True


def _job_board_queries(role: str, level: str, city: str) -> List[str]:
    city_india = f"{city}, India"
    return [
        f"site:linkedin.com/jobs {role} {level} {city_india} skills requirements",
        f"site:glassdoor.co.in {role} {level} {city_india} job description skills",
        f"site:wellfound.com/jobs {role} {level} {city_india}",
        f"site:naukri.com {role} {level} {city_india} skills required",
        f"site:indeed.co.in {role} {level} {city_india} hiring",
        _city_jobs_query(role, level, city),
    ]


def _search_jobs(role: str, level: str, city: str, max_results: int = 8) -> List[Dict]:
    items: List[Dict] = []
    seen_links = set()
    queries = _job_board_queries(role, level, city)

    try:
        with DDGS() as ddgs:
            for query in queries:
                for r in ddgs.text(query, region="in-en", safesearch="moderate", timelimit="y"):
                    title = r.get("title", "").strip()
                    snippet = r.get("body", "").strip()
                    link = r.get("href", "").strip()
                    date_text = str(r.get("date", "")).strip()
                    if not link or link in seen_links:
                        continue
                    if not _is_allowed_job_result(title, snippet, link, city, date_text):
                        continue

                    source = _extract_domain(link)
                    skills = _find_result_skills(f"{title} {snippet}")
                    items.append(
                        {
                            "title": title or "Job listing",
                            "source": source,
                            "link": link,
                            "date": date_text,
                            "snippet": snippet or "No description snippet available.",
                            "skills": skills,
                        }
                    )
                    seen_links.add(link)
                    if len(items) >= max_results:
                        break
                if len(items) >= max_results:
                    break
    except Exception as e:
        print(f"Career search error: {e}")

    return items


def _market_required_skills(role: str, job_market: List[Dict]) -> List[str]:
    counter: Counter = Counter()
    for item in job_market:
        counter.update(item.get("skills", []))

    ranked = [skill for skill, _ in counter.most_common(10)]
    if ranked:
        return ranked
    return ROLE_SKILLS.get(role, [])


def _build_proceed_guide(role: str, city: str, missing_skills: List[str], matched_skills: List[str]) -> Dict[str, List[str]]:
    immediate = [
        f"Lock target role as {role} in {city} and shortlist 20 active openings.",
        "Update resume headline and summary to match top 5 recurring skills in job posts.",
        "Set up a weekly tracker: applications, interview rounds, and rejected-skill reasons.",
    ]
    short_term = [
        f"Close top gaps first: {', '.join([s for i, s in enumerate(missing_skills) if i < 3])}" if missing_skills else "Strengthen one depth area and one breadth area each week.",
        "Build one portfolio artifact tied to real job requirements.",
        "Practice role-specific interview questions for 30-45 minutes daily.",
    ]
    mid_term = [
        "Apply to 8-12 well-matched jobs per week with tailored resumes.",
        "Refactor projects to include measurable outcomes and production-like practices.",
        "Run two mock interviews weekly and log weak areas.",
    ]
    long_term = [
        "Convert portfolio into case-study style stories with impact metrics.",
        "Add one advanced specialization to stand out in shortlisted roles.",
        f"Review matched strengths monthly and deepen: {', '.join([s for i, s in enumerate(matched_skills) if i < 4])}" if matched_skills else "Review progress monthly and recalibrate role fit.",
    ]

    return {
        "immediate": immediate,
        "short_term": short_term,
        "mid_term": mid_term,
        "long_term": long_term,
    }


def _build_roadmap(role: str, missing_skills: List[str], market_skills: List[str]) -> Dict[str, List[str]]:
    foundational_focus = list(missing_skills)[:4] or list(market_skills)[:4] or ROLE_SKILLS.get(role, [])
    job_readiness_focus = list(market_skills)[:5] or ROLE_SKILLS.get(role, [])

    foundation = [f"Master {skill} with focused practice and mini-deliverables." for skill in list(foundational_focus)[:4]]
    job_readiness = [f"Demonstrate {skill} in at least one resume-listed project bullet." for skill in list(job_readiness_focus)[:5]]
    interview_prep = [
        "Prepare role-specific fundamentals with concise explanations.",
        "Build a bank of 30 likely interview questions and answers.",
        "Practice timed mock interviews and improve weak responses weekly.",
    ]
    projects = [
        f"{role} Capstone: design, build, test, and deploy an end-to-end project.",
        "Production Readiness Project: observability, error handling, and documentation.",
        "Case Study Project: business problem, technical solution, measurable impact.",
    ]

    return {
        "foundation": foundation,
        "job_readiness": job_readiness,
        "interview_prep": interview_prep,
        "projects": projects,
    }


def generate_career_report(resume_text: str, role: str, level: str, city: str) -> Dict:
    normalized_role = role if role in ROLE_SKILLS else "Fullstack Developer"
    resume_skills = _extract_skills_from_text(resume_text)
    job_market = _search_jobs(normalized_role, level, city)
    market_required_skills = _market_required_skills(normalized_role, job_market)

    resume_upper = {s.upper() for s in resume_skills}
    missing_skills = [s for s in market_required_skills if s.upper() not in resume_upper]
    matched_skills = [s for s in market_required_skills if s.upper() in resume_upper]

    baseline = market_required_skills if market_required_skills else ROLE_SKILLS.get(normalized_role, [])
    readiness_score = int((len(matched_skills) / max(len(baseline), 1)) * 100)

    return {
        "role": normalized_role,
        "level": level,
        "city": city,
        "readiness_score": readiness_score,
        "resume_skills": resume_skills,
        "market_required_skills": market_required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "job_market": job_market,
        "proceed_guide": _build_proceed_guide(normalized_role, city, missing_skills, matched_skills),
        "roadmap": _build_roadmap(normalized_role, missing_skills, market_required_skills),
    }
