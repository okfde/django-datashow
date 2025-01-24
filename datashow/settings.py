from django.conf import settings

DATASHOW_DB_CACHE_PATH = getattr(settings, "DATASHOW_DATABASE_LOCATION", None)
DATASHOW_STORAGE_BACKEND = getattr(settings, "DATASHOW_STORAGE_BACKEND", "default")
