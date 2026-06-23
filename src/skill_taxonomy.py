CORE_SKILLS = {
    "Python": 1.0,
    "PyTorch": 1.0,
    "TensorFlow": 0.9,
    "NLP": 1.0,
    "Machine Learning": 0.85,
    "Deep Learning": 0.85,
    "BM25": 1.0,
    "Learning to Rank": 1.0,
    "Qdrant": 0.95,
    "Weaviate": 0.95,
    "Milvus": 0.95,
    "pgvector": 0.9,
    "scikit-learn": 0.75,
    "Elasticsearch": 0.95,
    "OpenSearch": 0.95,
    "Haystack": 0.85,
    "LlamaIndex": 0.8,
    "QLoRA": 0.8,
    "PEFT": 0.8,
    "LoRA": 0.8,
}


BUZZWORD_SKILLS = {
    "Hugging Face Transformers": 0.55,
    "LangChain": 0.35,          
    "Information Retrieval": 0.7,
    "LLMs": 0.4,
    "Recommendation Systems": 0.6,
    "Semantic Search": 0.6,
    "Sentence Transformers": 0.6,
    "Embeddings": 0.6,
    "Vector Search": 0.65,
    "Prompt Engineering": 0.3,
    "Pinecone": 0.5,
    "FAISS": 0.65,
    "RAG": 0.4,
    "Fine-tuning LLMs": 0.55,
    "Feature Engineering": 0.45,
    "MLOps": 0.45,
    "BentoML": 0.4,
    "Data Science": 0.4,
    "MLflow": 0.45,
    "Statistical Modeling": 0.35,
    "Reinforcement Learning": 0.3,
}


ADJACENT_ML_SKILLS = {
    "YOLO": 0.1,
    "GANs": 0.1,
    "OpenCV": 0.1,
    "ASR": 0.15,
    "Image Classification": 0.1,
    "Computer Vision": 0.15,
    "Speech Recognition": 0.15,
    "CNN": 0.15,
    "Object Detection": 0.1,
    "Diffusion Models": 0.1,
    "Time Series": 0.2,
    "Forecasting": 0.15,
    "TTS": 0.1,
    "Kubeflow": 0.25,
    "Weights & Biases": 0.25,
}


DATA_INFRA_SKILLS = {
    "Spark": 0.3,
    "Kafka": 0.25,
    "Airflow": 0.25,
    "dbt": 0.2,
    "Snowflake": 0.15,
    "BigQuery": 0.15,
    "Databricks": 0.25,
    "Hadoop": 0.2,
    "ETL": 0.2,
    "Data Pipelines": 0.25,
    "Redis": 0.1,
    "Kubernetes": 0.15,
    "Docker": 0.15,
    "Microservices": 0.15,
    "gRPC": 0.1,
    "REST APIs": 0.05,
    "PostgreSQL": 0.1,
    "MongoDB": 0.1,
    "SQL": 0.15,
    "CI/CD": 0.1,
    "Go": 0.1,
    "Rust": 0.1,
    "Java": 0.05,
}


HONEYPOT_BAIT_SKILLS = {
    "Information Retrieval Systems", "Search Backend", "Text Encoders",
    "Vector Representations", "Content Matching", "Model Adaptation",
    "Ranking Systems", "Search & Discovery", "Workflow Orchestration",
    "Search Infrastructure", "Indexing Algorithms",
    "Open-source ML libraries", "Natural Language Processing",
    "Document Processing",
}


NOISE_SKILLS_WEIGHT = 0.0

SKILL_WEIGHTS = {}
SKILL_WEIGHTS.update(CORE_SKILLS)
SKILL_WEIGHTS.update(BUZZWORD_SKILLS)
SKILL_WEIGHTS.update(ADJACENT_ML_SKILLS)
SKILL_WEIGHTS.update(DATA_INFRA_SKILLS)


PROFICIENCY_MULTIPLIER = {
    "beginner": 0.4,
    "intermediate": 0.7,
    "advanced": 1.0,
    "expert": 1.0,  
}


def skill_weight(name: str) -> float:
    return SKILL_WEIGHTS.get(name, 0.0)


def is_honeypot_bait_skill(name: str) -> bool:
    return name in HONEYPOT_BAIT_SKILLS
