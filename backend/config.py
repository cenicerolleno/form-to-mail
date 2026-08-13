import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DEBUG = True
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")
    MAIL_FROM = os.getenv("MAIL_FROM")
    MAIL_TO = os.getenv("MAIL_TO")
    ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")