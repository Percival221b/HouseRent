from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange


class RepairForm(FlaskForm):
    house_id = IntegerField("房源ID", validators=[DataRequired(), NumberRange(min=1)])
    title = StringField("问题概述", validators=[DataRequired(), Length(max=120)])
    description = TextAreaField("问题描述", validators=[DataRequired()])
