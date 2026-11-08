import os
import shutil
import django
from datetime import datetime, timezone
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.conf import settings
from core.models import User, CropScanTracking, CropScan

# 1. Copie des images avec des noms propres
src_dir = settings.MEDIA_ROOT / "scans" / "test suivi"
dst_dir = settings.MEDIA_ROOT / "scans" / "2026" / "10"
dst_dir.mkdir(parents=True, exist_ok=True)

# Correspondance des images de la simulation
image_map = {
    "manioc_suivi_j1_critique.png": "Capture d'écran 2026-10-22 100110.png",
    "manioc_suivi_j2_elevee.png": "Capture d'écran 2026-10-22 100110.png",
    "manioc_suivi_j3_moderee.png": "Capture d'écran 2026-10-22 100134.png",
    "manioc_suivi_j4_moderee.png": "Capture d'écran 2026-10-22 100134.png",
    "manioc_suivi_j5_faible.png": "Capture d'écran 2026-10-22 100149.png",
    "manioc_suivi_j6_gueri.png": "Capture d'écran 2026-10-22 100204.png",
}

for dst_name, src_name in image_map.items():
    src_path = src_dir / src_name
    if not src_path.exists():
        # Fallback si l'encodage sur le disque a des caractères de remplacement
        matching = [p for p in src_dir.iterdir() if src_name[:15] in p.name]
        if matching:
            src_path = matching[0]
    dst_path = dst_dir / dst_name
    shutil.copy2(src_path, dst_path)
    print(f"Copié {src_path.name} -> {dst_name} ({dst_path.stat().st_size} octets)")

# 2. Utilisateur et Tracking
user = User.objects.filter(email="azizcompaore252@gmail.com").first() or User.objects.first()
if not user:
    print("Erreur: aucun utilisateur trouvé.")
    exit(1)

# Récupérer ou créer le tracking Manioc
tracking = CropScanTracking.objects.filter(owner=user, name__icontains="Manioc").first()
if not tracking:
    tracking = CropScanTracking.objects.create(
        owner=user,
        name="Manioc – Parcelle A",
        status="active"
    )
else:
    tracking.name = "Manioc – Mosaïque (CMD)"
    tracking.status = "active"
    tracking.save()

# Mettre à jour sa date de création au 17 Octobre 2026
tracking_date = datetime(2026, 10, 17, 8, 30, 0, tzinfo=timezone.utc)
CropScanTracking.objects.filter(id=tracking.id).update(created_date=tracking_date, updated_date=datetime(2026, 10, 22, 10, 0, 0, tzinfo=timezone.utc))

# Nettoyer les anciens scans attachés à ce tracking pour avoir une belle courbe propre
old_scans = CropScan.objects.filter(tracking=tracking)
print(f"Suppression de {old_scans.count()} anciens scans du tracking...")
old_scans.delete()

# 3. Création des 6 scans journaliers progressifs (du 17 au 22 Octobre 2026)
scans_data = [
    {
        "day": 1,
        "date": datetime(2026, 10, 17, 9, 0, 0, tzinfo=timezone.utc),
        "severity": "critique",
        "confidence": 96.0,
        "is_healthy": False,
        "status": "active",
        "image": "scans/2026/10/manioc_suivi_j1_critique.png",
        "symptoms": "Mosaïque jaune sévère sur l'ensemble des folioles, déformations et crispations accentuées des feuilles.",
        "remedy": "Pulvérisation d'un biopesticide à l'huile de neem (5ml/L) le matin pour éliminer l'aleurode Bemisia tabaci (vecteur de la mosaïque). Élimination des adventices hôtes.",
        "dosage": "5 ml d'huile de neem par litre d'eau, renouveler tous les 3 jours.",
        "notes": "Jour 1 : Détection initiale critique. Forte attaque virale avec risque de transmission aux plants voisins. Traitement d'urgence appliqué.",
    },
    {
        "day": 2,
        "date": datetime(2026, 10, 18, 9, 30, 0, tzinfo=timezone.utc),
        "severity": "élevée",
        "confidence": 93.0,
        "is_healthy": False,
        "status": "treated",
        "image": "scans/2026/10/manioc_suivi_j2_elevee.png",
        "symptoms": "Feuilles médianes encore fortement marbrées, mais arrêt de l'extension de l'infection sur l'apex végétatif.",
        "remedy": "Deuxième application d'extrait de neem + purin d'ortie dilué pour fortifier les défenses foliaires.",
        "dosage": "Purin d'ortie à 10% en pulvérisation le soir.",
        "notes": "Jour 2 : Début de stabilisation. Population de mouches blanches en nette régression sous les feuilles.",
    },
    {
        "day": 3,
        "date": datetime(2026, 10, 19, 9, 15, 0, tzinfo=timezone.utc),
        "severity": "modérée",
        "confidence": 89.0,
        "is_healthy": False,
        "status": "treated",
        "image": "scans/2026/10/manioc_suivi_j3_moderee.png",
        "symptoms": "Régression notable des chloroses. Les nouvelles feuilles se développent avec une couleur verte dominante.",
        "remedy": "Apport de compost organique riche en potassium et maintien de l'arrosage au pied.",
        "dosage": "2 kg de compost mûr par poquet, enfouissement superficiel.",
        "notes": "Jour 3 : Amélioration visible. La surface foliaire photosynthétique active ré-augmente sensiblement.",
    },
    {
        "day": 4,
        "date": datetime(2026, 10, 20, 10, 0, 0, tzinfo=timezone.utc),
        "severity": "modérée",
        "confidence": 87.0,
        "is_healthy": False,
        "status": "treated",
        "image": "scans/2026/10/manioc_suivi_j4_moderee.png",
        "symptoms": "Marbrures jaunes résiduelles très localisées. Bonne tenue des folioles.",
        "remedy": "Paillage végétal pour préserver l'humidité du sol et prévenir le stress hydrique.",
        "dosage": "Couche de 5 cm de paille sèche autour du pied.",
        "notes": "Jour 4 : Évolution favorable confirmée. Plante en phase active de convalescence.",
    },
    {
        "day": 5,
        "date": datetime(2026, 10, 21, 9, 45, 0, tzinfo=timezone.utc),
        "severity": "faible",
        "confidence": 91.0,
        "is_healthy": False,
        "status": "treated",
        "image": "scans/2026/10/manioc_suivi_j5_faible.png",
        "symptoms": "Quasi-disparition des symptômes. Folioles vertes, fermes et bien déployées avec seulement d'infimes nuances résiduelles.",
        "remedy": "Arrêt des pulvérisations, simple maintien de l'arrosage et surveillance sanitaire.",
        "dosage": "Arrosage matinal standard.",
        "notes": "Jour 5 : Stade de guérison très avancée. La plante a reconstitué sa vigueur normale.",
    },
    {
        "day": 6,
        "date": datetime(2026, 10, 22, 10, 0, 0, tzinfo=timezone.utc),
        "severity": "faible",
        "confidence": 98.0,
        "is_healthy": True,
        "status": "resolved",
        "image": "scans/2026/10/manioc_suivi_j6_gueri.png",
        "symptoms": "Feuille parfaitement saine, vert profond homogène, sans distorsion ni chlorose.",
        "remedy": "Plante guérie et consolidée. Maintenir une surveillance préventive hebdomadaire du feuillage.",
        "dosage": "Aucun traitement curatif nécessaire.",
        "notes": "Jour 6 : Guérison complète constatée ! La plante a totalement surmonté l'infection. Suivi validé avec succès.",
    },
]

for item in scans_data:
    scan = CropScan.objects.create(
        owner=user,
        tracking=tracking,
        crop_name="Manioc",
        disease_name="Mosaïque africaine du manioc (CMD)",
        severity=item["severity"],
        confidence=item["confidence"],
        is_healthy=item["is_healthy"],
        status=item["status"],
        image=item["image"],
        symptoms=item["symptoms"],
        remedy=item["remedy"],
        dosage=item["dosage"],
        prevention="Utiliser des boutures certifiées saines et résistantes, désinfecter les outils, contrôler régulièrement les aleurodes.",
        notes=item["notes"],
        location_lat=5.3599,
        location_lng=-4.0083,
    )
    # Mettre à jour created_date
    CropScan.objects.filter(id=scan.id).update(created_date=item["date"], updated_date=item["date"])
    print(f"Créé scan Jour {item['day']} ({item['date'].strftime('%d/%m')}) - Gravité: {item['severity']} - ID: {scan.id}")

print("\nSimulation de suivi Manioc initialisée avec succès !")
