from datetime import date

from sqlalchemy import select, null, or_, func

from etc.common import Actions, EquipmentStatus
from crud.equipment import get_equipment_obj_by_id
from crud.users import get_workers
from models import session
from models.models import Repair, Employee, Material, Equipment
from etc.permisisons import get_action_buttons
from crud.comments import format_string, format_comments, crop_text


def get_new_repair_button_data(user: Employee):
    add_rep_button = get_action_buttons([Actions.AddRepTitle], user, status_id=None, rid=None, eid=None)
    return add_rep_button


repair_action_buttons = [Actions.SartRepair, Actions.EndRepair, Actions.Accept, Actions.Comment]


def get_repair_table_data(user, fresh=False, filter_equipment_id=None):
    if fresh:
        q = select(Repair).where(or_(Repair.acceptance_date.is_(null()), Repair.acceptance_date == date.today()))

    elif filter_equipment_id:
        q = (
            select(Repair)
            .join(Equipment, Equipment.id == Repair.equipment_id)
            .where(Equipment.id == filter_equipment_id)
        )
    else:
        q = select(Repair)
    repair = session.execute(q).scalars().all()
    table_data = []
    for r in repair:
        table_dict = {
            "fresh": 1 if (r.acceptance_date is None or r.acceptance_date == date.today()) else 0,
            "id": r.id,
            "repair_number": r.repair_number,
            "status_id": r.equipment.status_id,
            "status": r.equipment.status.name,
            "equipment": r.equipment.name,
            "identified_employee": r.identified_employee.name if r.identified_employee else None,
            "breakdown_date": r.breakdown_date,
            "breakdown_description": r.breakdown_description,
            "expected_date": r.expected_date,
            "inspection_date": r.inspection_date,
            "inspected_employee": r.inspected_employee.name if r.inspected_employee else None,
            "materials": format_string([m.name for m in r.materials]),
            "executors": format_string([m.name for m in r.executors]),
            "repair_date": r.repair_date,
            "acceptance_date": r.acceptance_date,
            "accepted_employee": r.accepted_employee.name if r.accepted_employee else None,
            "comments": crop_text(format_comments(r.comments), 100),
            "action-buttons": get_action_buttons(
                repair_action_buttons, user, r.equipment.status_id, r.id, filter_equipment_id
            ),
        }
        table_data.append(table_dict)

    header = {
        "fresh": "свежак",
        "repair_number": "№ заявки",
        "equipment": "оборудование",
        "status": "статус оборудования",
        "breakdown_date": "дата поломки",
        "breakdown_description": "описание поломки",
        "identified_employee": "выявил",
        "expected_date": "ожидаемая дата окончания ремонта",
        "inspection_date": "дата ознакомления ремонтной службы",
        "inspected_employee": "ФИO ознакомлен",
        "repair_date": "дата устранения",
        "executors": "исполнители",
        "materials": "материалы",
        "acceptance_date": "дата приемки",
        "accepted_employee": "ФИО принял",
        "comments": "комментарии",
        "action-buttons": "действия",
    }
    obj = {"header": header, "data": table_data}
    return obj


def get_repair_obj_by_id(repair_id: int) -> Repair:
    q = select(Repair).where(Repair.id == repair_id)
    r = session.execute(q).scalar()
    return r


def get_repair_objs_by_equipment_id(equipment_id: int) -> list[Repair]:
    r = get_equipment_obj_by_id(equipment_id)
    return r.repairs


def get_materials() -> list[Material]:
    return session.execute(select(Material)).scalars().all()


def get_material_obj_by_id(mid: int) -> Material:
    q = select(Material).where(Material.id == mid)
    res = session.execute(q).scalar()
    return res


def get_material_objs_by_ids(eids: list[int]) -> list[Material]:
    q = select(Material).where(Material.id.in_(eids))
    res = session.execute(q).scalars().all()
    return res


def get_start_repair_data(user: Employee, repair: Repair):
    data = {
        "title": {"equipment": repair.equipment.name, "repair_number": repair.repair_number},
        "info": {
            "Описание поломки": repair.breakdown_description,
            "ФИO ознакомлен": user.name,
            "Дата ознакомления": date.today(),
        },
        "form": {
            "executors": [(w.id, w.name) for w in get_workers()],
            "materials": [(m.id, m.name) for m in get_materials()],
        },
    }
    return data


def get_finish_repair_data(repair: Repair):
    data = {
        "title": {"equipment": repair.equipment.name, "repair_number": repair.repair_number},
        "form": {
            "repair_id": repair.id,
            "description": repair.breakdown_description,
            "executors": ", ".join([e.name for e in repair.executors]),
            "repair_date": date.today(),
        },
    }
    return data


def get_accept_repair_data(user: Employee, repair: Repair):
    data = {
        "title": {"equipment": repair.equipment.name, "repair_number": repair.repair_number},
        "form": {
            "accepted_employee": user.name,
            "repair_id": repair.id,
            "description": repair.breakdown_description,
            "repair_date": repair.repair_date,
            "accept_date": date.today(),
        },
    }
    return data


def create_new_repair(user, equipment_id, description) -> None:
    q = select(func.max(Repair.repair_number))
    new_number = session.execute(q).scalar() + 1
    # присавиваем оборудованию статус "выявлена неисправность"
    q = select(Equipment).where(Equipment.id == equipment_id)
    eq: Equipment = session.execute(q).scalar()
    eq.status_id = EquipmentStatus.Detected.value
    params = {
        "repair_number": new_number,
        "equipment_id": equipment_id,
        "identified_by_id": user.id,
        "breakdown_description": description,
    }
    r = Repair(**params)
    session.add(r)
    session.commit()
