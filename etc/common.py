from enum import Enum


# этапы ремонта
class EquipmentStatus(int, Enum):
    Detected = 1
    Repairing = 2
    Fixed = 3
    Working = 4


# должности
class Position(int, Enum):
    Worker = 1  # рабочий
    HoS = 2  # начальник цеха
    HoRT = 3  # начальник ремонтной бригады
    Engeneer = 4


# действия, которые могут совершать работники
class Actions(int, Enum):
    History = 1  # история ремонтов конкретного оборудования
    AddEquip = 2  # добавить оборудование
    AddRep = 3  # добавить ремонт
    SartRepair = 4  # приянть времонт
    EndRepair = 5  # закончить ремонт
    Accept = 6  # принять в отремонтированное оборудование в работу
    Comment = 7  # перейти к комментариям
    AddRepTitle = 8  # добавить кнопку "выявить неисправность" над таблицей, а не для конкретного оборудования
