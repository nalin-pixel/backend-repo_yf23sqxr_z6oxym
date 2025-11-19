import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product as ProductSchema, QuoteRequest as QuoteRequestSchema

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: str
    images: List[str] = []
    specs: dict = {}
    tags: List[str] = []
    price_from: Optional[float] = None
    in_stock: bool = True


@app.get("/")
def read_root():
    return {"message": "Ergo B2B backend running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = getattr(db, 'name', None) or "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


def _serialize_product(doc) -> ProductOut:
    return ProductOut(
        id=str(doc.get("_id")),
        title=doc.get("title"),
        description=doc.get("description"),
        category=doc.get("category"),
        images=doc.get("images", []),
        specs=doc.get("specs", {}),
        tags=doc.get("tags", []),
        price_from=doc.get("price_from"),
        in_stock=doc.get("in_stock", True),
    )


def _ensure_seed_data():
    if db is None:
        return
    count = db["product"].count_documents({})
    if count == 0:
        samples: List[ProductSchema] = [
            ProductSchema(
                title="ErgoPro Mesh Chair",
                description="Breathable mesh, adaptive lumbar support, 4D armrests.",
                category="chair",
                images=[
                    "https://images.unsplash.com/photo-1582582429416-0ef2559c1dda?q=80&w=1200&auto=format&fit=crop",
                ],
                specs={
                    "Back": "High back mesh",
                    "Lumbar": "Dynamic",
                    "Armrests": "4D adjustable",
                    "Base": "Aluminum",
                },
                tags=["chair", "mesh", "lumbar"],
                price_from=329.0,
            ),
            ProductSchema(
                title="Executive Comfort Chair",
                description="Premium foam seat with headrest and synchro-tilt.",
                category="chair",
                images=[
                    "https://images.unsplash.com/photo-1582582429119-9f928eb6a0c0?q=80&w=1200&auto=format&fit=crop",
                ],
                specs={
                    "Mechanism": "Synchro-tilt",
                    "Headrest": "Adjustable",
                    "Seat": "High-density foam",
                },
                tags=["chair", "executive"],
                price_from=399.0,
            ),
            ProductSchema(
                title="Anti-Fatigue Standing Mat",
                description="Closed-cell polyurethane with beveled edges.",
                category="mat",
                images=[
                    "https://images.unsplash.com/photo-1598300183423-5bea7a1e9adb?q=80&w=1200&auto=format&fit=crop",
                ],
                specs={
                    "Material": "Polyurethane",
                    "Thickness": "0.75 in",
                    "Edges": "Trip-free beveled",
                },
                tags=["mat", "standing desk"],
                price_from=89.0,
            ),
            ProductSchema(
                title="XL Anti-Fatigue Mat",
                description="Extra-wide coverage for collaborative workstations.",
                category="mat",
                images=[
                    "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?q=80&w=1200&auto=format&fit=crop",
                ],
                specs={
                    "Material": "PU + Gel core",
                    "Width": "48 in",
                },
                tags=["mat", "xl"],
                price_from=129.0,
            ),
        ]
        for s in samples:
            create_document("product", s)


@app.get("/api/products", response_model=List[ProductOut])
def list_products(category: Optional[str] = None):
    _ensure_seed_data()
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    filter_q = {"category": category} if category else {}
    docs = get_documents("product", filter_q)
    return [_serialize_product(d) for d in docs]


@app.post("/api/quotes")
def create_quote(payload: QuoteRequestSchema):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    quote_id = create_document("quoterequest", payload)
    return {"id": quote_id, "status": "received"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
