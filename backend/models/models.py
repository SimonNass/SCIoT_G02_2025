from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Float, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from backend.extensions import db
import uuid
import enum

class Floor(db.Model):
    __tablename__ = 'floors'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    floor_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    floor_name: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationship: One floor has many rooms
    rooms: Mapped[List["Room"]] = relationship(
        back_populates="floor", 
        cascade="all, delete-orphan",
        order_by="Room.room_number"
    )
    
    def __repr__(self) -> str:
        return f"Floor(id={self.id!r}, floor_number={self.floor_number!r}, floor_name={self.floor_name!r})"


class Room(db.Model):
    __tablename__ = 'rooms'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    room_number: Mapped[str] = mapped_column(String(20), nullable=False, unique=True) 
    room_type: Mapped[str] = mapped_column(String(50), nullable=False) 
    description: Mapped[Optional[str]] = mapped_column(Text)
    capacity: Mapped[int] = mapped_column(Integer, default=2)
    is_occupied: Mapped[bool] = mapped_column(Boolean, default=False)
    last_cleaned: Mapped[Optional[datetime]] = mapped_column(DateTime)
    is_cleaned: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)
    
    rfid_access_id: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Foreign key to Floor
    floor_id: Mapped[str] = mapped_column(ForeignKey("floors.id"), nullable=False)
    
    # Relationships
    floor: Mapped["Floor"] = relationship(back_populates="rooms")
    devices: Mapped[List["Device"]] = relationship(
        back_populates="room", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"Room(id={self.id!r}, room_number={self.room_number!r}, room_type={self.room_type!r})"


class Device(db.Model):
    __tablename__ = 'devices'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'sensor' or 'actuator'
    type_name: Mapped[str] = mapped_column(String(100), nullable=False)  # 'temperature', 'humidity', etc.
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen: Mapped[Optional[datetime]] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Device specifications
    connector: Mapped[Optional[str]] = mapped_column(String(50))
    connector_type: Mapped[Optional[str]] = mapped_column(String(50))
    min_value: Mapped[Optional[float]] = mapped_column(Float)
    max_value: Mapped[Optional[float]] = mapped_column(Float)
    datatype: Mapped[Optional[str]] = mapped_column(String(50))
    unit: Mapped[Optional[str]] = mapped_column(String(20))
    last_value: Mapped[Optional[str]] = mapped_column(Text)

    # Sensor-specific fields
    read_interval: Mapped[Optional[int]] = mapped_column(Integer)
    notify_interval: Mapped[Optional[str]] = mapped_column(String(50))
    notify_change_precision: Mapped[Optional[float]] = mapped_column(Float)
    last_value_simplified: Mapped[Optional[int]] = mapped_column(Integer)
    
    # Actuator-specific fields
    initial_value: Mapped[Optional[str]] = mapped_column(String(100))
    off_value: Mapped[Optional[str]] = mapped_column(String(100))
    is_off: Mapped[Optional[bool]] = mapped_column(Boolean, default=None)
    
    # Foreign key to Room
    room_id: Mapped[str] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    
    # Foreign key to TypeNameConfig
    type_name_config_id: Mapped[Optional[str]] = mapped_column(ForeignKey("type_name_configs.id"))
    
    # Relationship
    room: Mapped["Room"] = relationship(back_populates="devices")
    sensor_data: Mapped[List["SensorData"]] = relationship(
        back_populates="device", 
        cascade="all, delete-orphan",
        order_by="SensorData.timestamp.desc()"
    )
    device_type_config: Mapped[Optional["TypeNameConfig"]] = relationship( 
        back_populates="devices"
    )
    
    # Sensor-Actuator mapping relationships
    # When this device is an actuator that influences sensors
    actuator_mappings: Mapped[List["SensorActuatorMapping"]] = relationship(
        back_populates="actuator_device",
        foreign_keys="SensorActuatorMapping.actuator_device_id",
        cascade="all, delete-orphan"
    )
    
    # When this device is a sensor influenced by actuators
    sensor_mappings: Mapped[List["SensorActuatorMapping"]] = relationship(
        back_populates="sensor_device",
        foreign_keys="SensorActuatorMapping.sensor_device_id",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"Device(id={self.id!r}, device_id={self.device_id!r}, name={self.name!r}, type={self.device_type!r})"

class SensorData(db.Model):
    """Store time-series data from sensors/actuators"""
    __tablename__ = 'sensor_data'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), nullable=False)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    simplified_value: Mapped[int] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    device: Mapped["Device"] = relationship(back_populates="sensor_data")
    
    def __repr__(self) -> str:
        return f"SensorData(id={self.id!r}, device_id={self.device_id!r}, value={self.value!r}, timestamp={self.timestamp!r})"

class SensorActuatorMapping(db.Model):
    """Store mappings between sensors and actuators with influence parameters"""
    __tablename__ = 'sensor_actuator_mappings'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys to devices (nullable to handle creation order)
    actuator_device_id: Mapped[Optional[str]] = mapped_column(ForeignKey("devices.id"), nullable=True)
    sensor_device_id: Mapped[Optional[str]] = mapped_column(ForeignKey("devices.id"), nullable=True)
    
    # UUIDs from the mapping payload (used for initial creation and later linking)
    uuid_actuator: Mapped[str] = mapped_column(String(100), nullable=False)
    uuid_sensor: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Mapping parameters
    impact_factor: Mapped[float] = mapped_column(Float, nullable=False)
    actuator_can_increases_sensor: Mapped[bool] = mapped_column(Boolean, nullable=False)
    actuator_can_decreases_sensor: Mapped[bool] = mapped_column(Boolean, nullable=False)
    only_physical: Mapped[bool] = mapped_column(Boolean, default=False)
    active_influences: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=datetime.utcnow)
    
    # Relationships
    actuator_device: Mapped[Optional["Device"]] = relationship(
        back_populates="actuator_mappings",
        foreign_keys=[actuator_device_id]
    )
    sensor_device: Mapped[Optional["Device"]] = relationship(
        back_populates="sensor_mappings",
        foreign_keys=[sensor_device_id]
    )
    
    # Unique constraint to prevent duplicate mappings
    __table_args__ = (
        db.UniqueConstraint('uuid_actuator', 'uuid_sensor', name='unique_actuator_sensor_mapping'),
    )
    
    def __repr__(self) -> str:
        return f"SensorActuatorMapping(actuator={self.uuid_actuator!r}, sensor={self.uuid_sensor!r}, impact={self.impact_factor!r})"
    
class TypeNameConfig(db.Model):
    """Stores lower-mid and upper-mid limits for each device type to enable dynamic determination of simiplified values"""
    __tablename__ = 'type_name_configs'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'sensor', 'actuator'
    type_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)  # e.g., 'temperature', 'humidity'
    lower_mid_limit: Mapped[float] = mapped_column(Float)
    upper_mid_limit: Mapped[float] = mapped_column(Float)
    min_value: Mapped[float] = mapped_column(Float)
    max_value: Mapped[float] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(20))

    devices: Mapped[List["Device"]] = relationship(back_populates="device_type_config")

    def __repr__(self) -> str:
        return f"TypeNameConfig(id={self.id!r}, device_type={self.device_type!r}, type_name={self.type_name!r}, lower_mid_limit={self.lower_mid_limit!r}, lower_mid_limit={self.upper_mid_limit!r})"

class PlanScope(enum.Enum):
    BUILDING = "building"
    FLOOR = "floor"
    ROOM = "room"

class PDDLPlan(db.Model):
    """Store PDDL plans with their metadata and scope"""
    __tablename__ = 'plans'

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scope: Mapped[PlanScope] = mapped_column(Enum(PlanScope), nullable=False)
    target_floor_id: Mapped[Optional[str]] = mapped_column(ForeignKey("floors.id"))
    target_room_id: Mapped[Optional[str]] = mapped_column(ForeignKey("rooms.id"))

    total_cost: Mapped[Optional[float]] = mapped_column(Float)
    planning_time: Mapped[Optional[float]] = mapped_column(Float)
    planner_used: Mapped[str] = mapped_column(String(100))
    raw_plan: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    target_floor: Mapped[Optional["Floor"]] = relationship("Floor", foreign_keys=[target_floor_id])
    target_room: Mapped[Optional["Room"]] = relationship("Room", foreign_keys=[target_room_id])
    steps: Mapped[List["PlanStep"]] = relationship(
        back_populates="plan", 
        cascade="all, delete-orphan",
        order_by="PlanStep.step_order"
    )

    def __repr__(self) -> str:
        return f"Plan(id={self.id!r}, scope={self.scope!r}, planner_used={self.planner_used!r}, raw_plan={self.raw_plan!r})"

class PlanStep(db.Model):
    """Store individual steps of a PDDL plan"""
    __tablename__ = 'plan_steps'
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id"), nullable=False)

    # Step details
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    action_name: Mapped[str] = mapped_column(String(200), nullable=False)
    raw_step: Mapped[str] = mapped_column(Text, nullable=False)  # Original step string from planner

    target_device_ids: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Relationships
    plan: Mapped["PDDLPlan"] = relationship(back_populates="steps")