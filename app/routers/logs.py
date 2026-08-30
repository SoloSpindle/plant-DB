from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.database import UPLOAD_DIR, get_db
from app.models import Plant, PlantLog, PlantLogType, PlantPhoto, PlantStage

router = APIRouter()


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    raw = value.strip()
    if raw == "":
        return None
    return float(raw)


@router.post("/plant/{plant_id}/logs/quick-water")
def quick_water(
    plant_id: int,
    input_ph: str = Form(""),
    input_ec: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if not db.query(Plant).filter(Plant.id == plant_id).first():
        raise HTTPException(status_code=404, detail="Plant not found")

    db.add(
        PlantLog(
            plant_id=plant_id,
            log_type=PlantLogType.WATERING,
            input_ph=_to_float(input_ph),
            input_ec=_to_float(input_ec),
            notes=notes.strip() or None,
            timestamp=datetime.utcnow(),
        )
    )
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/plant/{plant_id}/logs/quick-feed")
def quick_feed(
    plant_id: int,
    input_ph: str = Form(""),
    input_ec: str = Form(""),
    runoff_ph: str = Form(""),
    runoff_ec: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if not db.query(Plant).filter(Plant.id == plant_id).first():
        raise HTTPException(status_code=404, detail="Plant not found")

    db.add(
        PlantLog(
            plant_id=plant_id,
            log_type=PlantLogType.FEEDING,
            input_ph=_to_float(input_ph),
            input_ec=_to_float(input_ec),
            runoff_ph=_to_float(runoff_ph),
            runoff_ec=_to_float(runoff_ec),
            notes=notes.strip() or None,
            timestamp=datetime.utcnow(),
        )
    )
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/plant/{plant_id}/logs/quick-train")
def quick_train(
    plant_id: int,
    training_type: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if not db.query(Plant).filter(Plant.id == plant_id).first():
        raise HTTPException(status_code=404, detail="Plant not found")

    db.add(
        PlantLog(
            plant_id=plant_id,
            log_type=PlantLogType.TRAINING,
            training_type=training_type.strip() or None,
            notes=notes.strip() or None,
            timestamp=datetime.utcnow(),
        )
    )
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/plant/{plant_id}/logs/quick-photo")
async def quick_photo(
    plant_id: int,
    caption: str = Form(""),
    notes: str = Form(""),
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if not db.query(Plant).filter(Plant.id == plant_id).first():
        raise HTTPException(status_code=404, detail="Plant not found")

    suffix = Path(photo.filename or "upload.jpg").suffix.lower() or ".jpg"
    filename = f"{uuid4().hex}{suffix}"
    file_path = UPLOAD_DIR / filename
    data = await photo.read()
    file_path.write_bytes(data)

    relative_path = f"/static/uploads/{filename}"

    db.add(
        PlantPhoto(
            plant_id=plant_id,
            file_path=relative_path,
            caption=caption.strip() or None,
            timestamp=datetime.utcnow(),
        )
    )
    db.add(
        PlantLog(
            plant_id=plant_id,
            log_type=PlantLogType.GENERAL_NOTE,
            notes=notes.strip() or caption.strip() or "Photo captured",
            photo_url=relative_path,
            timestamp=datetime.utcnow(),
        )
    )
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@router.post("/plant/{plant_id}/logs/stage-pot-update")
def quick_stage_pot(
    plant_id: int,
    current_stage: str = Form(...),
    pot_size: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    old_stage = plant.current_stage
    old_pot = plant.pot_size
    plant.current_stage = PlantStage(current_stage)
    plant.pot_size = pot_size.strip()
    plant.updated_at = datetime.utcnow()

    parts = []
    if old_stage != plant.current_stage:
        parts.append(f"Stage: {old_stage.value} → {plant.current_stage.value}")
    if old_pot != plant.pot_size:
        parts.append(f"Pot: {old_pot} → {plant.pot_size}")
    if notes.strip():
        parts.append(notes.strip())

    db.add(
        PlantLog(
            plant_id=plant.id,
            log_type=PlantLogType.STAGE_CHANGE,
            notes=" | ".join(parts) if parts else "Stage/Pot updated",
            timestamp=datetime.utcnow(),
        )
    )
    db.commit()

    return RedirectResponse(url="/", status_code=303)
