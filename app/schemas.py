from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel

from app.models import PlantLogType, PlantStage, PlantStatus


class PlantBase(BaseModel):
    nfc_tag_id: str | None = None
    name: str
    strain_name: str
    phenotype_code: str | None = None
    sprout_date: date
    current_stage: PlantStage
    pot_size: str
    substrate_type: str
    nutrient_line: str
    care_maintenance_rating: int | None = None
    overall_pheno_rating: int | None = None
    notes: str | None = None
    status: PlantStatus = PlantStatus.ACTIVE


class PlantRead(PlantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlantLogRead(BaseModel):
    id: int
    plant_id: int
    timestamp: datetime
    log_type: PlantLogType
    input_ph: float | None = None
    input_ec: float | None = None
    runoff_ph: float | None = None
    runoff_ec: float | None = None
    training_type: str | None = None
    notes: str | None = None
    photo_url: str | None = None

    class Config:
        from_attributes = True


class PlantPhotoRead(BaseModel):
    id: int
    plant_id: int
    timestamp: datetime
    file_path: str
    caption: str | None = None

    class Config:
        from_attributes = True
