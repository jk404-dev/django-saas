from pathlib import Path

from django.conf import settings
from helpers import download_to_local
from typing import Any
from django.conf import settings
from django.core.management.base import BaseCommand

STATICFILES_VENDOR_DIR = getattr(settings, "STATICFILES_VENDOR_DIR")

VENDOR_STATICFILES =  {
    "flowbite.min.css": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.css",
    "flowbite.min.js": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js",
    "flowbite.min.js.map": "https://cdn.jsdelivr.net/npm/flowbite@3.1.2/dist/flowbite.min.js.map",
}


class Command(BaseCommand):
    
    def handle(self, *args: Any, **options: Any) -> str | None:
        self.stdout.write("Pulling vendor files...")
        completed_urls = []
        
        for name, url in VENDOR_STATICFILES.items():
            out_path = STATICFILES_VENDOR_DIR / name
            dl_success = download_to_local(url, out_path)
            self.stdout.write(f"Downloading {url} to {out_path}")
            if dl_success:
                completed_urls.append(url)
            else:
                self.stderr.write(self.style.ERROR(f"Failed to download {url}"))

        if set(completed_urls) == set(VENDOR_STATICFILES.values()):
            self.stdout.write(self.style.SUCCESS("Vendor files pulled successfully."))
        else:
            self.stderr.write(self.style.ERROR("Failed to pull all vendor files."))
