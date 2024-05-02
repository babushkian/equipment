from sqlalchemy import select

from models import session
from models.models import Employee
from etc.common import Position as Ep


def get_workers() -> list[Employee]:
    q = select(Employee).where(Employee.position_id == Ep.Worker.value)
    result = session.execute(q).scalars().all()
    return result


def get_employee_obj_by_id(eid: int) -> Employee:
    q = select(Employee).where(Employee.id == eid)
    res = session.execute(q).scalar()
    return res


def get_employee_objs_by_ids(eids: list[int]) -> list[Employee]:
    q = select(Employee).where(Employee.id.in_(eids))
    res = session.execute(q).scalars().all()
    return res


def managers_list_for_login() -> list[Employee]:
    q = select(Employee).where(Employee.position_id > 1).order_by(Employee.position_id.desc()).order_by(Employee.name)
    result = session.execute(q).scalars().all()
    return result


def get_all_employees() -> list[Employee]:
    q = select(Employee).order_by(Employee.name)
    result = session.execute(q).scalars().all()
    return result
