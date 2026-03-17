from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import anthropic
import base64
import json
import uuid
import os
import shutil
from datetime import datetime
from generate_doc import generate_devis, generate_facture
import subprocess

app = FastAPI(title="Green Consulting API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En prod: remplacer par ton domaine Vercel
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "/tmp/uploads"
OUTPUT_DIR = "/tmp/outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEMPLATE_DEVIS = os.path.join(os.path.dirname(__file__), "templates/template_devis_vierge.xlsx")
TEMPLATE_FACTURE = os.path.join(os.path.dirname(__file__), "templates/Template_facture_vierge.xlsx")
RECALC_SCRIPT = os.path.join(os.path.dirname(__file__), "scripts/recalc.py")


# ─── MODÈLES ───────────────────────────────────────────────────────────────

class Item(BaseModel):
    designation: str
    quantite: float
    unite: str = "u"
    prix_unitaire: float

class DevisData(BaseModel):
    date: str
    numero: str
    client: str
    categorie: Optional[str] = ""
    sous_categorie: Optional[str] = ""
    items: List[Item]
    livraison: Optional[str] = "-"

class FactureData(BaseModel):
    date: str
    numero: str
    client: str
    da: Optional[str] = ""
    categorie: Optional[str] = ""
    items: List[Item]
    modalites: Optional[str] = "Le solde à la livraison"


# ─── ENDPOINT 1 : Extraire les données d'une capture Excel ────────────────

@app.post("/api/extract-image")
async def extract_image(file: UploadFile = File(...)):
    """Reçoit une image de capture Excel, retourne les données extraites par IA."""
    content = await file.read()
    b64 = base64.b64encode(content).decode()
    media_type = file.content_type or "image/png"

    client = anthropic.Anthropic()  # utilise ANTHROPIC_API_KEY depuis l'env
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": b64}
                },
                {
                    "type": "text",
                    "text": (
                        "Extrais toutes les lignes articles de cette capture Excel de devis. "
                        "Réponds UNIQUEMENT en JSON valide, sans balises markdown:\n"
                        '{"items":[{"designation":"","quantite":1,"unite":"u","prix_unitaire":0}],'
                        '"reference":"","client":""}'
                    )
                }
            ]
        }]
    )

    raw = response.content[0].text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(raw)
    return data


# ─── ENDPOINT 2 : Générer un devis Excel ──────────────────────────────────

@app.post("/api/generate-devis")
async def generate_devis_endpoint(data: DevisData):
    """Génère le fichier devis .xlsx à partir des données."""
    file_id = str(uuid.uuid4())[:8]
    output_path = os.path.join(OUTPUT_DIR, f"DE_{file_id}_{data.client.replace(' ','_')}.xlsx")

    payload = {
        "date": data.date,
        "numero": data.numero,
        "client": data.client,
        "categorie": data.categorie,
        "sous_categorie": data.sous_categorie,
        "items": [i.dict() for i in data.items],
        "livraison": data.livraison,
    }

    generate_devis(payload, TEMPLATE_DEVIS, output_path)

    # Recalcul LibreOffice pour montant en lettres
    subprocess.run(["python3", RECALC_SCRIPT, output_path, "30"], check=True)

    filename = f"{data.numero}_{data.client}.xlsx"
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )


# ─── ENDPOINT 3 : Générer une facture Excel ───────────────────────────────

@app.post("/api/generate-facture")
async def generate_facture_endpoint(data: FactureData):
    """Génère le fichier facture .xlsx à partir des données."""
    file_id = str(uuid.uuid4())[:8]
    output_path = os.path.join(OUTPUT_DIR, f"FA_{file_id}_{data.client.replace(' ','_')}.xlsx")

    payload = {
        "date": data.date,
        "numero": data.numero,
        "client": data.client,
        "da": data.da,
        "categorie": data.categorie,
        "items": [i.dict() for i in data.items],
        "modalites": data.modalites,
    }

    generate_facture(payload, TEMPLATE_FACTURE, output_path)
    subprocess.run(["python3", RECALC_SCRIPT, output_path, "30"], check=True)

    filename = f"{data.numero}_{data.client}.xlsx"
    return FileResponse(
        output_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=filename
    )


# ─── HEALTH CHECK ─────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "app": "Green Consulting API", "version": "1.0"}
