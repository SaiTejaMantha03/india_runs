HONEYPOT_BUCKET_TITLES = {
    "Senior AI Engineer", "Lead AI Engineer", "Staff Machine Learning Engineer",
    "Senior Machine Learning Engineer", "Senior NLP Engineer", "Senior Applied Scientist",
    "NLP Engineer", "AI Engineer", "Search Engineer", "Applied ML Engineer",
    "Machine Learning Engineer", "Recommendation Systems Engineer", "Senior Data Scientist",
}

TITLE_PRIOR = {
    
    **{t: 0.25 for t in HONEYPOT_BUCKET_TITLES},


    "Data Scientist": 0.75,
    "ML Engineer": 0.75,
    "AI Specialist": 0.72,
    "AI Research Engineer": 0.55,        
    "Senior Software Engineer (ML)": 0.78,
    "Junior ML Engineer": 0.55,           
    "Computer Vision Engineer": 0.45,     

    "Senior Data Engineer": 0.55,
    "Data Engineer": 0.50,
    "Analytics Engineer": 0.45,
    "Backend Engineer": 0.40,


    "Software Engineer": 0.28,
    "Senior Software Engineer": 0.30,
    "Full Stack Developer": 0.22,
    "Cloud Engineer": 0.20,
    "DevOps Engineer": 0.18,
    "Java Developer": 0.15,
    ".NET Developer": 0.10,
    "Frontend Engineer": 0.08,
    "Mobile Developer": 0.08,
    "QA Engineer": 0.08,
    "Data Analyst": 0.32,


    "Business Analyst": 0.05,
    "HR Manager": 0.03,
    "Mechanical Engineer": 0.03,
    "Accountant": 0.02,
    "Project Manager": 0.08,
    "Customer Support": 0.02,
    "Operations Manager": 0.04,
    "Content Writer": 0.04,
    "Sales Executive": 0.02,
    "Civil Engineer": 0.02,
    "Graphic Designer": 0.03,
    "Marketing Manager": 0.04,
}


NON_TECHNICAL_TITLES = {
    "Business Analyst", "HR Manager", "Mechanical Engineer", "Accountant",
    "Project Manager", "Customer Support", "Operations Manager",
    "Content Writer", "Sales Executive", "Civil Engineer",
    "Graphic Designer", "Marketing Manager",
}

CV_SPEECH_ROBOTICS_TITLES = {"Computer Vision Engineer"}


def title_prior(title: str) -> float:
    """Return the relevance prior for a given current_title. Unknown titles
    default to a conservative 0.15 (neither trusted nor dismissed)."""
    return TITLE_PRIOR.get(title, 0.15)


def is_honeypot_bucket_title(title: str) -> bool:
    return title in HONEYPOT_BUCKET_TITLES
