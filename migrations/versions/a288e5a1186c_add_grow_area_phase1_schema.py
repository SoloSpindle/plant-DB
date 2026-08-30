"""add grow area phase1 schema

Revision ID: a288e5a1186c
Revises: 
Create Date: 2026-08-30 18:52:00.648381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a288e5a1186c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "grow_areas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("exposure", sa.Enum("INDOOR", "OUTDOOR", name="areaexposure"), nullable=False),
        sa.Column(
            "area_type",
            sa.Enum(
                "TENT",
                "SHELF",
                "BED",
                "POT",
                "BAG",
                "GREENHOUSE",
                "ROOM",
                "OTHER",
                name="growareatype",
            ),
            nullable=False,
        ),
        sa.Column("location_label", sa.String(length=255), nullable=True),
        sa.Column("length_inches", sa.Float(), nullable=True),
        sa.Column("width_inches", sa.Float(), nullable=True),
        sa.Column("height_inches", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_grow_areas_id"), "grow_areas", ["id"], unique=False)
    op.create_index(op.f("ix_grow_areas_name"), "grow_areas", ["name"], unique=True)

    op.create_table(
        "area_env_targets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("air_temp_min", sa.Float(), nullable=True),
        sa.Column("air_temp_max", sa.Float(), nullable=True),
        sa.Column("air_humidity_min", sa.Float(), nullable=True),
        sa.Column("air_humidity_max", sa.Float(), nullable=True),
        sa.Column("vpd_min", sa.Float(), nullable=True),
        sa.Column("vpd_max", sa.Float(), nullable=True),
        sa.Column("soil_temp_min", sa.Float(), nullable=True),
        sa.Column("soil_temp_max", sa.Float(), nullable=True),
        sa.Column("water_content_pct_min", sa.Float(), nullable=True),
        sa.Column("water_content_pct_max", sa.Float(), nullable=True),
        sa.Column("soil_ec_min", sa.Float(), nullable=True),
        sa.Column("soil_ec_max", sa.Float(), nullable=True),
        sa.Column("co2_min", sa.Float(), nullable=True),
        sa.Column("co2_max", sa.Float(), nullable=True),
        sa.Column("ppfd_min", sa.Float(), nullable=True),
        sa.Column("ppfd_max", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["grow_areas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_area_env_targets_area_id"), "area_env_targets", ["area_id"], unique=False)
    op.create_index(op.f("ix_area_env_targets_id"), "area_env_targets", ["id"], unique=False)

    op.create_table(
        "area_equipment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column(
            "equipment_type",
            sa.Enum(
                "LIGHT",
                "FAN",
                "DEHUMIDIFIER",
                "HUMIDIFIER",
                "HEATER",
                "COOLER",
                "CONTROLLER",
                "SENSOR",
                "IRRIGATION",
                "OTHER",
                name="areaequipmenttype",
            ),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("model", sa.String(length=255), nullable=True),
        sa.Column("serial_number", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["grow_areas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_area_equipment_area_type", "area_equipment", ["area_id", "equipment_type"], unique=False)
    op.create_index(op.f("ix_area_equipment_area_id"), "area_equipment", ["area_id"], unique=False)
    op.create_index(op.f("ix_area_equipment_id"), "area_equipment", ["id"], unique=False)

    op.create_table(
        "area_light_schedules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("mode", sa.Enum("FIXED", "SUNLIGHT", "HYBRID", name="lightschedulemode"), nullable=False),
        sa.Column("lights_on_time", sa.Time(), nullable=True),
        sa.Column("lights_off_time", sa.Time(), nullable=True),
        sa.Column("light_hours", sa.Float(), nullable=True),
        sa.Column("dark_hours", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["grow_areas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_area_light_schedules_area_id"), "area_light_schedules", ["area_id"], unique=False)
    op.create_index(op.f("ix_area_light_schedules_id"), "area_light_schedules", ["id"], unique=False)

    op.create_table(
        "area_readings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(), nullable=False),
        sa.Column("source", sa.Enum("MANUAL", "IMPORT", "SENSOR", name="areareadingsource"), nullable=False),
        sa.Column("air_temp", sa.Float(), nullable=True),
        sa.Column("air_humidity", sa.Float(), nullable=True),
        sa.Column("vpd", sa.Float(), nullable=True),
        sa.Column("soil_temp", sa.Float(), nullable=True),
        sa.Column("water_content_pct", sa.Float(), nullable=True),
        sa.Column("soil_ec", sa.Float(), nullable=True),
        sa.Column("co2", sa.Float(), nullable=True),
        sa.Column("ppfd", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["grow_areas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_area_readings_area_recorded_at", "area_readings", ["area_id", "recorded_at"], unique=False)
    op.create_index(op.f("ix_area_readings_area_id"), "area_readings", ["area_id"], unique=False)
    op.create_index(op.f("ix_area_readings_id"), "area_readings", ["id"], unique=False)

    op.create_table(
        "fertilizer_products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("brand", sa.String(length=255), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("formulation", sa.String(length=255), nullable=True),
        sa.Column("npk_ratio", sa.String(length=255), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("brand", "product_name", name="uq_fertilizer_product_brand_name"),
    )
    op.create_index(op.f("ix_fertilizer_products_brand"), "fertilizer_products", ["brand"], unique=False)
    op.create_index(op.f("ix_fertilizer_products_id"), "fertilizer_products", ["id"], unique=False)
    op.create_index(op.f("ix_fertilizer_products_product_name"), "fertilizer_products", ["product_name"], unique=False)

    op.create_table(
        "nutrient_applications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("applied_at", sa.DateTime(), nullable=False),
        sa.Column("amount_value", sa.Float(), nullable=True),
        sa.Column("amount_unit", sa.String(length=50), nullable=True),
        sa.Column("dilution_ratio", sa.String(length=100), nullable=True),
        sa.Column("solution_ec", sa.Float(), nullable=True),
        sa.Column("solution_ph", sa.Float(), nullable=True),
        sa.Column("runoff_ec", sa.Float(), nullable=True),
        sa.Column("runoff_ph", sa.Float(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["grow_areas.id"]),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
        sa.ForeignKeyConstraint(["product_id"], ["fertilizer_products.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_nutrient_applications_area_applied_at", "nutrient_applications", ["area_id", "applied_at"], unique=False)
    op.create_index(op.f("ix_nutrient_applications_area_id"), "nutrient_applications", ["area_id"], unique=False)
    op.create_index(op.f("ix_nutrient_applications_id"), "nutrient_applications", ["id"], unique=False)
    op.create_index(op.f("ix_nutrient_applications_plant_id"), "nutrient_applications", ["plant_id"], unique=False)
    op.create_index("ix_nutrient_applications_plant_applied_at", "nutrient_applications", ["plant_id", "applied_at"], unique=False)
    op.create_index(op.f("ix_nutrient_applications_product_id"), "nutrient_applications", ["product_id"], unique=False)

    op.create_table(
        "plant_area_assignments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plant_id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("start_at", sa.DateTime(), nullable=False),
        sa.Column("end_at", sa.DateTime(), nullable=True),
        sa.Column("move_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["area_id"], ["grow_areas.id"]),
        sa.ForeignKeyConstraint(["plant_id"], ["plants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_plant_area_assignments_area_id"), "plant_area_assignments", ["area_id"], unique=False)
    op.create_index("ix_plant_area_assignments_area_time", "plant_area_assignments", ["area_id", "start_at", "end_at"], unique=False)
    op.create_index(op.f("ix_plant_area_assignments_id"), "plant_area_assignments", ["id"], unique=False)
    op.create_index(
        "ix_plant_area_assignments_one_active_per_plant",
        "plant_area_assignments",
        ["plant_id"],
        unique=True,
        sqlite_where=sa.text("end_at IS NULL"),
    )
    op.create_index(op.f("ix_plant_area_assignments_plant_id"), "plant_area_assignments", ["plant_id"], unique=False)
    op.create_index("ix_plant_area_assignments_plant_time", "plant_area_assignments", ["plant_id", "start_at", "end_at"], unique=False)

    op.create_table(
        "area_alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("area_id", sa.Integer(), nullable=False),
        sa.Column("reading_id", sa.Integer(), nullable=True),
        sa.Column(
            "metric",
            sa.Enum(
                "AIR_TEMP",
                "AIR_HUMIDITY",
                "VPD",
                "SOIL_TEMP",
                "WATER_CONTENT_PCT",
                "SOIL_EC",
                "CO2",
                "PPFD",
                name="areametric",
            ),
            nullable=False,
        ),
        sa.Column("observed_value", sa.Float(), nullable=True),
        sa.Column("min_threshold", sa.Float(), nullable=True),
        sa.Column("max_threshold", sa.Float(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("OPEN", "ACKNOWLEDGED", "RESOLVED", "DISMISSED", name="areaalertstatus"),
            nullable=False,
        ),
        sa.Column("severity", sa.Enum("INFO", "WARNING", "CRITICAL", name="areaalertseverity"), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["area_id"], ["grow_areas.id"]),
        sa.ForeignKeyConstraint(["reading_id"], ["area_readings.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_area_alerts_area_id"), "area_alerts", ["area_id"], unique=False)
    op.create_index("ix_area_alerts_area_status_created_at", "area_alerts", ["area_id", "status", "created_at"], unique=False)
    op.create_index(op.f("ix_area_alerts_id"), "area_alerts", ["id"], unique=False)
    op.create_index(op.f("ix_area_alerts_reading_id"), "area_alerts", ["reading_id"], unique=False)
    op.create_index("ix_area_alerts_status_created_at", "area_alerts", ["status", "created_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_area_alerts_status_created_at", table_name="area_alerts")
    op.drop_index(op.f("ix_area_alerts_reading_id"), table_name="area_alerts")
    op.drop_index(op.f("ix_area_alerts_id"), table_name="area_alerts")
    op.drop_index("ix_area_alerts_area_status_created_at", table_name="area_alerts")
    op.drop_index(op.f("ix_area_alerts_area_id"), table_name="area_alerts")
    op.drop_table("area_alerts")

    op.drop_index("ix_plant_area_assignments_plant_time", table_name="plant_area_assignments")
    op.drop_index(op.f("ix_plant_area_assignments_plant_id"), table_name="plant_area_assignments")
    op.drop_index("ix_plant_area_assignments_one_active_per_plant", table_name="plant_area_assignments")
    op.drop_index(op.f("ix_plant_area_assignments_id"), table_name="plant_area_assignments")
    op.drop_index("ix_plant_area_assignments_area_time", table_name="plant_area_assignments")
    op.drop_index(op.f("ix_plant_area_assignments_area_id"), table_name="plant_area_assignments")
    op.drop_table("plant_area_assignments")

    op.drop_index(op.f("ix_nutrient_applications_product_id"), table_name="nutrient_applications")
    op.drop_index("ix_nutrient_applications_plant_applied_at", table_name="nutrient_applications")
    op.drop_index(op.f("ix_nutrient_applications_plant_id"), table_name="nutrient_applications")
    op.drop_index(op.f("ix_nutrient_applications_id"), table_name="nutrient_applications")
    op.drop_index(op.f("ix_nutrient_applications_area_id"), table_name="nutrient_applications")
    op.drop_index("ix_nutrient_applications_area_applied_at", table_name="nutrient_applications")
    op.drop_table("nutrient_applications")

    op.drop_index(op.f("ix_fertilizer_products_product_name"), table_name="fertilizer_products")
    op.drop_index(op.f("ix_fertilizer_products_id"), table_name="fertilizer_products")
    op.drop_index(op.f("ix_fertilizer_products_brand"), table_name="fertilizer_products")
    op.drop_table("fertilizer_products")

    op.drop_index(op.f("ix_area_readings_id"), table_name="area_readings")
    op.drop_index(op.f("ix_area_readings_area_id"), table_name="area_readings")
    op.drop_index("ix_area_readings_area_recorded_at", table_name="area_readings")
    op.drop_table("area_readings")

    op.drop_index(op.f("ix_area_light_schedules_id"), table_name="area_light_schedules")
    op.drop_index(op.f("ix_area_light_schedules_area_id"), table_name="area_light_schedules")
    op.drop_table("area_light_schedules")

    op.drop_index(op.f("ix_area_equipment_id"), table_name="area_equipment")
    op.drop_index(op.f("ix_area_equipment_area_id"), table_name="area_equipment")
    op.drop_index("ix_area_equipment_area_type", table_name="area_equipment")
    op.drop_table("area_equipment")

    op.drop_index(op.f("ix_area_env_targets_id"), table_name="area_env_targets")
    op.drop_index(op.f("ix_area_env_targets_area_id"), table_name="area_env_targets")
    op.drop_table("area_env_targets")

    op.drop_index(op.f("ix_grow_areas_name"), table_name="grow_areas")
    op.drop_index(op.f("ix_grow_areas_id"), table_name="grow_areas")
    op.drop_table("grow_areas")
