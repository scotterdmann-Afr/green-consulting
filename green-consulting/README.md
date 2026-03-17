# Green Consulting — Plateforme de gestion devis & factures

## Structure du projet

```
green-consulting/
├── backend/                  ← API Python FastAPI
│   ├── main.py               ← Tous les endpoints API
│   ├── generate_doc.py       ← Moteur de génération Excel
│   ├── requirements.txt      ← Dépendances Python
│   ├── scripts/
│   │   └── recalc.py         ← Recalcul LibreOffice (montant en lettres)
│   └── templates/
│       ├── template_devis_vierge.xlsx
│       └── Template_facture_vierge.xlsx
├── frontend/                 ← App React / Next.js
│   └── src/
│       ├── app/              ← Pages Next.js
│       ├── components/       ← Composants React
│       └── lib/
│           └── api.ts        ← Appels vers le backend
├── render.yaml               ← Config déploiement Render
└── .env.example              ← Variables d'environnement à copier
```

---

## Déploiement en 5 étapes

### Étape 1 — Préparer GitHub

1. Crée un compte sur https://github.com si tu n'en as pas
2. Crée un nouveau repository appelé `green-consulting`
3. Upload tout le contenu de ce dossier dedans

### Étape 2 — Déployer le backend sur Render

1. Va sur https://render.com et crée un compte gratuit
2. Clique **"New +"** → **"Web Service"**
3. Connecte ton repo GitHub `green-consulting`
4. Paramètres à remplir :
   - **Root Directory** : `backend`
   - **Build Command** : `pip install -r requirements.txt`
   - **Start Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type** : Free
5. Dans **"Environment Variables"**, ajoute :
   - `ANTHROPIC_API_KEY` = ta clé API Anthropic (sur console.anthropic.com)
6. Clique **"Create Web Service"**
7. Attends 3-5 min → tu obtiens une URL genre :
   `https://green-consulting-api.onrender.com`

> ⚠️ **Note Render gratuit** : le service s'endort après 15 min d'inactivité.
> Le premier appel après une pause prend ~30 secondes. Suffisant pour démarrer.

### Étape 3 — Déployer le frontend sur Vercel

1. Va sur https://vercel.com et crée un compte gratuit
2. Clique **"New Project"** → connecte ton repo GitHub
3. **Root Directory** : `frontend`
4. Dans **"Environment Variables"**, ajoute :
   - `NEXT_PUBLIC_API_URL` = l'URL Render obtenue à l'étape 2
5. Clique **"Deploy"**
6. Tu obtiens une URL genre : `https://green-consulting.vercel.app`

### Étape 4 — Tester

Ouvre ton URL Vercel, uploade une capture Excel, vérifie que le devis se génère.

Pour tester le backend seul, va sur :
`https://green-consulting-api.onrender.com/docs`
→ Interface Swagger interactive avec tous les endpoints.

### Étape 5 — Partager à ton équipe

Envoie simplement l'URL Vercel à tes 2-5 collègues. Rien à installer.

---

## Endpoints API disponibles

| Méthode | URL | Description |
|---------|-----|-------------|
| `POST` | `/api/extract-image` | Envoie une image, reçoit les articles JSON |
| `POST` | `/api/generate-devis` | Envoie les données, reçoit le .xlsx devis |
| `POST` | `/api/generate-facture` | Envoie les données, reçoit le .xlsx facture |
| `GET`  | `/` | Health check |
| `GET`  | `/docs` | Documentation Swagger automatique |

---

## Variables d'environnement

Copie `.env.example` :
- En `.env` dans `/backend` pour développement local
- En variables d'environnement dans Render pour la production

---

## Développement local

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# → http://localhost:8000

# Frontend
cd frontend
npm install
npm run dev
# → http://localhost:3000
```
