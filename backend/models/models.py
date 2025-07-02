from sqlalchemy import String, Text, Boolean, Integer, DateTime, ForeignKey, Float, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from backend.extensions import db
import uuid

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
    
    # Foreign key to Floor
    floor_id: Mapped[int] = mapped_column(ForeignKey("floors.id"), nullable=False)
    
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
    
    # Actuator-specific fields
    initial_value: Mapped[Optional[str]] = mapped_column(String(100))
    off_value: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Foreign key to Room
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    
    # Relationship
    room: Mapped["Room"] = relationship(back_populates="devices")
    sensor_data: Mapped[List["SensorData"]] = relationship(
        back_populates="device", 
        cascade="all, delete-orphan",
        order_by="SensorData.timestamp.desc()"
    )
    device_type_config: Mapped[Optional["TypeNameConfig"]] = relationship( 
        back_populates="devices", 
    )
    
    # Todo: Add PDDL info need to know which actuator can influence which sensor
    
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
    
class TypeNameConfig(db.Model):
    """Stores lower-mid and upper-mid limits for each device type to enable dynamic determination of simiplified values"""
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    device_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'sensor', 'actuator'
    type_name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)  # e.g., 'temperature', 'humidity'
    lower_mid_limit: Mapped[float] = mapped_column(Float)
    upper_mid_limit: Mapped[float] = mapped_column(Float)
    min_value: Mapped[float] = mapped_column(Float)
    max_value: Mapped[float] = mapped_column(Float)
    unit: Mapped[Optional[str]] = mapped_column(String(20))

    devices: Mapped[List["Device"]] = relationship(back_populates="device_type_config")
