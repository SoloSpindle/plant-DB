from __future__ import annotations

from datetime import date, datetime

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Plant, PlantLog, PlantLogType, PlantStage, PlantStatus

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def dashboard(
    request: Request,
    q: str = "",
    stage: str = "",
    strain: str = "",
    pot_size: str = "",
    db: Session = Depends(get_db),
):
    plants_query = db.query(Plant).filter(Plant.status == PlantStatus.ACTIVE)
    if q:
        query = f"%{q}%"
        plants_query = plants_query.filter((Plant.name.ilike(query)) | (Plant.strain_name.ilike(query)))
    if stage:
        plants_query = plants_query.filter(Plant.current_stage == stage)
    if strain:
        plants_query = plants_query.filter(Plant.strain_name == strain)
    if pot_size:
        plants_query = plants_query.filter(Plant.pot_size == pot_size)

    plants = plants_query.order_by(Plant.updated_at.desc()).all()

    cards = []
    now_dt = datetime.utcnow()
    for plant in plants:
        last_watered = (
            db.query(PlantLog)
            .filter(PlantLog.plant_id == plant.id, PlantLog.log_type == PlantLogType.WATERING)
            .order_by(PlantLog.timestamp.desc())
            .first()
        )
        last_stage_log = (
            db.query(PlantLog)
            .filter(PlantLog.plant_id == plant.id, PlantLog.log_type == PlantLogType.STAGE_CHANGE)
            .order_by(PlantLog.timestamp.desc())
            .first()
        )
        stage_start_date = (last_stage_log.timestamp.date() if last_stage_log else plant.sprout_date)
        cards.append(
            {
                "plant": plant,
                "days_since_sprout": (now_dt.date() - plant.sprout_date).days,
                "days_in_stage": (now_dt.date() - stage_start_date).days,
                "last_watered": last_watered.timestamp if last_watered else None,
            }
        )

    strains = [
        row[0]
        for row in db.query(Plant.strain_name)
        .filter(Plant.status == PlantStatus.ACTIVE)
        .distinct()
        .order_by(func.lower(Plant.strain_name))
        .all()
    ]
    pot_sizes = [
        row[0]
        for row in db.query(Plant.pot_size)
        .filter(Plant.status == PlantStatus.ACTIVE)
        .distinct()
        .order_by(func.lower(Plant.pot_size))
        .all()
    ]

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "cards": cards,
            "stages": [s.value for s in PlantStage],
            "strains": strains,
            "pot_sizes": pot_sizes,
            "filters": {"q": q, "stage": stage, "strain": strain, "pot_size": pot_size},
        },
    )


@router.get("/plants/new")
def new_plant_form(request: Request):
    return templates.TemplateResponse(
        "plant_form.html",
        {
            "request": request,
            "stages": [s.value for s in PlantStage],
            "statuses": [s.value for s in PlantStatus],
            "today": date.today().isoformat(),
        },
    )


@router.post("/plants/new")
def create_plant(
    name: str = Form(...),
    strain_name: str = Form(...),
    sprout_date: str = Form(...),
    current_stage: str = Form(...),
    pot_size: str = Form(...),
    substrate_type: str = Form(...),
    nutrient_line: str = Form(...),
    phenotype_code: str = Form(""),
    nfc_tag_id: str = Form(""),
    care_maintenance_rating: int | None = Form(None),
    overall_pheno_rating: int | None = Form(None),
    notes: str = Form(""),
    status: str = Form("Active"),
    db: Session = Depends(get_db),
):
    if nfc_tag_id:
        existing = db.query(Plant).filter(Plant.nfc_tag_id == nfc_tag_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="NFC tag ID already assigned")

    plant = Plant(
        name=name.strip(),
        strain_name=strain_name.strip(),
        sprout_date=datetime.strptime(sprout_date, "%Y-%m-%d").date(),
        current_stage=PlantStage(current_stage),
        pot_size=pot_size.strip(),
        substrate_type=substrate_type.strip(),
        nutrient_line=nutrient_line.strip(),
        phenotype_code=phenotype_code.strip() or None,
        nfc_tag_id=nfc_tag_id.strip() or None,
        care_maintenance_rating=care_maintenance_rating,
        overall_pheno_rating=overall_pheno_rating,
        notes=notes.strip() or None,
        status=PlantStatus(status),
    )
    db.add(plant)
    db.commit()
    db.refresh(plant)

    return RedirectResponse(url=f"/plant/{plant.id}", status_code=303)


@router.get("/scan/{nfc_tag_id}")
def scan_view(request: Request, nfc_tag_id: str, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.nfc_tag_id == nfc_tag_id).first()
    assignable_plants = (
        db.query(Plant)
        .filter(Plant.status == PlantStatus.ACTIVE)
        .order_by(Plant.name.asc())
        .all()
    )
    return templates.TemplateResponse(
        "scan.html",
        {
            "request": request,
            "nfc_tag_id": nfc_tag_id,
            "plant": plant,
            "plants": assignable_plants,
            "stages": [s.value for s in PlantStage],
        },
    )


@router.post("/scan/{nfc_tag_id}/assign")
def assign_tag(
    nfc_tag_id: str,
    plant_id: int = Form(...),
    db: Session = Depends(get_db),
):
    existing = db.query(Plant).filter(Plant.nfc_tag_id == nfc_tag_id).first()
    if existing and existing.id != plant_id:
        raise HTTPException(status_code=400, detail="Tag already assigned")

    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    plant.nfc_tag_id = nfc_tag_id
    plant.updated_at = datetime.utcnow()
    db.commit()
    return RedirectResponse(url=f"/scan/{nfc_tag_id}", status_code=303)


@router.get("/plant/{plant_id}")
def plant_detail(request: Request, plant_id: int, db: Session = Depends(get_db)):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    logs = db.query(PlantLog).filter(PlantLog.plant_id == plant.id).order_by(PlantLog.timestamp.desc()).all()
    photos = sorted(plant.photos, key=lambda p: p.timestamp, reverse=True)

    return templates.TemplateResponse(
        "plant_detail.html",
        {
            "request": request,
            "plant": plant,
            "logs": logs,
            "photos": photos,
            "stages": [s.value for s in PlantStage],
            "statuses": [s.value for s in PlantStatus],
        },
    )


@router.post("/plant/{plant_id}/update")
def update_plant(
    plant_id: int,
    name: str = Form(...),
    strain_name: str = Form(...),
    sprout_date: str = Form(...),
    current_stage: str = Form(...),
    pot_size: str = Form(...),
    substrate_type: str = Form(...),
    nutrient_line: str = Form(...),
    phenotype_code: str = Form(""),
    nfc_tag_id: str = Form(""),
    care_maintenance_rating: int | None = Form(None),
    overall_pheno_rating: int | None = Form(None),
    notes: str = Form(""),
    status: str = Form("Active"),
    db: Session = Depends(get_db),
):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    if nfc_tag_id:
        existing = db.query(Plant).filter(Plant.nfc_tag_id == nfc_tag_id, Plant.id != plant_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="NFC tag ID already assigned")

    previous_stage = plant.current_stage
    previous_pot = plant.pot_size

    plant.name = name.strip()
    plant.strain_name = strain_name.strip()
    plant.sprout_date = datetime.strptime(sprout_date, "%Y-%m-%d").date()
    plant.current_stage = PlantStage(current_stage)
    plant.pot_size = pot_size.strip()
    plant.substrate_type = substrate_type.strip()
    plant.nutrient_line = nutrient_line.strip()
    plant.phenotype_code = phenotype_code.strip() or None
    plant.nfc_tag_id = nfc_tag_id.strip() or None
    plant.care_maintenance_rating = care_maintenance_rating
    plant.overall_pheno_rating = overall_pheno_rating
    plant.notes = notes.strip() or None
    plant.status = PlantStatus(status)
    plant.updated_at = datetime.utcnow()

    if previous_stage != plant.current_stage or previous_pot != plant.pot_size:
        details = []
        if previous_stage != plant.current_stage:
            details.append(f"Stage: {previous_stage.value} → {plant.current_stage.value}")
        if previous_pot != plant.pot_size:
            details.append(f"Pot: {previous_pot} → {plant.pot_size}")
        db.add(
            PlantLog(
                plant_id=plant.id,
                log_type=PlantLogType.STAGE_CHANGE,
                notes=" | ".join(details),
                timestamp=datetime.utcnow(),
            )
        )

    db.commit()
    return RedirectResponse(url=f"/plant/{plant.id}", status_code=303)
