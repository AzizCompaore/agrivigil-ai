import os
import sys
import django
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from core.ai_diagnosis import diagnose_crop_image

suivi_dir = settings.MEDIA_ROOT / "scans" / "test suivi"
files = sorted(list(suivi_dir.glob("*.png")), key=lambda p: p.name)

print(f"Found {len(files)} files.", flush=True)
for f in files:
    print(f"\nProcessing: {f.name} ({f.stat().st_size} bytes)", flush=True)
    data = f.read_bytes()
    try:
        diag = diagnose_crop_image(data, declared_crop="manioc")
        print(f" -> Result for {f.name}:", flush=True)
        print(f"    disease_name: {diag.get('disease_name')}", flush=True)
        print(f"    severity:     {diag.get('severity')}", flush=True)
        print(f"    is_healthy:   {diag.get('is_healthy')}", flush=True)
        print(f"    confidence:   {diag.get('confidence')}%", flush=True)
        print(f"    is_valid:     {diag.get('is_valid_subject')}", flush=True)
    except Exception as e:
        import traceback
        print(f" -> ERROR: {e}", flush=True)
        traceback.print_exc()
