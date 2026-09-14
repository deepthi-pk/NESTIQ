from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__='users'; id=Column(Integer, primary_key=True); name=Column(String, default='Alex')
class Room(Base):
    __tablename__='rooms'; id=Column(Integer, primary_key=True); name=Column(String, unique=True); kind=Column(String); devices=relationship('Device', back_populates='room')
class Device(Base):
    __tablename__='devices'; id=Column(String, primary_key=True); name=Column(String); type=Column(String); room_id=Column(Integer, ForeignKey('rooms.id')); power=Column(Boolean, default=False); brightness=Column(Integer, nullable=True); level=Column(String, nullable=True); last_changed=Column(DateTime, server_default=func.now()); room=relationship('Room', back_populates='devices')
class DeviceStateHistory(Base):
    __tablename__='device_state_history'; id=Column(Integer, primary_key=True); device_id=Column(String); state=Column(JSON); timestamp=Column(DateTime, server_default=func.now())
class HomeObservation(Base):
    __tablename__='home_observations'; id=Column(Integer, primary_key=True); timestamp=Column(DateTime, server_default=func.now()); room=Column(String); environment_type=Column(String); detected_objects=Column(JSON); image_reference=Column(String, nullable=True); lighting_condition=Column(String); notes=Column(String); confidence=Column(Float)
class ObjectObservation(Base):
    __tablename__='object_observations'; id=Column(Integer, primary_key=True); object_name=Column(String, index=True); location=Column(String); room=Column(String); observed_at=Column(DateTime, server_default=func.now()); confidence=Column(Float); observation_id=Column(Integer, ForeignKey('home_observations.id'))
class RoutineEvent(Base):
    __tablename__='routine_events'; id=Column(Integer, primary_key=True); event_type=Column(String); room=Column(String); details=Column(String); timestamp=Column(DateTime, server_default=func.now())
class Automation(Base):
    __tablename__='automations'; id=Column(Integer, primary_key=True); name=Column(String); trigger=Column(String); actions=Column(JSON); approved=Column(Boolean, default=False); explanation=Column(String)
class TimelineEvent(Base):
    __tablename__='timeline_events'; id=Column(Integer, primary_key=True); timestamp=Column(DateTime, server_default=func.now()); title=Column(String); description=Column(String); type=Column(String, default='activity')
class AIInteraction(Base):
    __tablename__='ai_interactions'; id=Column(Integer, primary_key=True); prompt=Column(String); response=Column(JSON); timestamp=Column(DateTime, server_default=func.now())
