// Remplace cette URL par celle de ton backend Render après déploiement
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function extractImage(file: File) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch(`${API_BASE}/api/extract-image`, {
    method: "POST",
    body: form,
  });
  if (!res.ok) throw new Error("Extraction IA échouée");
  return res.json();
}

export async function generateDevis(data: object) {
  const res = await fetch(`${API_BASE}/api/generate-devis`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Génération devis échouée");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `devis_${Date.now()}.xlsx`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function generateFacture(data: object) {
  const res = await fetch(`${API_BASE}/api/generate-facture`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Génération facture échouée");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `facture_${Date.now()}.xlsx`;
  a.click();
  URL.revokeObjectURL(url);
}
