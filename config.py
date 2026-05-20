import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    FIVETRAN_API_KEY    = os.getenv("FIVETRAN_API_KEY", "")
    FIVETRAN_API_SECRET = os.getenv("FIVETRAN_API_SECRET", "")
    GOOGLE_API_KEY      = os.getenv("GOOGLE_API_KEY", "")
    GCP_PROJECT_ID      = os.getenv("GCP_PROJECT_ID", "agrisync-agent")
    BIGQUERY_DATASET    = os.getenv("BIGQUERY_DATASET", "agrisync")

    @classmethod
    def validate(cls):
        missing = []
        if not cls.FIVETRAN_API_KEY:    missing.append("FIVETRAN_API_KEY")
        if not cls.FIVETRAN_API_SECRET: missing.append("FIVETRAN_API_SECRET")
        if not cls.GOOGLE_API_KEY:      missing.append("GOOGLE_API_KEY")
        if missing:
            raise ValueError(f"Missing env vars: {', '.join(missing)}")
        return True

config = Config()