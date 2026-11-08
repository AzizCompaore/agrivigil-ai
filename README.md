# AgriVigil AI — MVP fonctionnel (Vibeathon 2026)

Ce paquet contient une version **fonctionnelle et autonome** de l'application,
reconstruite à partir de l'export Base44 (`agri-vigil-smart`) :

```
agrivigil-ai/
├── frontend/    → React + Vite + Tailwind (l'interface exportée de Base44, adaptée)
└── backend/     → Django REST Framework (nouveau, à connecter au frontend)
```

## Ce qui a changé par rapport à l'export Base44

- Le SDK propriétaire `@base44/sdk` a été retiré. Le frontend utilise
  maintenant `frontend/src/api/apiClient.js`, un client REST classique qui
  parle à `backend/`.
- L'authentification (`AuthContext.jsx`) a été réécrite : la version exportée
  appelait une fonction (`createAxiosClient`) qui n'existait nulle part dans
  le code — elle n'aurait jamais fonctionné en dehors de Base44.
- Le Scan IA appelle **réellement Gemini 2.5 Flash** pour analyser l'image
  envoyée (voir `backend/core/ai_diagnosis.py`). ⚠️ Le projet visait
  initialement "Gemini 1.5 Flash", mais Google a définitivement arrêté toute
  la génération 1.5 mi-2026 (erreur 404 systématique) — j'ai donc basculé sur
  **Gemini 2.5 Flash**, le modèle Flash stable actuellement en production.
- La météo appelle **réellement OpenWeatherMap** (voir `backend/core/weather.py`).

Les deux nécessitent une clé API (voir section suivante). Sans clé, le
diagnostic IA bascule automatiquement sur un moteur simulé (pratique pour
développer sans compte Google), et la météo renvoie une erreur claire plutôt
que d'inventer des données.

## Clés API à configurer

Dans `backend/.env` (copié depuis `.env.example`) :

```
GEMINI_API_KEY=ta_cle_gemini
OPENWEATHER_API_KEY=ta_cle_openweathermap
```

- **Gemini** : crée une clé gratuite sur https://aistudio.google.com/apikey
  (compte Google requis, activation immédiate).
- **OpenWeatherMap** : crée un compte gratuit sur
  https://openweathermap.org/api → onglet "API keys". ⚠️ La clé met
  généralement **jusqu'à 2 heures** à s'activer après la création du compte —
  ne t'inquiète pas si tu as une erreur 401 juste après l'inscription.


## Démarrage rapide

### Déploiement en ligne (GitHub Pages + Render)

Le dépôt contient un workflow GitHub Actions pour publier le frontend sur
GitHub Pages et un Blueprint Render (`render.yaml`) pour créer l'API Django
et sa base PostgreSQL. GitHub Pages ne pouvant pas exécuter Django, les deux
services doivent être déployés.

1. Sur Render, crée un **Blueprint** à partir de ce dépôt et confirme la
   création de `agrivigil-ai-api` et `agrivigil-ai-db`. Le Blueprint démarre
   avec les offres gratuites : le serveur peut s'endormir après une période
   d'inactivité et la base gratuite est temporaire (30 jours). Pour une
   utilisation durable, choisis une base PostgreSQL payante et configure des
   sauvegardes.
2. Pour recevoir les codes d'inscription et de réinitialisation, crée un
   compte [Resend](https://resend.com/), vérifie un domaine expéditeur et
   configure dans **Render → agrivigil-ai-api → Environment** :
   `EMAIL_HOST_PASSWORD` (clé SMTP Resend) et `DEFAULT_FROM_EMAIL` (adresse
   vérifiée, par exemple `AgriVigil AI <noreply@ton-domaine.com>`). Ne partage
   jamais ces valeurs dans le dépôt. Sans ces deux variables, l'inscription
   et la réinitialisation de mot de passe ne peuvent pas envoyer de code.
3. Après le premier déploiement Render, copie l'URL publique de l'API, par
   exemple `https://agrivigil-ai-api.onrender.com`. Dans GitHub, ouvre
   **Settings → Secrets and variables → Actions → Variables**, ajoute
   `VITE_API_BASE_URL` avec cette URL (sans `/api`).
4. Dans GitHub, ouvre **Settings → Pages**, choisis **GitHub Actions** comme
   source, puis lance le workflow **Deploy frontend to GitHub Pages** depuis
   l'onglet **Actions**. Les prochaines modifications du frontend publiées
   sur `main` déclencheront automatiquement le déploiement.

L'application sera disponible à l'adresse
`https://azizcompaore.github.io/agrivigil-ai/`. Les routes utilisent des
fragments (`/#/login`) pour fonctionner sur GitHub Pages, et les appels
frontend utilisent l'API Render. Après avoir renseigné `VITE_API_BASE_URL`,
relance le workflow pour intégrer l'adresse de l'API au frontend.

Les services optionnels doivent aussi être configurés dans Render pour
activer leurs fonctions : `GEMINI_API_KEY` (diagnostic IA),
`OPENWEATHER_API_KEY` (météo), et les identifiants
`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
pour conserver les images de scans malgré les redémarrages du serveur.

### Lancement officiel pour le jury (une seule commande)

Prérequis : Docker Desktop installé et lancé.

1. Copier le fichier d’environnement de base :

```bash
copy .env.example .env
```

Sur Linux/macOS, remplacer par :

```bash
cp .env.example .env
```

2. Lancer l’application depuis la racine du projet :

```bash
docker compose up --build
```

Une fois démarré :
- Frontend : http://localhost:5173/
- Backend API : http://localhost:8000/api/

> La commande ci-dessus démarre automatiquement le backend Django et le frontend Vite avec la configuration adaptée au projet.

### Lancement manuel (si Docker n’est pas disponible)

#### 1. Backend (Django)

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # ou .\venv\Scripts\activate sous Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_experts       # crée les 4 experts du Hub Experts
python manage.py createsuperuser    # optionnel, pour /admin/
python manage.py runserver
```

L'API tourne sur http://localhost:8000/api/.

#### 2. Frontend (React/Vite)

```bash
cd frontend
npm install
npm run dev
```

L'appli tourne sur http://localhost:5173/.

## Endpoints REST disponibles

| Méthode | Endpoint                          | Description                                  |
|---------|------------------------------------|-----------------------------------------------|
| POST    | `/api/auth/register/`              | Inscription (déclenche un code OTP)          |
| POST    | `/api/auth/verify-otp/`            | Valide le code, retourne les tokens JWT      |
| POST    | `/api/auth/resend-otp/`            | Renvoie un code                              |
| POST    | `/api/auth/login/`                 | Connexion email/mot de passe                 |
| POST    | `/api/auth/token/refresh/`         | Rafraîchit le token d'accès                  |
| GET     | `/api/auth/me/`                    | Profil de l'utilisateur connecté             |
| POST    | `/api/auth/logout/`                | Déconnexion                                   |
| POST    | `/api/auth/forgot-password/`       | Demande de réinitialisation                  |
| POST    | `/api/auth/reset-password/`        | Réinitialisation du mot de passe             |
| GET/POST| `/api/scans/`                      | Historique des scans / créer un scan brut    |
| POST    | `/api/scans/analyze/`              | Envoie une image → diagnostic IA complet     |
| GET/POST| `/api/alerts/`                     | Alertes sanitaires communautaires            |
| GET/POST| `/api/calculator/`                 | Historique / calcul d'engrais NPK            |
| GET     | `/api/experts/`                    | Annuaire des experts (Hub Experts)            |
| GET/POST| `/api/experts/messages/`           | Messagerie experts (réponse simulée auto)     |
| GET     | `/api/weather/?city=Abidjan`       | Météo agricole du jour                        |
| GET     | `/api/weather/cities/`             | Liste des villes ivoiriennes disponibles      |

**Note sur le "temps réel"** : conformément à ta demande d'endpoints REST
propres pour le MVP, il n'y a pas de WebSocket. Les composants qui
affichaient un flux en direct (alertes communautaires, chat experts) font
un **polling léger** (toutes les 6 secondes) côté frontend — voir la méthode
`subscribe()` dans `apiClient.js`. C'est transparent pour l'utilisateur et
largement suffisant pour un MVP de hackathon ; tu pourras migrer vers Django
Channels plus tard sans changer l'interface des composants.

## Limitations connues du MVP

- SQLite en développement local ; le Blueprint Render utilise PostgreSQL
  en production.
- En développement, les codes OTP sont affichés dans la console Django.
  En production, un SMTP Resend vérifié est requis pour envoyer les codes
  d'inscription et de réinitialisation (voir la configuration de déploiement).
- La connexion Google (bouton présent dans l'UI) n'est pas branchée — elle
  affiche un message clair plutôt que de planter.
- Le diagnostic IA (Gemini) et la météo (OpenWeatherMap) nécessitent tes
  propres clés API — voir la section ci-dessus. Sans clé Gemini, le scan
  fonctionne quand même via un moteur de secours simulé ; sans clé
  OpenWeatherMap, l'écran météo renverra une erreur explicite tant que la
  clé n'est pas configurée.
