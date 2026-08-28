import os

UI_BASE_URL = os.getenv(
    "UI_BASE_URL",
    "https://svcdemoaz.puremonitor.supercom.com/AQApplication/Noam",
)

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://svcdemoaz.puremonitor.supercom.com/AQApplication/Noam/api",
)
