from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from sqlalchemy import Date, DateTime, Enum as SQLEnum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class PlantStage(str, Enum):
    SEEDLING = "Seedling"
    VEGETATIVE = "Vegetative"
    FLOWERING = "Flowering"
    HARVESTED = "Harvested"
    ARCHIVED = "Archived"


class PlantStatus(str, Enum):
    ACTIVE = "Active"
    ARCHIVED = "Archived"


class PlantLogType(str, Enum):
    WATERING = "Watering"
    FEEDING = "Feeding"
    PRUNING = "Pruning"
    TRAINING = "Training"
    STAGE_CHANGE = "Stage Change"
    GENERAL_NOTE = "General Note"


class Plant(Base):
    __tablename__ = "plants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nfc_tag_id: Mapped[str | None] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    strain_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phenotype_code: Mapped[str | None] = mapped_column(String(255))
    sprout_date: Mapped[date] = mapped_column(Date, nullable=False)
    current_stage: Mapped[PlantStage] = mapped_column(
        SQLEnum(PlantStage), default=PlantStage.SEEDLING, nullable=False
    )
    pot_size: Mapped[str] = mapped_column(String(255), nullable=False)
    substrate_type: Mapped[str] = mapped_column(String(255), nullable=False)
    nutrient_line: Mapped[str] = mapped_column(String(255), nullable=False)
    care_maintenance_rating: Mapped[int | None] = mapped_column(Integer)
    overall_pheno_rating: Mapped[int | None] = mapped_column(Integer)
    notes: Mapped[str | None] = mapped_column(Text)
    status: Mapped[PlantStatus] = mapped_column(SQLEnum(PlantStatus), default=PlantStatus.ACTIVE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    logs: Mapped[list["PlantLog"]] = relationship(
        "PlantLog", back_populates="plant", cascade="all, delete-orphan"
    )
    photos: Mapped[list["PlantPhoto"]] = relationship(
        "PlantPhoto", back_populates="plant", cascade="all, delete-orphan"
    )


class PlantLog(Base):
    __tablename__ = "plant_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    log_type: Mapped[PlantLogType] = mapped_column(SQLEnum(PlantLogType), nullable=False)
    input_ph: Mapped[float | None] = mapped_column(Float)
    input_ec: Mapped[float | None] = mapped_column(Float)
    runoff_ph: Mapped[float | None] = mapped_column(Float)
    runoff_ec: Mapped[float | None] = mapped_column(Float)
    training_type: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    photo_url: Mapped[str | None] = mapped_column(String(500))

    plant: Mapped[Plant] = relationship("Plant", back_populates="logs")


class PlantPhoto(Base):
    __tablename__ = "plant_photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str | None] = mapped_column(String(255))

    plant: Mapped[Plant] = relationship("Plant", back_populates="photos")
