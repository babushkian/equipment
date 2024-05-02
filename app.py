from datetime import date

from flask import Flask, url_for, render_template, request, redirect, flash

from flask_login import login_required, login_user, current_user, logout_user
from etc.forms import AddEquipmentForm, AddCommentForm, LoginForm, AddRepairForm, StartRepairForm

from models import session, login_manager
from etc.common import EquipmentStatus

from crud.repair import (
    get_repair_table_data,
    get_new_repair_button_data,
    get_repair_obj_by_id,
    get_start_repair_data,
    get_finish_repair_data,
    get_accept_repair_data,
    create_new_repair,
    get_material_objs_by_ids,
)
from crud.users import (
    managers_list_for_login,
    get_employee_obj_by_id,
    get_employee_objs_by_ids,
)
from crud.equipment import (
    get_working_equpment,
    get_equipment_table,
    get_add_equiment_button_data,
    create_new_equipment,
    get_equipment_obj_by_id,
)
from crud.comments import get_comments, add_new_comment

app = Flask(__name__)
app.config["SECRET_KEY"] = "aboba"


login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Для работы необходимо авторизоваться."


@app.get("/logout")
@login_required
def logout():
    if current_user:
        logout_user()
    return redirect(url_for("login"))


@app.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    employees_list = managers_list_for_login()
    form.user_id.choices = [(e.id, f"{e.name} ({e.position.name})") for e in employees_list]
    if form.validate_on_submit():
        user = get_employee_obj_by_id(int(form.user_id.data))
        login_user(user, remember=True)
        return redirect(url_for("repair_table"))
    return render_template("login.html", employees=employees_list, form=form)


@app.get("/")
@login_required
def repair_table():
    data = get_repair_table_data(current_user)
    data["user"] = current_user
    add_rep = get_new_repair_button_data(current_user)
    data.update(add_rep)
    return render_template("repairs.html", data=data)


@app.route("/repair_create", methods=("GET", "POST"))
@login_required
def repair_create():
    form = AddRepairForm()
    el = get_working_equpment()
    selected = request.args.get("add-repair")
    form.equipment_id.choices = [(e.id, e.name) for e in el]

    if form.validate_on_submit():
        create_new_repair(current_user, int(form.equipment_id.data), form.description.data)
        flash("Создана заявка на ремнот", category="success")

        return redirect(url_for("repair_table"))
    else:
        if selected is not None:
            form.equipment_id.data = selected
        data = {"user": current_user}
        return render_template("repair_create.html", data=data, form=form)


@app.get("/repair_start")
@login_required
def repair_start():
    form = StartRepairForm()
    repair_id = int(request.args.get("start-repair"))
    repair = get_repair_obj_by_id(repair_id)
    data = get_start_repair_data(current_user, repair)
    form.repair_id.data = repair_id
    form.worker_ids.choices = data["form"]["executors"]
    form.worker_ids.render_kw = {"size": len(data["form"]["executors"])}
    form.materials_ids.choices = data["form"]["materials"]
    form.materials_ids.render_kw = {"size": len(data["form"]["materials"])}
    form.expexted_date.min_date = date.today()
    del data["form"]
    data["user"] = current_user
    return render_template("repair_start.html", data=data, form=form)


@app.post("/repair_start_process")
@login_required
def repair_start_process():
    form = StartRepairForm()
    repair_id = int(request.form["repair_id"])
    repair = get_repair_obj_by_id(repair_id)
    data = get_start_repair_data(current_user, repair)
    form.worker_ids.choices = data["form"]["executors"]
    form.materials_ids.choices = data["form"]["materials"]
    if form.validate_on_submit():
        expected = form.expexted_date.data
        executors = get_employee_objs_by_ids(list(map(int, form.worker_ids.data)))
        materials = get_material_objs_by_ids(list(map(int, form.materials_ids.data)))

        repair.inspected_employee = current_user
        repair.equipment.status_id = EquipmentStatus.Repairing.value
        repair.expected_date = expected
        repair.executors = executors
        repair.materials = materials
        session.commit()
        flash("Сделана запись о начале ремонта", category="success")
    else:
        flash("Заявка на ремонт не добавлена", category="danger")
    return redirect(url_for("repair_table"))


@app.post("/repair_finish")
@login_required
def repair_finish():

    repair_id = int(request.form["end-repair"])
    repair = get_repair_obj_by_id(repair_id)
    data = get_finish_repair_data(repair)
    data["user"] = current_user
    return render_template("repair_finish.html", data=data)


@app.post("/repair_finish_process")
@login_required
def repair_finish_process():
    if request.form:
        repair = get_repair_obj_by_id(int(request.form["repair_id"]))
        repair.equipment.status_id = EquipmentStatus.Fixed.value
        repair.repair_date = date.today()
        session.commit()
        flash("Сделана запись об окончании ремонта", category="success")
    else:
        flash("Не удалось сделать запись об окончании ремонта", category="danger")
    return redirect(url_for("repair_table"))


@app.post("/repair_accept")
@login_required
def repair_accept():
    repair_id = int(request.form["repair_accept"])
    repair = get_repair_obj_by_id(repair_id)
    data = get_accept_repair_data(current_user, repair)
    data["user"] = current_user
    return render_template("repair_accept.html", data=data)


@app.post("/repair_accept_process")
@login_required
def repair_accept_process():
    if request.form:
        repair = get_repair_obj_by_id(int(request.form["repair_id"]))
        repair.equipment.status_id = EquipmentStatus.Working.value
        repair.accepted_employee = current_user
        repair.acceptance_date = date.today()
        session.commit()
        flash("Сделана запись о приеме оборудования в эксплуатацию", category="success")
    else:
        flash("Не удалось сделать запись о приеме оборудования в эксплуатацию", category="danger")
    return redirect(url_for("repair_table"))


@app.post("/repair_comment")
@login_required
def repair_comment():
    if request.form:
        repair = get_repair_obj_by_id(int(request.form["comment"]))
        all_comments = get_comments(repair)
        data = {"repair": repair, "comments": all_comments, "user": current_user}
        form = AddCommentForm()
        form.repair_id.data = repair.id
    return render_template("comment.html", data=data, form=form)


@app.post("/repair_comment_process")
@login_required
def repair_comment_process():
    form = AddCommentForm()
    if form.validate_on_submit():
        comment = form.comment.data
        repair_id = form.repair_id.data
        add_new_comment(comment, repair_id, current_user.id)
        flash("Добавлен новый комментарий", category="success")
    else:
        flash("Не удалось добавить новый комментарий", category="danger")
    return redirect(url_for("repair_table"))


@app.get("/equipment")
@login_required
def equipment_table():
    data = get_equipment_table(current_user)  # словарь с заголовком и телом таблицы
    data["user"] = current_user  # данные для отображения юзера в заголовке страницы
    add_eq = get_add_equiment_button_data(current_user)
    data.update(add_eq)
    return render_template("equipment.html", data=data)


@app.route("/add_equipment", methods=("POST", "GET"))
@login_required
def equipment_add():
    form = AddEquipmentForm(request.form)
    if form.validate_on_submit():
        create_new_equipment(form.equipment_name.data)
        flash("Добавлено новое оборудование", category="success")
        return redirect(url_for("equipment_table"))
    else:
        data = {"user": current_user}
        return render_template("add_equipment.html", data=data, form=form)


@app.get("/equipment_history")
@login_required
def equipment_history():
    eid = int(request.args.get("equipment-history"))
    equipment = get_equipment_obj_by_id(eid)
    data = get_repair_table_data(current_user, filter_equipment_id=eid)
    data["user"] = current_user
    data["title"] = {"equipment": equipment.name, "status": equipment.status.name}
    return render_template("equipment_history.html", data=data)


app.run(debug=True)
