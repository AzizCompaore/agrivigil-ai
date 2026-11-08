"""
seed_manioc_scans.py
--------------------
Injecte des scans journaliers simulés sur le carnet "Manioc" pour tester
la courbe d'évolution dans le Carnet de Santé.

Scénario : Mosaïque africaine du manioc détectée il y a 14 jours,
aggravation progressive jusqu'à un pic critique à J-7, puis légère
amélioration après traitement (début J-5).
"""

import os
import django
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.core.files.base import ContentFile
from core.models import CropScan, CropScanTracking, User

USER_ID     = "9b94f85d-dbed-4311-b9ce-7b5de605bda3"
TRACKING_ID = "d906a678-2ef9-4ae3-a031-ff24e7de6dfd"

user     = User.objects.get(pk=USER_ID)
tracking = CropScanTracking.objects.get(pk=TRACKING_ID)

SCENARIO = [
    (14, "faible",   False, "Mosaique africaine du manioc",  62.0),
    (13, "faible",   False, "Mosaique africaine du manioc",  65.3),
    (12, "moderee",  False, "Mosaique africaine du manioc",  70.1),
    (11, "moderee",  False, "Mosaique africaine du manioc",  74.8),
    (10, "moderee",  False, "Mosaique africaine du manioc",  76.5),
    ( 9, "elevee",   False, "Mosaique africaine du manioc",  81.2),
    ( 8, "elevee",   False, "Mosaique africaine du manioc",  85.0),
    ( 7, "critique", False, "Mosaique africaine du manioc",  91.4),
    ( 6, "critique", False, "Mosaique africaine du manioc",  89.7),
    ( 5, "elevee",   False, "Mosaique africaine du manioc",  83.3),
    ( 4, "elevee",   False, "Mosaique africaine du manioc",  78.9),
    ( 3, "moderee",  False, "Mosaique africaine du manioc",  72.0),
    ( 2, "moderee",  False, "Mosaique africaine du manioc",  66.5),
    ( 1, "faible",   False, "Mosaique africaine du manioc",  59.1),
    ( 0, "faible",   False, "Mosaique africaine du manioc",  54.8),
]

SEVERITY_MAP = {
    "faible":   "faible",
    "moderee":  "mod\u00e9r\u00e9e",
    "elevee":   "\u00e9lev\u00e9e",
    "critique": "critique",
}

REMEDY     = "Arracher et detruire les plants atteints. Utiliser exclusivement des boutures saines certifiees."
DOSAGE     = "Aucun traitement chimique efficace — lutte par varietes resistantes uniquement."
SYMPTOMS   = "Feuilles mosaiquees (melange de vert clair et fonce), deformees et reduites. Nervures decolorees."
PREVENTION = "Rotation des cultures, lutte contre la mouche blanche (vecteur), boutures certifiees."


def make_svg(severity_key: str) -> bytes:
    colors = {"faible": "#4CAF50", "moderee": "#FF9800", "elevee": "#FF5722", "critique": "#B71C1C"}
    labels = {"faible": "Faible", "moderee": "Moderee", "elevee": "Elevee", "critique": "Critique"}
    color = colors.get(severity_key, "#9E9E9E")
    label = labels.get(severity_key, severity_key)
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">'
        f'<rect width="200" height="200" fill="{color}" rx="12"/>'
        f'<text x="100" y="90" text-anchor="middle" font-family="Arial" font-size="12" fill="white" font-weight="bold">Manioc - Mosaique</text>'
        f'<text x="100" y="112" text-anchor="middle" font-family="Arial" font-size="11" fill="white">Gravite : {label}</text>'
        f'<text x="100" y="130" text-anchor="middle" font-family="Arial" font-size="9" fill="rgba(255,255,255,0.8)">Scan simule</text>'
        '</svg>'
    )
    return svg.encode("utf-8")


now = datetime.now(tz=timezone.utc)
created_count = 0

for days_ago, severity_key, is_healthy, disease_name, confidence in SCENARIO:
    severity_db = SEVERITY_MAP[severity_key]
    scan_time = now - timedelta(days=days_ago)
    scan_time = scan_time.replace(hour=8 + (days_ago % 4), minute=10 + days_ago % 50, second=0, microsecond=0)

    scan = CropScan(
        owner=user,
        tracking=tracking,
        crop_name="manioc",
        disease_name=disease_name,
        severity=severity_db,
        is_healthy=is_healthy,
        remedy=REMEDY,
        dosage=DOSAGE,
        symptoms=SYMPTOMS,
        prevention=PREVENTION,
        confidence=confidence,
        notes="plante",
        status="active",
    )

    svg_bytes = make_svg(severity_key)
    filename = f"sim_manioc_j{days_ago}_{severity_key}.svg"
    scan.image.save(filename, ContentFile(svg_bytes), save=False)
    scan.save()

    CropScan.objects.filter(pk=scan.pk).update(created_date=scan_time, updated_date=scan_time)

    print(f"  OK  J-{days_ago:02d}  [{severity_db:<10}]  conf={confidence}%")
    created_count += 1

print(f"\nTermine : {created_count} scans injectes dans le carnet '{tracking.name}'.")
