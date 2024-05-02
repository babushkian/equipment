from sqlalchemy import select

from models import session
from models.models import Equipment
from etc.common import EquipmentStatus
from etc.permisisons import get_action_buttons
from etc.common import Actions


def get_working_equpment() -> list[Equipment]:
    q = select(Equipment).where(Equipment.status_id == EquipmentStatus.Working.value)
    result = session.execute(q).scalars()
    return result


def get_add_equiment_button_data(user):
    add_eq_button = get_action_buttons([Actions.AddEquip], user, status_id=None, rid=None, eid=None)
    return add_eq_button


def get_equipment_obj_by_id(eid: int) -> Equipment:
    q = select(Equipment).where(Equipment.id == eid)
    return session.execute(q).scalar()


equip_action_buttons = [Actions.History, Actions.AddRep]


def get_equipment_objs() -> list[Equipment]:
    q = select(Equipment)
    return session.execute(q).scalars()


def get_equipment_table(user):
    table_data = []
    equipment = get_equipment_objs()
    for e in equipment:
        table_dict = {
            "id": e.id,
            "name": e.name,
            "repaired": "да" if e.repairs is not None else "нет",
            "status": e.status.name,
        }
        table_dict["action-buttons"] = get_action_buttons(
            equip_action_buttons, user, status_id=e.status.id, rid=None, eid=e.id
        )

        table_data.append(table_dict)
    header = {
        "id": "№",
        "name": "название",
        "repaired": "ремонтировалось",
        "status": "состояние",
        "action-buttons": "действия",
    }
    obj = {"header": header, "data": table_data}
    return obj


def create_new_equipment(equipment_name):
    session.add(Equipment(name=equipment_name))
    session.commit()
