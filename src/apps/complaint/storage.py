from pathlib import Path
from django.conf import settings
from django.core.files.storage import FileSystemStorage

temp_storage = FileSystemStorage(
    location=Path(settings.BASE_DIR) / "temp_uploads"
)