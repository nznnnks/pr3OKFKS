import os


SECRET_KEY = os.environ.get("VIOLENTDECK_SECRET", "violentdeck-secret-key")
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:admin@localhost:5432/course_skateshop",
)

EMAIL_HOST = "smtp.yandex.ru"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""

VERIFICATION_CODE_TTL_MINUTES = 10
