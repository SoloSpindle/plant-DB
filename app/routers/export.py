from __future__ import annotations

import csv
import io
import zipfile

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Plant, PlantLog

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/csv")
def export_csv(db: Session = Depends(get_db)):
    plants_rows = db.query(Plant).order_by(Plant.id.asc()).all()
    logs_rows = db.query(PlantLog).order_by(PlantLog.id.asc()).all()

    plants_csv = io.StringIO()
    plant_writer = csv.writer(plants_csv)
    plant_writer.writerow(
        [
            "id",
            "nfc_tag_id",
            "name",
            "strain_name",
            "phenotype_code",
            "sprout_date",
            "current_stage",
            "pot_size",
            "substrate_type",
            "nutrient_line",
            "care_maintenance_rating",
            "overall_pheno_rating",
            "notes",
            "status",
            "created_at",
            "updated_at",
        ]
    )
    for plant in plants_rows:
        plant_writer.writerow(
            [
                plant.id,
                plant.nfc_tag_id,
                plant.name,
                plant.strain_name,
                plant.phenotype_code,
                plant.sprout_date.isoformat(),
                plant.current_stage.value,
                plant.pot_size,
                plant.substrate_type,
                plant.nutrient_line,
                plant.care_maintenance_rating,
                plant.overall_pheno_rating,
                plant.notes,
                plant.status.value,
                plant.created_at.isoformat(),
                plant.updated_at.isoformat(),
            ]
        )

    logs_csv = io.StringIO()
    log_writer = csv.writer(logs_csv)
    log_writer.writerow(
        [
            "id",
            "plant_id",
            "timestamp",
            "log_type",
            "input_ph",
            "input_ec",
            "runoff_ph",
            "runoff_ec",
            "training_type",
            "notes",
            "photo_url",
        ]
    )
    for log in logs_rows:
        log_writer.writerow(
            [
                log.id,
                log.plant_id,
                log.timestamp.isoformat(),
                log.log_type.value,
                log.input_ph,
                log.input_ec,
                log.runoff_ph,
                log.runoff_ec,
                log.training_type,
                log.notes,
                log.photo_url,
            ]
        )

    output = io.BytesIO()
    with zipfile.ZipFile(output, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("plants_export.csv", plants_csv.getvalue())
        zf.writestr("logs_export.csv", logs_csv.getvalue())
    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=plant_tracker_exports.zip"},
    )
