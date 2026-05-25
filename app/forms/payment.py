from flask_wtf import FlaskForm
from wtforms import DateField, DecimalField, IntegerField, SelectField
from wtforms.validators import DataRequired, NumberRange


class PaymentForm(FlaskForm):
    contract_id = IntegerField("合同ID", validators=[DataRequired(), NumberRange(min=1)])
    amount = DecimalField("金额", validators=[DataRequired(), NumberRange(min=0.01)])
    payment_type = SelectField("费用类型", choices=[
        ("rent", "租金"), ("deposit", "押金"), ("other", "其他"),
    ], default="rent")
    payment_method = SelectField("支付方式", choices=[
        ("mock", "模拟支付"), ("cash", "现金"),
        ("alipay", "支付宝"), ("wechat", "微信"), ("bank_card", "银行卡"),
    ], default="mock")
    due_date = DateField("截止日期", validators=[DataRequired()])
