from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    SelectField,
    StringField,
    TextAreaField,
)
from wtforms.validators import DataRequired, NumberRange, Optional, Length

FACILITY_CHOICES = [
    ("空调", "空调"),
    ("冰箱", "冰箱"),
    ("洗衣机", "洗衣机"),
    ("热水器", "热水器"),
    ("宽带", "宽带"),
    ("电视", "电视"),
    ("床", "床"),
    ("衣柜", "衣柜"),
    ("沙发", "沙发"),
    ("餐桌", "餐桌"),
    ("独立卫生间", "独立卫生间"),
    ("阳台", "阳台"),
    ("电梯", "电梯"),
    ("燃气灶", "燃气灶"),
    ("暖气", "暖气"),
]

DECORATION_CHOICES = [
    ("", "不限"),
    ("精装修", "精装修"),
    ("简装修", "简装修"),
    ("豪华装修", "豪华装修"),
    ("毛坯", "毛坯"),
]

ORIENTATION_CHOICES = [
    ("", "不限"),
    ("东", "东"),
    ("南", "南"),
    ("西", "西"),
    ("北", "北"),
    ("东南", "东南"),
    ("西南", "西南"),
    ("东北", "东北"),
    ("西北", "西北"),
    ("南北通透", "南北通透"),
]

LAYOUT_CHOICES = [
    ("", "不限"),
    ("1室0厅", "1室0厅"),
    ("1室1厅", "1室1厅"),
    ("2室1厅", "2室1厅"),
    ("2室2厅", "2室2厅"),
    ("3室1厅", "3室1厅"),
    ("3室2厅", "3室2厅"),
    ("4室1厅", "4室1厅"),
    ("4室2厅", "4室2厅"),
    ("5室及以上", "5室及以上"),
]

DISTRICT_CHOICES = [
    ("", "不限"),
    ("朝阳区", "朝阳区"),
    ("海淀区", "海淀区"),
    ("东城区", "东城区"),
    ("西城区", "西城区"),
    ("丰台区", "丰台区"),
    ("石景山区", "石景山区"),
    ("通州区", "通州区"),
    ("大兴区", "大兴区"),
    ("昌平区", "昌平区"),
    ("顺义区", "顺义区"),
    ("房山区", "房山区"),
]

SORT_CHOICES = [
    ("newest", "最新发布"),
    ("rent_asc", "租金从低到高"),
    ("rent_desc", "租金从高到低"),
    ("area_asc", "面积从小到大"),
    ("area_desc", "面积从大到小"),
]

STATUS_CHOICES = [
    ("vacant", "空置"),
    ("rented", "已出租"),
    ("offline", "下架"),
]


class HouseForm(FlaskForm):
    title = StringField("房源标题", validators=[DataRequired("请输入房源标题"), Length(max=120)])
    address = StringField("详细地址", validators=[DataRequired("请输入详细地址"), Length(max=255)])
    district = SelectField("所在区域", choices=DISTRICT_CHOICES, default="")
    business_area = StringField("商圈", validators=[Optional(), Length(max=120)])
    community = StringField("小区名称", validators=[Optional(), Length(max=120)])
    layout = SelectField("户型", choices=LAYOUT_CHOICES, default="")
    house_type = StringField("房屋类型", validators=[Optional(), Length(max=50)])
    floor = IntegerField("所在楼层", validators=[Optional(), NumberRange(min=1)])
    total_floor = IntegerField("总楼层", validators=[Optional(), NumberRange(min=1)])
    orientation = SelectField("朝向", choices=ORIENTATION_CHOICES, default="")
    area = DecimalField("面积(m²)", validators=[Optional()])
    rent = DecimalField("月租金(元)", validators=[DataRequired("请输入月租金"), NumberRange(min=0)])
    deposit = DecimalField("押金(元)", validators=[Optional(), NumberRange(min=0)])
    decoration = SelectField("装修情况", choices=DECORATION_CHOICES, default="")
    status = SelectField("房源状态", choices=STATUS_CHOICES, default="vacant")
    description = TextAreaField("房源描述", validators=[Optional()])
    video_url = StringField("视频链接", validators=[Optional(), Length(max=255)])

    # Facility checkboxes
    facility_空调 = BooleanField("空调")
    facility_冰箱 = BooleanField("冰箱")
    facility_洗衣机 = BooleanField("洗衣机")
    facility_热水器 = BooleanField("热水器")
    facility_宽带 = BooleanField("宽带")
    facility_电视 = BooleanField("电视")
    facility_床 = BooleanField("床")
    facility_衣柜 = BooleanField("衣柜")
    facility_沙发 = BooleanField("沙发")
    facility_餐桌 = BooleanField("餐桌")
    facility_独立卫生间 = BooleanField("独立卫生间")
    facility_阳台 = BooleanField("阳台")
    facility_电梯 = BooleanField("电梯")
    facility_燃气灶 = BooleanField("燃气灶")
    facility_暖气 = BooleanField("暖气")

    def get_facilities(self) -> list[str]:
        """Collect checked facilities into a list."""
        result = []
        for label, _ in FACILITY_CHOICES:
            field = getattr(self, f"facility_{label}", None)
            if field and field.data:
                result.append(label)
        return result

    def set_facilities(self, facilities: list[str]) -> None:
        """Pre-check facility fields from a stored list."""
        for label, _ in FACILITY_CHOICES:
            field = getattr(self, f"facility_{label}", None)
            if field:
                field.data = label in (facilities or [])


class HouseSearchForm(FlaskForm):
    keyword = StringField("关键词", validators=[Optional()])
    district = SelectField("区域", choices=DISTRICT_CHOICES, default="")
    layout = SelectField("户型", choices=LAYOUT_CHOICES, default="")
    rent_min = IntegerField("最低租金", validators=[Optional(), NumberRange(min=0)])
    rent_max = IntegerField("最高租金", validators=[Optional(), NumberRange(min=0)])
    area_min = IntegerField("最小面积", validators=[Optional(), NumberRange(min=0)])
    area_max = IntegerField("最大面积", validators=[Optional(), NumberRange(min=0)])
    decoration = SelectField("装修", choices=DECORATION_CHOICES, default="")
    orientation = SelectField("朝向", choices=ORIENTATION_CHOICES, default="")
    sort_by = SelectField("排序", choices=SORT_CHOICES, default="newest")
