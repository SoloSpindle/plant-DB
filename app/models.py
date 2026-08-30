from __future__ import annotations

from datetime import date, datetime, time
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SQLEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    UniqueConstraint,
    text,
)
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


class AreaExposure(str, Enum):
    INDOOR = "Indoor"
    OUTDOOR = "Outdoor"


class GrowAreaType(str, Enum):
    TENT = "Tent"
    SHELF = "Shelf"
    BED = "Bed"
    POT = "Pot"
    BAG = "Bag"
    GREENHOUSE = "Greenhouse"
    ROOM = "Room"
    OTHER = "Other"


class LightScheduleMode(str, Enum):
    FIXED = "Fixed"
    SUNLIGHT = "Sunlight"
    HYBRID = "Hybrid"


class AreaEquipmentType(str, Enum):
    LIGHT = "Light"
    FAN = "Fan"
    DEHUMIDIFIER = "Dehumidifier"
    HUMIDIFIER = "Humidifier"
    HEATER = "Heater"
    COOLER = "Cooler"
    CONTROLLER = "Controller"
    SENSOR = "Sensor"
    IRRIGATION = "Irrigation"
    OTHER = "Other"


class AreaReadingSource(str, Enum):
    MANUAL = "Manual"
    IMPORT = "Import"
    SENSOR = "Sensor"


class AreaMetric(str, Enum):
    AIR_TEMP = "air_temp"
    AIR_HUMIDITY = "air_humidity"
    VPD = "vpd"
    SOIL_TEMP = "soil_temp"
    WATER_CONTENT_PCT = "water_content_pct"
    SOIL_EC = "soil_ec"
    CO2 = "co2"
    PPFD = "ppfd"


class AreaAlertStatus(str, Enum):
    OPEN = "Open"
    ACKNOWLEDGED = "Acknowledged"
    RESOLVED = "Resolved"
    DISMISSED = "Dismissed"


class AreaAlertSeverity(str, Enum):
    INFO = "Info"
    WARNING = "Warning"
    CRITICAL = "Critical"


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
    area_assignments: Mapped[list["PlantAreaAssignment"]] = relationship(
        "PlantAreaAssignment",
        back_populates="plant",
        cascade="all, delete-orphan",
    )
    nutrient_applications: Mapped[list["NutrientApplication"]] = relationship(
        "NutrientApplication",
        back_populates="plant",
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


class GrowArea(Base):
    __tablename__ = "grow_areas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    exposure: Mapped[AreaExposure] = mapped_column(
        SQLEnum(AreaExposure), nullable=False, default=AreaExposure.INDOOR
    )
    area_type: Mapped[GrowAreaType] = mapped_column(
        SQLEnum(GrowAreaType), nullable=False, default=GrowAreaType.OTHER
    )
    location_label: Mapped[str | None] = mapped_column(String(255))
    length_inches: Mapped[float | None] = mapped_column(Float)
    width_inches: Mapped[float | None] = mapped_column(Float)
    height_inches: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    assignments: Mapped[list["PlantAreaAssignment"]] = relationship(
        "PlantAreaAssignment",
        back_populates="area",
        cascade="all, delete-orphan",
    )
    light_schedules: Mapped[list["AreaLightSchedule"]] = relationship(
        "AreaLightSchedule",
        back_populates="area",
        cascade="all, delete-orphan",
    )
    env_targets: Mapped[list["AreaEnvTarget"]] = relationship(
        "AreaEnvTarget",
        back_populates="area",
        cascade="all, delete-orphan",
    )
    readings: Mapped[list["AreaReading"]] = relationship(
        "AreaReading",
        back_populates="area",
        cascade="all, delete-orphan",
    )
    equipment: Mapped[list["AreaEquipment"]] = relationship(
        "AreaEquipment",
        back_populates="area",
        cascade="all, delete-orphan",
    )
    nutrient_applications: Mapped[list["NutrientApplication"]] = relationship(
        "NutrientApplication",
        back_populates="area",
        cascade="all, delete-orphan",
    )
    alerts: Mapped[list["AreaAlert"]] = relationship(
        "AreaAlert",
        back_populates="area",
        cascade="all, delete-orphan",
    )


class PlantAreaAssignment(Base):
    __tablename__ = "plant_area_assignments"
    __table_args__ = (
        Index("ix_plant_area_assignments_plant_time", "plant_id", "start_at", "end_at"),
        Index("ix_plant_area_assignments_area_time", "area_id", "start_at", "end_at"),
        Index(
            "ix_plant_area_assignments_one_active_per_plant",
            "plant_id",
            unique=True,
            sqlite_where=text("end_at IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    plant_id: Mapped[int] = mapped_column(ForeignKey("plants.id"), nullable=False, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("grow_areas.id"), nullable=False, index=True)
    start_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    end_at: Mapped[datetime | None] = mapped_column(DateTime)
    move_reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    plant: Mapped[Plant] = relationship("Plant", back_populates="area_assignments")
    area: Mapped[GrowArea] = relationship("GrowArea", back_populates="assignments")


class AreaLightSchedule(Base):
    __tablename__ = "area_light_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("grow_areas.id"), nullable=False, index=True)
    mode: Mapped[LightScheduleMode] = mapped_column(
        SQLEnum(LightScheduleMode), nullable=False, default=LightScheduleMode.FIXED
    )
    lights_on_time: Mapped[time | None] = mapped_column(Time)
    lights_off_time: Mapped[time | None] = mapped_column(Time)
    light_hours: Mapped[float | None] = mapped_column(Float)
    dark_hours: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    area: Mapped[GrowArea] = relationship("GrowArea", back_populates="light_schedules")


class AreaEnvTarget(Base):
    __tablename__ = "area_env_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("grow_areas.id"), nullable=False, index=True)
    air_temp_min: Mapped[float | None] = mapped_column(Float)
    air_temp_max: Mapped[float | None] = mapped_column(Float)
    air_humidity_min: Mapped[float | None] = mapped_column(Float)
    air_humidity_max: Mapped[float | None] = mapped_column(Float)
    vpd_min: Mapped[float | None] = mapped_column(Float)
    vpd_max: Mapped[float | None] = mapped_column(Float)
    soil_temp_min: Mapped[float | None] = mapped_column(Float)
    soil_temp_max: Mapped[float | None] = mapped_column(Float)
    water_content_pct_min: Mapped[float | None] = mapped_column(Float)
    water_content_pct_max: Mapped[float | None] = mapped_column(Float)
    soil_ec_min: Mapped[float | None] = mapped_column(Float)
    soil_ec_max: Mapped[float | None] = mapped_column(Float)
    co2_min: Mapped[float | None] = mapped_column(Float)
    co2_max: Mapped[float | None] = mapped_column(Float)
    ppfd_min: Mapped[float | None] = mapped_column(Float)
    ppfd_max: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    area: Mapped[GrowArea] = relationship("GrowArea", back_populates="env_targets")


class AreaReading(Base):
    __tablename__ = "area_readings"
    __table_args__ = (Index("ix_area_readings_area_recorded_at", "area_id", "recorded_at"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("grow_areas.id"), nullable=False, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    source: Mapped[AreaReadingSource] = mapped_column(
        SQLEnum(AreaReadingSource), nullable=False, default=AreaReadingSource.MANUAL
    )
    air_temp: Mapped[float | None] = mapped_column(Float)
    air_humidity: Mapped[float | None] = mapped_column(Float)
    vpd: Mapped[float | None] = mapped_column(Float)
    soil_temp: Mapped[float | None] = mapped_column(Float)
    water_content_pct: Mapped[float | None] = mapped_column(Float)
    soil_ec: Mapped[float | None] = mapped_column(Float)
    co2: Mapped[float | None] = mapped_column(Float)
    ppfd: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    area: Mapped[GrowArea] = relationship("GrowArea", back_populates="readings")
    alerts: Mapped[list["AreaAlert"]] = relationship("AreaAlert", back_populates="reading")


class AreaEquipment(Base):
    __tablename__ = "area_equipment"
    __table_args__ = (Index("ix_area_equipment_area_type", "area_id", "equipment_type"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("grow_areas.id"), nullable=False, index=True)
    equipment_type: Mapped[AreaEquipmentType] = mapped_column(SQLEnum(AreaEquipmentType), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str | None] = mapped_column(String(255))
    serial_number: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    area: Mapped[GrowArea] = relationship("GrowArea", back_populates="equipment")


class FertilizerProduct(Base):
    __tablename__ = "fertilizer_products"
    __table_args__ = (UniqueConstraint("brand", "product_name", name="uq_fertilizer_product_brand_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    brand: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    formulation: Mapped[str | None] = mapped_column(String(255))
    npk_ratio: Mapped[str | None] = mapped_column(String(255))
    notes: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    nutrient_applications: Mapped[list["NutrientApplication"]] = relationship(
        "NutrientApplication",
        back_populates="product",
    )


class NutrientApplication(Base):
    __tablename__ = "nutrient_applications"
    __table_args__ = (
        Index("ix_nutrient_applications_area_applied_at", "area_id", "applied_at"),
        Index("ix_nutrient_applications_plant_applied_at", "plant_id", "applied_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("grow_areas.id"), nullable=False, index=True)
    plant_id: Mapped[int | None] = mapped_column(ForeignKey("plants.id"), index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("fertilizer_products.id"), nullable=False, index=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    amount_value: Mapped[float | None] = mapped_column(Float)
    amount_unit: Mapped[str | None] = mapped_column(String(50))
    dilution_ratio: Mapped[str | None] = mapped_column(String(100))
    solution_ec: Mapped[float | None] = mapped_column(Float)
    solution_ph: Mapped[float | None] = mapped_column(Float)
    runoff_ec: Mapped[float | None] = mapped_column(Float)
    runoff_ph: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    area: Mapped[GrowArea] = relationship("GrowArea", back_populates="nutrient_applications")
    plant: Mapped[Plant | None] = relationship("Plant", back_populates="nutrient_applications")
    product: Mapped[FertilizerProduct] = relationship("FertilizerProduct", back_populates="nutrient_applications")


class AreaAlert(Base):
    __tablename__ = "area_alerts"
    __table_args__ = (
        Index("ix_area_alerts_status_created_at", "status", "created_at"),
        Index("ix_area_alerts_area_status_created_at", "area_id", "status", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    area_id: Mapped[int] = mapped_column(ForeignKey("grow_areas.id"), nullable=False, index=True)
    reading_id: Mapped[int | None] = mapped_column(ForeignKey("area_readings.id"), index=True)
    metric: Mapped[AreaMetric] = mapped_column(SQLEnum(AreaMetric), nullable=False)
    observed_value: Mapped[float | None] = mapped_column(Float)
    min_threshold: Mapped[float | None] = mapped_column(Float)
    max_threshold: Mapped[float | None] = mapped_column(Float)
    status: Mapped[AreaAlertStatus] = mapped_column(
        SQLEnum(AreaAlertStatus), nullable=False, default=AreaAlertStatus.OPEN
    )
    severity: Mapped[AreaAlertSeverity] = mapped_column(
        SQLEnum(AreaAlertSeverity), nullable=False, default=AreaAlertSeverity.WARNING
    )
    message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime)

    area: Mapped[GrowArea] = relationship("GrowArea", back_populates="alerts")
    reading: Mapped[AreaReading | None] = relationship("AreaReading", back_populates="alerts")
