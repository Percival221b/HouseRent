from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, StringField, TextAreaField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ComplaintForm(FlaskForm):
    house_id = SelectField("关联房源", coerce=int, validators=[Optional()])
    target_user_id = SelectField("被投诉人", coerce=int, validators=[Optional()])
    title = StringField("投诉标题", validators=[DataRequired(), Length(max=120)])
    content = TextAreaField("投诉内容", validators=[DataRequired()])
