from etc.common import EquipmentStatus as Es, Position as P, Actions as A

"""
Здесь вычисляется появление тех или иных кнопок в интерфейсе в зависимости отдолжности пользователя и состояния ремнота
"""

permissions: dict[A, dict[int, Es | None]] = {
    A.History: {P.HoS.value: None, P.HoRT.value: None, P.Engeneer.value: None},
    A.AddRep: {P.HoS.value: Es.Working.value},
    A.AddRepTitle: {P.HoS.value: None},
    A.AddEquip: {P.Engeneer.value: None},
    A.SartRepair: {P.HoRT.value: Es.Detected.value},
    A.EndRepair: {P.HoRT.value: Es.Repairing.value},
    A.Accept: {P.HoS.value: Es.Fixed.value},
    A.Comment: {P.Worker.value: None, P.HoS.value: None, P.HoRT.value: None, P.Engeneer.value: None},
}


def get_permission(action: A, position: int, status: int | None = None) -> bool:
    """
    Права действуют по следующему принципу: в словаре permissions на определенное действие (Action)
    есть ключ, указываюший на определенную должность, например Position.Engeneer.value. Если его нет, значит
    действие для данной должности не разрешено. Если ключ присутствует, но его значение равно None,
    значит действие для данной должности разрешено для любого состояния оборудования.
    Если ключ равен какому-то конкретному состоянию оборудования, например Es.Detected.value, то
    действие для данной должности разрешено только если оборудование находится в указанном состоянии.
    Отсутствие ключа должности: действие по любому запрещено.
    Значение ключа равно None: действие для данного ключа разрешено в любом случае
    Ключ имеет конкретное значение: действие разрешено только при указанном состоянии оборудования
    """
    ep = permissions[action].get(position)
    if (pos := position in permissions[action].keys()) and ep is None:
        return True
    if pos and status == permissions[action][position]:
        return True
    return False


"""
данные кнопок: когда появляются, в какой роут отправляют данные, и что именно отправляют
"""
action_data = {
    A.History: {
        "name": "equipment-history",
        "endpoint": "equipment_history",
        "title": "история",
        "value_key": "eid",
        "method": "GET",
    },
    A.AddEquip: {
        "name": "add-equipment",
        "endpoint": "equipment_add",
        "title": "добавить оборудование",
        "value_key": "eid",
        "method": "GET",
    },
    A.AddRep: {
        "name": "add-repair",
        "endpoint": "repair_create",
        "title": "добавить заявку на ремонт",
        "value_key": "eid",
        "method": "GET",
    },
    A.SartRepair: {
        "name": "start-repair",
        "endpoint": "repair_start",
        "title": "отправить в ремонт",
        "value_key": "rid",
        "method": "get",
    },
    A.EndRepair: {
        "name": "end-repair",
        "endpoint": "repair_finish",
        "title": "закончить ремонт",
        "value_key": "rid",
        "method": "POST",
    },
    A.Accept: {
        "name": "repair_accept",
        "endpoint": "repair_accept",
        "title": "принять оборудование",
        "value_key": "rid",
        "method": "POST",
    },
    A.Comment: {
        "name": "comment",
        "endpoint": "repair_comment",
        "title": "комментарии",
        "value_key": "rid",
        "method": "POST",
    },
    A.AddRepTitle: {
        "name": "add-repair",
        "endpoint": "repair_create",
        "title": "добавить заявку на ремнот",
        "value_key": "rid",
        "method": "GET",
    },
}


def get_action_buttons(actions: list[A], user, status_id, rid, eid=None):
    uid = user.id  # user_id
    act_dict = {}
    for a in actions:
        button_dict = {"display": False}
        if get_permission(a, user.position_id, status_id):
            button_dict = {
                "display": True,
                "name": action_data[a]["name"],
                "endpoint": action_data[a]["endpoint"],
                "title": action_data[a]["title"],
                "method": action_data[a]["method"],
                "value": locals().get(action_data[a]["value_key"]),
            }
        act_dict[action_data[a]["name"]] = button_dict
    return act_dict
