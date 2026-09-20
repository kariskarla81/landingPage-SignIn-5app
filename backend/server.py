from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any, Annotated
from pydantic.functional_validators import BeforeValidator
import uuid
from datetime import datetime, timezone
from bson import ObjectId

from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI(title="Elastech Production API")
api_router = APIRouter(prefix="/api")

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Module metadata (used for validation, AI prompting & labels)
# ---------------------------------------------------------------------------
MODULES: Dict[str, Dict[str, Any]] = {
    "khtt": {
        "title": "K-HTT Analyst",
        "description": "Analisa kualitas & karakteristik High Temperature Test pada produk minyak bumi.",
        "rating_options": ["Excellent", "Good", "Fair", "Poor", "Reject"],
        "parameters": [
            {"key": "appearance", "label": "Appearance", "unit": ""},
            {"key": "color", "label": "Color (ASTM D1500)", "unit": ""},
            {"key": "water_content", "label": "Water Content", "unit": "% vol"},
            {"key": "sediment", "label": "Sediment", "unit": "% wt"},
            {"key": "total_acid_number", "label": "Total Acid Number", "unit": "mg KOH/g"},
            {"key": "kinematic_viscosity", "label": "Kinematic Viscosity @40°C", "unit": "cSt"},
            {"key": "flash_point", "label": "Flash Point", "unit": "°C"},
            {"key": "thermal_stability", "label": "Thermal Stability Index", "unit": ""},
        ],
    },
    "copper-strip": {
        "title": "Copper Strip ASTM D130",
        "description": "Uji korosi bilah tembaga (copper strip corrosion) sesuai standar ASTM D130.",
        "rating_options": ["1a", "1b", "2a", "2b", "2c", "2d", "2e", "3a", "3b", "4a", "4b", "4c"],
        "parameters": [
            {"key": "test_temperature", "label": "Test Temperature", "unit": "°C"},
            {"key": "test_duration", "label": "Test Duration", "unit": "hours"},
            {"key": "strip_appearance", "label": "Strip Appearance", "unit": ""},
            {"key": "tarnish_level", "label": "Tarnish Level", "unit": ""},
            {"key": "bath_medium", "label": "Bath Medium", "unit": ""},
        ],
    },
    "rating-dka": {
        "title": "Rating DKA",
        "description": "Penilaian Deposit / Karbon / Aging (DKA) pada minyak pelumas & bahan bakar.",
        "rating_options": ["A - Sangat Baik", "B - Baik", "C - Cukup", "D - Kurang", "E - Buruk"],
        "parameters": [
            {"key": "deposit_level", "label": "Deposit Level", "unit": "merit"},
            {"key": "carbon_residue", "label": "Carbon Residue", "unit": "% wt"},
            {"key": "oxidation_stability", "label": "Oxidation Stability", "unit": "min"},
            {"key": "sludge_content", "label": "Sludge Content", "unit": "mg/100ml"},
            {"key": "varnish_rating", "label": "Varnish Rating", "unit": "merit"},
            {"key": "color_change", "label": "Color Change", "unit": ""},
        ],
    },
}


def require_module(module: str) -> Dict[str, Any]:
    meta = MODULES.get(module)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Unknown module '{module}'")
    return meta


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
def _to_str_id(v: Any) -> str:
    if isinstance(v, ObjectId):
        return str(v)
    return str(v)


PyObjectId = Annotated[str, BeforeValidator(_to_str_id)]


class SampleCreate(BaseModel):
    sample_code: str
    sample_name: str
    product_type: str = ""
    operator: str = ""
    test_date: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)
    rating: str = ""
    notes: str = ""


class Sample(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    module: str
    sample_code: str
    sample_name: str
    product_type: str = ""
    operator: str = ""
    test_date: str = ""
    parameters: Dict[str, Any] = Field(default_factory=dict)
    rating: str = ""
    notes: str = ""
    ai_analysis: Optional[str] = None
    ai_analyzed_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@api_router.get("/")
async def root():
    return {"message": "Elastech Production API"}


@api_router.get("/modules")
async def get_modules():
    return MODULES


@api_router.get("/modules/{module}")
async def get_module(module: str):
    return require_module(module)


@api_router.post("/{module}/samples", response_model=Sample)
async def create_sample(module: str, payload: SampleCreate):
    require_module(module)
    sample = Sample(module=module, **payload.model_dump())
    await db.samples.insert_one(sample.model_dump())
    return sample


@api_router.get("/{module}/samples", response_model=List[Sample])
async def list_samples(module: str):
    require_module(module)
    docs = await db.samples.find({"module": module}, {"_id": 0}).sort("created_at", -1).to_list(1000)
    return [Sample(**d) for d in docs]


@api_router.get("/{module}/samples/{sample_id}", response_model=Sample)
async def get_sample(module: str, sample_id: str):
    require_module(module)
    doc = await db.samples.find_one({"module": module, "id": sample_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Sample not found")
    return Sample(**doc)


@api_router.delete("/{module}/samples/{sample_id}")
async def delete_sample(module: str, sample_id: str):
    require_module(module)
    res = await db.samples.delete_one({"module": module, "id": sample_id})
    if res.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Sample not found")
    return {"success": True}


def _build_prompt(meta: Dict[str, Any], sample: Sample) -> str:
    lines = [
        f"Modul Pengujian: {meta['title']}",
        f"Deskripsi: {meta['description']}",
        "",
        f"Kode Sampel: {sample.sample_code}",
        f"Nama Sampel: {sample.sample_name}",
        f"Jenis Produk: {sample.product_type or '-'}",
        f"Operator: {sample.operator or '-'}",
        f"Tanggal Uji: {sample.test_date or '-'}",
        f"Rating / Klasifikasi: {sample.rating or '-'}",
        "",
        "Parameter Hasil Uji:",
    ]
    param_labels = {p["key"]: p for p in meta["parameters"]}
    for key, value in sample.parameters.items():
        p = param_labels.get(key, {"label": key, "unit": ""})
        unit = f" {p['unit']}" if p.get("unit") else ""
        lines.append(f"- {p['label']}: {value}{unit}")
    if sample.notes:
        lines.append("")
        lines.append(f"Catatan Operator: {sample.notes}")
    return "\n".join(lines)


@api_router.post("/{module}/samples/{sample_id}/analyze", response_model=Sample)
async def analyze_sample(module: str, sample_id: str):
    meta = require_module(module)
    doc = await db.samples.find_one({"module": module, "id": sample_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Sample not found")
    sample = Sample(**doc)

    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=500, detail="LLM key not configured")

    system_message = (
        "Anda adalah ahli laboratorium pengujian minyak bumi (petroleum testing) senior di Elastech Production. "
        "Tugas Anda menganalisa hasil pengujian laboratorium dan memberikan laporan analisa profesional dalam Bahasa Indonesia. "
        "Berikan analisa yang ringkas, terstruktur, dan berbasis standar industri (ASTM/ISO) yang relevan. "
        "Gunakan format dengan bagian berikut:\n"
        "1. RINGKASAN HASIL — kesimpulan singkat kondisi sampel.\n"
        "2. INTERPRETASI PARAMETER — bahas parameter kunci dan artinya.\n"
        "3. PENILAIAN KUALITAS — apakah memenuhi spesifikasi umum, disertai alasan.\n"
        "4. REKOMENDASI — langkah tindak lanjut / perbaikan.\n"
        "Jangan gunakan tabel markdown. Tulis maksimal 350 kata."
    )

    try:
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"analyze-{module}-{sample_id}",
            system_message=system_message,
        ).with_model("anthropic", "claude-sonnet-4-6")
        user_message = UserMessage(text=_build_prompt(meta, sample))
        analysis = await chat.send_message(user_message)
    except Exception as e:
        logger.exception("AI analysis failed")
        raise HTTPException(status_code=502, detail=f"AI analysis failed: {e}")

    analyzed_at = datetime.now(timezone.utc).isoformat()
    await db.samples.update_one(
        {"module": module, "id": sample_id},
        {"$set": {"ai_analysis": analysis, "ai_analyzed_at": analyzed_at}},
    )
    sample.ai_analysis = analysis
    sample.ai_analyzed_at = analyzed_at
    return sample


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
