from datetime import date
from typing import Optional
from sqlalchemy import ForeignKey, Column, Date, Table, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from etc.common import EquipmentStatus

from flask_login import UserMixin

from models import Base, session, login_manager


class Position(Base):
    __tablename__ = "position"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Employee(Base, UserMixin):
    __tablename__ = "employee"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]  # ФИО одним полем, чтобы не плодить в задании многословность
    position_id: Mapped[int] = mapped_column(ForeignKey("position.id"))
    position: Mapped[Position] = relationship()


@login_manager.user_loader
def load_user(user_id: int) -> Employee:
    q = select(Employee).where(Employee.id == user_id)
    res = session.execute(q).scalar()
    return res


class Status(Base):
    __tablename__ = "status"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


class Equipment(Base):
    __tablename__ = "equipment"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    status_id: Mapped[int] = mapped_column(ForeignKey("status.id"), default=EquipmentStatus.Working.value)
    status: Mapped[Status] = relationship()
    repairs: Mapped["Repair"] = relationship(back_populates="equipment")


class Comment(Base):
    __tablename__ = "comment"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    employee_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))
    repair_id: Mapped[int] = mapped_column(ForeignKey("repair.id"))
    employee: Mapped[Employee] = relationship()
    repair_order: Mapped["Repair"] = relationship(back_populates="comments")

    def __repr__(self):
        return f"<Comment({self.content, self.employee_id})>"


class Material(Base):
    __tablename__ = "material"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]


repair_materials = Table(
    "reapir_materials",
    Base.metadata,
    Column("repair_id", ForeignKey("repair.id"), nullable=False),
    Column("material_id", ForeignKey("material.id"), nullable=False),
)

repair_employees = Table(
    "reapir_employees",
    Base.metadata,
    Column("repair_id", ForeignKey("repair.id"), nullable=False),
    Column("employee_id", ForeignKey("employee.id"), nullable=False),
)


class Repair(Base):
    __tablename__ = "repair"
    id: Mapped[int] = mapped_column(primary_key=True)
    repair_number: Mapped[int]  # номер в таблице
    # status_id: Mapped[int] = mapped_column(ForeignKey("repair_status.id"))
    # status: Mapped[RepairStatusName] = relationship()
    equipment_id: Mapped[int] = mapped_column(ForeignKey("equipment.id"))  # какое оборудование в ремонте
    equipment: Mapped[Equipment] = relationship(back_populates="repairs")
    identified_by_id: Mapped[int] = mapped_column(ForeignKey("employee.id"))  # кто выявил поломку
    identified_employee: Mapped[Employee] = relationship(foreign_keys=[identified_by_id])
    breakdown_date: Mapped[date] = mapped_column(insert_default=date.today())  # дата поломки
    breakdown_description: Mapped[str]
    expected_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # ожидаемая дата починки
    inspection_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)  # дата ознакомления ремонтной бригады
    inspection_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employee.id"), nullable=True
    )  # кто и знакомился с поломкой
    inspected_employee: Mapped[Employee] = relationship(foreign_keys=[inspection_by_id])
    repair_date: Mapped[date] = mapped_column(Date, nullable=True)  # дата починки
    acceptance_date: Mapped[date] = mapped_column(Date, nullable=True)  # дата приемки
    accepted_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("employee.id"), nullable=True
    )  # кто осуществлял приемку
    accepted_employee: Mapped[Employee] = relationship(foreign_keys=[accepted_by_id])
    materials: Mapped[list[Material]] = relationship(secondary=repair_materials)
    executors: Mapped[list[Employee]] = relationship(secondary=repair_employees)
    comments: Mapped[list[Comment]] = relationship(back_populates="repair_order")
