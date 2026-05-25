from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, NumberRange


class AppointmentForm(FlaskForm):
    house_id = IntegerField("房源ID", validators=[DataRequired(), NumberRange(min=1)])
    appointment_time = DateTimeLocalField("预约时间", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    remark = TextAreaField("备注")
