from sqlalchemy import event, insert
from sqlalchemy.engine import Engine
from datetime import date
from models import Base, engine, session
from models.models import (
    Position,
    Employee,
    Status,
    Equipment,
    Repair,
    Material,
    Comment,
    repair_materials,
    repair_employees,
)
from etc.common import EquipmentStatus


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode = MEMORY")
    cursor.execute("PRAGMA synchronous = OFF")
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


print(Base.metadata)
print(dir(Base.metadata))
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

print(Position)
print(dir(Position))
l = []
l.append(Position(id=1, name="работник"))
l.append(Position(id=2, name="начальник цеха"))
l.append(Position(id=3, name="начальник ремонтной службы"))
l.append(Position(id=4, name="главный инженер"))

session.add_all(l)
session.commit()
l = []
l.append(Employee(name="Марков А.И.", position_id=1))
l.append(Employee(name="Чахлый Ю.А.", position_id=1))
l.append(Employee(name="Злодеев Д.С.", position_id=2))
l.append(Employee(name="Степкин А.П.", position_id=3))
l.append(Employee(name="Перемыкин В.П.", position_id=4))
l.append(Employee(name="Ведерников А.А.", position_id=1))
l.append(Employee(name="Чупрунов М.С.", position_id=2))
l.append(Employee(name="Сажин С.С.", position_id=1))
session.add_all(l)
session.commit()


l = []
l.append(Status(id=EquipmentStatus.Detected.value, name="выявлена поломка"))
l.append(Status(id=EquipmentStatus.Repairing.value, name="в ремонте"))
l.append(Status(id=EquipmentStatus.Fixed.value, name="устранено"))
l.append(Status(id=EquipmentStatus.Working.value, name="в работе"))
session.add_all(l)
session.commit()

l = []
l.append(Equipment(id=1, name="самолет", status_id=EquipmentStatus.Repairing.value))
l.append(Equipment(id=2, name="камаз", status_id=EquipmentStatus.Detected.value))
l.append(Equipment(id=3, name="спектрометр", status_id=EquipmentStatus.Working.value))
l.append(Equipment(id=4, name="качеля", status_id=EquipmentStatus.Fixed.value))
l.append(Equipment(id=5, name="Зенит-Арена", status_id=EquipmentStatus.Detected.value))
l.append(Equipment(id=6, name="мост", status_id=EquipmentStatus.Working.value))
l.append(Equipment(id=7, name="вешалка", status_id=EquipmentStatus.Working.value))
l.append(Equipment(id=8, name="ботинки", status_id=EquipmentStatus.Working.value))
l.append(Equipment(id=9, name="очки", status_id=EquipmentStatus.Working.value))
l.append(Equipment(id=10, name="жигуль", status_id=EquipmentStatus.Working.value))
l.append(Equipment(id=11, name="домофон", status_id=EquipmentStatus.Working.value))
session.add_all(l)
session.commit()

l = []
l.append(Material(id=1, name="дерево"))
l.append(Material(id=2, name="камень"))
l.append(Material(id=3, name="железо"))
l.append(Material(id=4, name="золото"))
l.append(Material(id=5, name="алмазы"))
session.add_all(l)
session.commit()


rep_dict = [
    {
        "repair_number": 1,
        "equipment_id": 1,
        "identified_by_id": 3,
        "breakdown_date": date(2023, 12, 31),
        "breakdown_description": "упал",
        "expected_date": date(2025, 10, 30),
        "inspection_date": date(2024, 1, 11),
        "inspection_by_id": 4,
    },
    {
        "repair_number": 2,
        "equipment_id": 4,
        "identified_by_id": 3,
        "breakdown_date": date(2024, 1, 15),
        "breakdown_description": "не качает",
        "expected_date": date(2024, 5, 1),
        "inspection_date": date(2024, 4, 1),
        "inspection_by_id": 4,
        "repair_date": date(2024, 4, 2),
    },
    {
        "repair_number": 3,
        "equipment_id": 5,
        "identified_by_id": 7,
        "breakdown_date": date(2022, 6, 5),
        "breakdown_description": "бакланы склевали",
    },
    {
        "repair_number": 4,
        "equipment_id": 2,
        "identified_by_id": 7,
        "breakdown_date": date(2024, 3, 19),
        "breakdown_description": "колеса не едут",
    },
    {
        "repair_number": 5,
        "equipment_id": 9,
        "identified_by_id": 3,
        "breakdown_date": date(2023, 2, 14),
        "breakdown_description": "линза выпала",
        "expected_date": date(2023, 2, 20),
        "inspection_date": date(2023, 2, 15),
        "inspection_by_id": 4,
        "repair_date": date(2023, 2, 18),
        "acceptance_date": date(2023, 2, 19),
        "accepted_by_id": 7,
    },
    {
        "repair_number": 6,
        "equipment_id": 9,
        "identified_by_id": 7,
        "breakdown_date": date(2023, 4, 10),
        "breakdown_description": "дужка отвалилась",
        "expected_date": date(2023, 5, 1),
        "inspection_date": date(2023, 4, 10),
        "inspection_by_id": 4,
        "repair_date": date(2023, 4, 15),
        "acceptance_date": date(2023, 4, 15),
        "accepted_by_id": 7,
    },
]
for rep in rep_dict:
    session.add(Repair(**rep))
session.commit()

session.close()

l = []
l.append(Comment(id=1, content="вот это да", employee_id=1, repair_id=1))
l.append(Comment(id=2, content="это конец", employee_id=2, repair_id=1))
l.append(Comment(id=3, content="да как так-то", employee_id=3, repair_id=1))
l.append(Comment(id=4, content="все пропало", employee_id=4, repair_id=2))
l.append(Comment(id=5, content="тут разбираться надо", employee_id=5, repair_id=2))
l.append(Comment(id=6, content="первый раз такое вижу", employee_id=6, repair_id=2))
l.append(Comment(id=7, content="никогда такого не было", employee_id=7, repair_id=3))
l.append(Comment(id=8, content="тяжеловато", employee_id=6, repair_id=3))
l.append(Comment(id=9, content="а я говорил", employee_id=4, repair_id=3))
l.append(Comment(id=10, content="просто руки опускаются", employee_id=2, repair_id=4))
session.add_all(l)
session.commit()


# связь ремннтов с материалами
rm = [
    {"repair_id": 1, "material_id": 1},
    {"repair_id": 1, "material_id": 3},
    {"repair_id": 2, "material_id": 4},
    {"repair_id": 2, "material_id": 5},
    {"repair_id": 5, "material_id": 5},
    {"repair_id": 6, "material_id": 3},
    {"repair_id": 6, "material_id": 4},
]

# связь ремннтов с исполнителями
re = [
    {"repair_id": 1, "employee_id": 1},
    {"repair_id": 1, "employee_id": 2},
    {"repair_id": 2, "employee_id": 1},
    {"repair_id": 2, "employee_id": 2},
    {"repair_id": 2, "employee_id": 6},
    {"repair_id": 5, "employee_id": 8},
    {"repair_id": 6, "employee_id": 6},
]
with engine.connect() as connection:
    connection.execute(insert(repair_materials), rm)
    connection.execute(insert(repair_employees), re)
    connection.commit()
