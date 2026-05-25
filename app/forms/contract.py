from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Optional


class ContractForm(FlaskForm):
    house_id = IntegerField("房源ID", validators=[DataRequired(), NumberRange(min=1)])
    tenant_id = IntegerField("租客ID", validators=[DataRequired(), NumberRange(min=1)])
    start_date = DateField("开始日期", validators=[DataRequired()])
    end_date = DateField("结束日期", validators=[DataRequired()])
    monthly_rent = DecimalField("月租金", validators=[DataRequired(), NumberRange(min=0)])
    deposit = DecimalField("押金", validators=[Optional(), NumberRange(min=0)])
    content = TextAreaField("合同条款")
