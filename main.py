from services.db import init_db
from workflows.pipeline import run_pipeline

if __name__ == "__main__":
    init_db()
    run_pipeline()