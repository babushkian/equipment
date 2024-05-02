from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    EmailField,
    FloatField,
    FieldList,
    DateField,
    Form,
    ValidationError,
    FormField,
    HiddenField,
    SelectField,
)
from wtforms.fields.choices import SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired


class AddEquipmentForm(FlaskForm):
    equipment_name = StringField("Оборудование", validators=[DataRequired(), Length(4, 64)], name="equip_name")
    submit = SubmitField("Добавить")


class AddRepairForm(FlaskForm):
    equipment_id = SelectField("Оборудование", validators=[DataRequired()])
    description = StringField("Описание поломки", validators=[DataRequired(), Length(5, 100)], name="description")
    submit = SubmitField("Подтвердить")


class AddCommentForm(FlaskForm):
    comment = StringField(
        "Комментарий",
        validators=[DataRequired(), Length(max=100)],
        name="new_comment",
        description="комментируйте на здоровье",
    )
    repair_id = HiddenField()
    submit = SubmitField("Добавить")


class LoginForm(FlaskForm):
    user_id = SelectField("Сотрудники", validators=[DataRequired()])
    submit = SubmitField("Выбрать")


class StartRepairForm(FlaskForm):
    repair_id = HiddenField()
    expexted_date = DateField("ожидаемая дата окончания ремонта", validators=[DataRequired()])
    worker_ids = SelectMultipleField("Исполнители", validators=[DataRequired()])
    materials_ids = SelectMultipleField("Материалы", validators=[DataRequired()])
    submit = SubmitField("Подтвердить")


class MultiForm(FlaskForm):
    user_id = SelectMultipleField("Сотрудники", validators=[DataRequired()])
    submit = SubmitField("Выбрать")
