# from typing import Optional
from sqlalchemy import ForeignKey, create_engine, Text, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

# Fixed URL driver dialect to standard SQLite
DATABASE_URL = "sqlite:///inventory_tracker.db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

class Inventory(Base):
    __tablename__ = 'inventory'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()
    serial_no: Mapped[str] = mapped_column(unique=True)
    dept: Mapped[str] = mapped_column()
    make: Mapped[str] = mapped_column()
    
    logs: Mapped[list["MaintenanceHistory"]] = relationship(
        "MaintenanceHistory",
        back_populates="equipment",
        cascade="all, delete-orphan"
    )

class MaintenanceHistory(Base):
    __tablename__ = 'maintenance_history'
    
    log_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    equipment_id: Mapped[int] = mapped_column(ForeignKey('inventory.id', ondelete='CASCADE'))
    date_run: Mapped[str] = mapped_column()
    technician: Mapped[str] = mapped_column()
    action_taken: Mapped[str] = mapped_column(Text) 
    status: Mapped[str] = mapped_column()
    
    equipment: Mapped["Inventory"] = relationship("Inventory", back_populates="logs")


def initialize_database() -> None:
    """Builds physical database schemas seamlessly."""
    Base.metadata.create_all(bind=engine)


def get_equipment_with_log_counts_raw():
    """Aggregates all equipment with total log computations using a high-speed raw SQL JOIN."""
    with SessionLocal() as db:
        raw_query = text("""
            SELECT i.id, i.name, i.make, i.dept, COUNT(m.log_id) as total_logs
            FROM inventory i
            LEFT JOIN maintenance_history m ON i.id = m.equipment_id
            GROUP BY i.id
        """)
        return db.execute(raw_query).fetchall()

def get_logs_for_asset_raw(asset_id: int):
    """Fetches history records directly via indexed parametric identification."""
    with SessionLocal() as db:
        raw_query = text("""
            SELECT date_run, technician, action_taken, status 
            FROM maintenance_history 
            WHERE equipment_id = :asset_id
            ORDER BY date_run DESC
        """)
        return db.execute(raw_query, {"asset_id": asset_id}).fetchall()
    
def delete_equipment_by_id(asset_id: int) -> None:
    """Deletes an asset and cascades to drop all linked history logs instantly."""
    with SessionLocal() as db:
        try:
            # We use a raw SQL execution to bypass heavy ORM overhead
            db.execute(text("DELETE FROM inventory WHERE id = :id"), {"id": asset_id})
            db.commit()
        except Exception:
            db.rollback()
            raise