"""Seed the database with test house listings for Module C development."""
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.extensions import db
from app.models import Contract, House, HouseImage, User
from sqlalchemy import text
from werkzeug.security import generate_password_hash

app = create_app("development")

DEFAULT_HOUSE_IMAGE = "uploads/houses/default-house.svg"
DEMO_CONTRACT_NO = "CON-DEMO-TEST-TENANT"
SYSTEM_ADMIN_USERNAME = os.getenv("SYSTEM_ADMIN_USERNAME", "system_admin")
SYSTEM_ADMIN_PASSWORD = os.getenv("SYSTEM_ADMIN_PASSWORD", "SystemAdmin123")
DEMO_IMAGE_URLS = [
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1484154218962-a197022b5858?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1493809842364-78817add7ffb?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1554995207-c18c203602cb?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1615873968403-89e068629265?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1560185007-cde436f6a4d0?auto=format&fit=crop&w=1200&q=80",
    "https://images.unsplash.com/photo-1560185127-6ed189bf02f4?auto=format&fit=crop&w=1200&q=80",
]

TEST_HOUSES = [
    {
        "title": "【测试数据】朝阳区望京精装修两室一厅 近地铁15号线",
        "address": "北京市朝阳区望京街道望京西园三区12号楼3单元502",
        "district": "朝阳区",
        "business_area": "望京",
        "community": "望京西园三区",
        "layout": "2室1厅",
        "house_type": "普通住宅",
        "floor": 5,
        "total_floor": 18,
        "orientation": "南北通透",
        "area": 85.5,
        "rent": 6500,
        "deposit": 6500,
        "decoration": "精装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "床", "衣柜", "沙发", "电梯"],
        "status": "vacant",
        "description": "【测试数据】望京核心地段精装修两居室，南北通透，采光极好。小区环境优美，物业管理规范，24小时保安。步行5分钟到地铁15号线望京站，周边商圈成熟，超市、商场、餐饮一应俱全。家具家电齐全，拎包入住。",
    },
    {
        "title": "【测试数据】海淀区中关村高档公寓 一室一厅 适合白领",
        "address": "北京市海淀区中关村南大街甲8号中关村SOHO B座1502",
        "district": "海淀区",
        "business_area": "中关村",
        "community": "中关村SOHO",
        "layout": "1室1厅",
        "house_type": "商住两用",
        "floor": 15,
        "total_floor": 25,
        "orientation": "南",
        "area": 55.0,
        "rent": 5200,
        "deposit": 5200,
        "decoration": "豪华装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "电视", "床", "衣柜", "沙发", "独立卫生间", "电梯"],
        "status": "vacant",
        "description": "【测试数据】中关村核心商务区高档公寓，紧邻地铁4号线中关村站。全新豪华装修，品牌家电，智能门锁。楼下就是中关村购物中心，生活配套完善。特别适合在互联网公司工作的白领人士。",
    },
    {
        "title": "【测试数据】东城区胡同改造LOFT 文艺复古风 短租长租均可",
        "address": "北京市东城区安定门内大街方家胡同23号",
        "district": "东城区",
        "business_area": "安定门",
        "community": "方家胡同",
        "layout": "1室1厅",
        "house_type": "胡同改造",
        "floor": 1,
        "total_floor": 1,
        "orientation": "东",
        "area": 40.0,
        "rent": 4800,
        "deposit": 4800,
        "decoration": "精装修",
        "facilities": ["空调", "洗衣机", "热水器", "宽带", "床", "衣柜", "沙发", "独立卫生间", "暖气"],
        "status": "vacant",
        "description": "【测试数据】老北京胡同里的独特LOFT空间，设计师改造，保留原有砖墙和木梁结构。独立小院，闹中取静。步行可达雍和宫、国子监，周边网红咖啡馆和特色餐厅众多。",
    },
    {
        "title": "【测试数据】西城区金融街附近三室两厅 家庭整租 拎包入住",
        "address": "北京市西城区金融街街道丰汇园小区7号楼1单元801",
        "district": "西城区",
        "business_area": "金融街",
        "community": "丰汇园",
        "layout": "3室2厅",
        "house_type": "普通住宅",
        "floor": 8,
        "total_floor": 12,
        "orientation": "南北通透",
        "area": 130.0,
        "rent": 15000,
        "deposit": 15000,
        "decoration": "豪华装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "电视", "床", "衣柜", "沙发", "餐桌", "独立卫生间", "阳台", "电梯", "燃气灶", "暖气"],
        "status": "vacant",
        "description": "【测试数据】金融街核心位置大三居，南北通透，全明户型。品牌豪华装修，中央空调，全屋地暖。主卧带独立卫生间和衣帽间。小区物业管理一流，配有游泳池和健身房。步行10分钟到金融街各大写字楼。",
    },
    {
        "title": "【测试数据】丰台区科技园附近合租单间 适合实习生 价格实惠",
        "address": "北京市丰台区丰台科技园航丰路8号院2号楼1304",
        "district": "丰台区",
        "business_area": "丰台科技园",
        "community": "航丰路8号院",
        "layout": "3室1厅",
        "house_type": "合租单间",
        "floor": 13,
        "total_floor": 20,
        "orientation": "北",
        "area": 18.0,
        "rent": 1800,
        "deposit": 1800,
        "decoration": "简装修",
        "facilities": ["空调", "洗衣机", "热水器", "宽带", "床", "衣柜"],
        "status": "vacant",
        "description": "【测试数据】丰台科技园附近合租单间，价格实惠，押一付一。房间干净整洁，室友都是附近上班的年轻人，氛围融洽。距地铁9号线丰台科技园站步行8分钟。楼下有便利店和食堂，生活方便。",
    },
    {
        "title": "【测试数据】昌平区回龙观整租两居室 超大阳台 停车方便",
        "address": "北京市昌平区回龙观东大街龙腾苑六区15号楼5单元302",
        "district": "昌平区",
        "business_area": "回龙观",
        "community": "龙腾苑六区",
        "layout": "2室1厅",
        "house_type": "普通住宅",
        "floor": 3,
        "total_floor": 6,
        "orientation": "南北",
        "area": 92.0,
        "rent": 4200,
        "deposit": 4200,
        "decoration": "精装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "电视", "床", "衣柜", "沙发", "餐桌", "阳台", "燃气灶"],
        "status": "vacant",
        "description": "【测试数据】回龙观核心区两居整租，超大阳台，小区绿化好。新装修不到一年，环保材料。步行到地铁8号线回龙观东大街站约10分钟。小区有充足停车位。周边有大型超市和商业街，生活便利。",
    },
    {
        "title": "【测试数据】通州区万达广场旁 LOFT公寓 全新装修 首租",
        "address": "北京市通州区新华西街58号万达广场3号公寓楼2206",
        "district": "通州区",
        "business_area": "通州万达",
        "community": "万达广场公寓",
        "layout": "1室1厅",
        "house_type": "LOFT公寓",
        "floor": 22,
        "total_floor": 28,
        "orientation": "西南",
        "area": 48.0,
        "rent": 3500,
        "deposit": 3500,
        "decoration": "精装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "电视", "床", "衣柜", "沙发", "独立卫生间", "电梯"],
        "status": "vacant",
        "description": "【测试数据】通州万达广场旁高端LOFT公寓，全新首次出租。层高4.5米，上下两层独立空间。全景落地窗，城市夜景绝佳。楼下就是万达广场，餐饮购物娱乐一站式。距地铁八通线通州北苑站步行3分钟。",
    },
    {
        "title": "【测试数据】大兴区亦庄经济开发区 独栋别墅 带花园车位",
        "address": "北京市大兴区亦庄经济开发区荣华南路10号院 紫禁壹号院16栋",
        "district": "大兴区",
        "business_area": "亦庄",
        "community": "紫禁壹号院",
        "layout": "4室2厅",
        "house_type": "独栋别墅",
        "floor": 1,
        "total_floor": 3,
        "orientation": "南北通透",
        "area": 280.0,
        "rent": 25000,
        "deposit": 50000,
        "decoration": "豪华装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "电视", "床", "衣柜", "沙发", "餐桌", "独立卫生间", "阳台", "电梯", "燃气灶", "暖气"],
        "status": "vacant",
        "description": "【测试数据】亦庄核心区独栋别墅，地上三层地下一层。带200平米私家花园和双车位。中央空调，全屋智能家居系统。小区容积率仅0.8，绿化率超60%。适合企业高管和外籍人士居住。",
    },
    {
        "title": "【测试数据】顺义区中央别墅区 精装大三居 国际学校旁",
        "address": "北京市顺义区天竺镇空港工业区天柱东路28号 丽京花园18号楼",
        "district": "顺义区",
        "business_area": "中央别墅区",
        "community": "丽京花园",
        "layout": "3室2厅",
        "house_type": "普通住宅",
        "floor": 2,
        "total_floor": 6,
        "orientation": "南北通透",
        "area": 155.0,
        "rent": 18000,
        "deposit": 36000,
        "decoration": "豪华装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "电视", "床", "衣柜", "沙发", "餐桌", "独立卫生间", "阳台", "电梯", "燃气灶", "暖气"],
        "status": "vacant",
        "description": "【测试数据】顺义中央别墅区精装大三居，紧邻多所知名国际学校。低密度洋房社区，一梯两户。全屋进口品牌家具家电，地暖中央空调。小区24小时管家式物业服务。距首都机场高速出口仅5分钟。",
    },
    {
        "title": "【测试数据】石景山区首钢园附近 整租一居 工业风装修",
        "address": "北京市石景山区首钢园北区冬奥环路1号院6号楼1203",
        "district": "石景山区",
        "business_area": "首钢园",
        "community": "首钢园冬奥社区",
        "layout": "1室1厅",
        "house_type": "公寓",
        "floor": 12,
        "total_floor": 18,
        "orientation": "东",
        "area": 50.0,
        "rent": 3800,
        "deposit": 3800,
        "decoration": "精装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "床", "衣柜", "沙发", "独立卫生间", "电梯", "暖气"],
        "status": "rented",
        "description": "【测试数据】首钢园冬奥片区全新公寓，工业风精装修设计。窗外即可看到首钢滑雪大跳台和冷却塔景观。园区配套完善，有书店、咖啡馆、展览空间等。临近地铁6号线金安桥站。",
    },
    {
        "title": "【测试数据】海淀区五道口 学区房 一居室 清华北大附近",
        "address": "北京市海淀区成府路五道口华清嘉园10号楼802",
        "district": "海淀区",
        "business_area": "五道口",
        "community": "华清嘉园",
        "layout": "1室1厅",
        "house_type": "普通住宅",
        "floor": 8,
        "total_floor": 16,
        "orientation": "南",
        "area": 45.0,
        "rent": 5800,
        "deposit": 5800,
        "decoration": "精装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "床", "衣柜", "沙发", "独立卫生间", "电梯", "暖气"],
        "status": "vacant",
        "description": "【测试数据】五道口核心地段学区房，紧邻清华大学和北京大学。精装修一居室，麻雀虽小五脏俱全。楼下就是地铁13号线五道口站，周边餐饮娱乐配套极其丰富。",
    },
    {
        "title": "【测试数据】朝阳区三里屯 高端服务式公寓 拎包入住",
        "address": "北京市朝阳区三里屯北路19号太古里公寓楼A座2601",
        "district": "朝阳区",
        "business_area": "三里屯",
        "community": "三里屯太古里公寓",
        "layout": "2室1厅",
        "house_type": "服务式公寓",
        "floor": 26,
        "total_floor": 32,
        "orientation": "西南",
        "area": 75.0,
        "rent": 12000,
        "deposit": 12000,
        "decoration": "豪华装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "电视", "床", "衣柜", "沙发", "餐桌", "独立卫生间", "阳台", "电梯", "暖气"],
        "status": "vacant",
        "description": "【测试数据】三里屯太古里楼上高端服务式公寓。全景落地窗俯瞰整个三里屯和CBD天际线。每周一次专业保洁，24小时前台和安保。楼下就是三里屯太古里商业区，使馆区近在咫尺。接受月租和长租。",
    },
    {
        "title": "【测试数据】房山区良乡大学城 学生合租 考研考公自习 配置齐全",
        "address": "北京市房山区良乡大学城学园北街11号院阳光邑上5号楼204",
        "district": "房山区",
        "business_area": "良乡大学城",
        "community": "阳光邑上",
        "layout": "2室1厅",
        "house_type": "合租",
        "floor": 2,
        "total_floor": 6,
        "orientation": "南",
        "area": 25.0,
        "rent": 1500,
        "deposit": 1500,
        "decoration": "简装修",
        "facilities": ["空调", "洗衣机", "热水器", "宽带", "床", "衣柜", "餐桌"],
        "status": "vacant",
        "description": "【测试数据】良乡大学城附近合租单间，紧邻北京理工大学良乡校区和北京工商大学。房间宽敞明亮，配置大书桌和台灯，非常适合考研、考公复习。室友都是在读研究生，氛围安静。",
    },
    {
        "title": "【测试数据】朝阳区CBD国贸 大开间 甲级写字楼旁 商住两用",
        "address": "北京市朝阳区建国路93号万达广场5号楼1808",
        "district": "朝阳区",
        "business_area": "CBD国贸",
        "community": "万达广场",
        "layout": "1室0厅",
        "house_type": "商住两用",
        "floor": 18,
        "total_floor": 30,
        "orientation": "东",
        "area": 42.0,
        "rent": 7000,
        "deposit": 7000,
        "decoration": "精装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "电视", "床", "衣柜", "沙发", "独立卫生间", "电梯"],
        "status": "vacant",
        "description": "【测试数据】CBD核心区商住两用大开间。正对国贸三期和中国尊，视野极佳。步行5分钟到大望路地铁站（1号线/14号线）。周边聚集了众多世界500强企业。适合CBD上班的白领，省去通勤烦恼。",
    },
    {
        "title": "【测试数据】朝阳区常营 经济适用型两居 地铁6号线 适合年轻夫妻",
        "address": "北京市朝阳区常营中路1号院保利嘉园8号楼1205",
        "district": "朝阳区",
        "business_area": "常营",
        "community": "保利嘉园",
        "layout": "2室1厅",
        "house_type": "普通住宅",
        "floor": 12,
        "total_floor": 28,
        "orientation": "南",
        "area": 78.0,
        "rent": 4500,
        "deposit": 4500,
        "decoration": "精装修",
        "facilities": ["空调", "冰箱", "洗衣机", "热水器", "宽带", "床", "衣柜", "沙发", "阳台", "燃气灶", "电梯", "暖气"],
        "status": "vacant",
        "description": "【测试数据】常营保利嘉园精装两居室，南北通透，中间楼层采光好。小区是保利开发的大型社区，绿化率高，有中心花园和儿童游乐区。楼下就是地铁6号线常营站和龙湖长楹天街购物中心。户型方正，特别适合新婚夫妻或小家庭。",
    },
]


def _write_default_house_image() -> str:
    """Create the default blank SVG used when a listing has no downloaded image."""
    upload_dir = os.path.join(app.static_folder, "uploads", "houses")
    os.makedirs(upload_dir, exist_ok=True)

    file_path = os.path.join(upload_dir, "default-house.svg")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="800" viewBox="0 0 1200 800">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#e6f3f1"/>
      <stop offset="100%" stop-color="#ffffff"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="800" fill="url(#bg)"/>
  <rect x="110" y="170" width="980" height="510" rx="34" fill="#ffffff" opacity="0.9"/>
  <path d="M250 555V365L600 205L950 365V555H780V420H620V555H250Z" fill="#0f766e" opacity="0.92"/>
  <path d="M200 375L600 185L1000 375" fill="none" stroke="#0f766e" stroke-width="42" stroke-linecap="round" stroke-linejoin="round"/>
  <rect x="338" y="420" width="116" height="96" rx="12" fill="#ffffff" opacity="0.88"/>
  <rect x="486" y="420" width="116" height="96" rx="12" fill="#ffffff" opacity="0.88"/>
  <rect x="760" y="420" width="116" height="96" rx="12" fill="#ffffff" opacity="0.88"/>
  <text x="600" y="650" text-anchor="middle" font-family="Arial, Microsoft YaHei, sans-serif" font-size="48" font-weight="700" fill="#1f2937">暂无图片</text>
</svg>
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return DEFAULT_HOUSE_IMAGE


def _download_demo_house_image(index: int) -> str:
    """Download a room photo for demo listings, falling back to the default SVG."""
    upload_dir = os.path.join(app.static_folder, "uploads", "houses")
    os.makedirs(upload_dir, exist_ok=True)

    filename = f"demo-house-{index + 1:02d}.jpg"
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return f"uploads/houses/{filename}"

    url = DEMO_IMAGE_URLS[index % len(DEMO_IMAGE_URLS)]
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "HouseRent demo seeder"})
        with urllib.request.urlopen(request, timeout=20) as response:
            content_type = response.headers.get("Content-Type", "")
            image_bytes = response.read()
        if not content_type.startswith("image/") or len(image_bytes) < 1024:
            raise ValueError(f"Unexpected response from {url}: {content_type}")
        with open(file_path, "wb") as f:
            f.write(image_bytes)
        print(f"Downloaded demo image: {filename}")
        return f"uploads/houses/{filename}"
    except (OSError, urllib.error.URLError, ValueError) as exc:
        print(f"Image download failed for listing {index + 1}: {exc}")
        return _write_default_house_image()


def main():
    with app.app_context():
        if db.engine.dialect.name == "mysql":
            db.session.execute(
                text(
                    "ALTER TABLE users MODIFY role "
                    "ENUM('tenant','landlord','admin','system_admin') "
                    "NOT NULL DEFAULT 'tenant'"
                )
            )
            db.session.commit()

        _write_default_house_image()

        system_admin = User.query.filter_by(role="system_admin").first()
        if not system_admin:
            system_admin = User.query.filter_by(username=SYSTEM_ADMIN_USERNAME).first()
            if not system_admin:
                system_admin = User(
                    username=SYSTEM_ADMIN_USERNAME,
                    email="system_admin@test.com",
                    phone="13800000000",
                    password_hash=generate_password_hash(SYSTEM_ADMIN_PASSWORD),
                    role="system_admin",
                    real_name="系统管理员",
                    status="active",
                )
                db.session.add(system_admin)
            else:
                system_admin.role = "system_admin"
                system_admin.status = "active"
            db.session.flush()
            print("Created system admin account")

        # Create test landlord
        landlord = User.query.filter_by(username="test_landlord").first()
        if not landlord:
            landlord = User(
                username="test_landlord",
                email="test_landlord@test.com",
                phone="13800000001",
                password_hash=generate_password_hash("123456"),
                role="landlord",
                real_name="测试房东",
                status="active",
            )
            db.session.add(landlord)
            db.session.flush()
            print("Created test landlord account")

        # Create test tenant for multi-user demo
        tenant = User.query.filter_by(username="test_tenant").first()
        if not tenant:
            tenant = User(
                username="test_tenant",
                email="test_tenant@test.com",
                phone="13800000002",
                password_hash=generate_password_hash("Password123"),
                role="tenant",
                real_name="测试租客",
                status="active",
            )
            db.session.add(tenant)
            db.session.flush()
            print("Created test tenant account")

        # Delete old test data
        test_house_ids = [
            house_id
            for (house_id,) in House.query
            .filter(House.title.like("%【测试数据】%"))
            .with_entities(House.id)
            .all()
        ]
        if test_house_ids:
            Contract.query.filter(
                (Contract.contract_no == DEMO_CONTRACT_NO)
                | (Contract.house_id.in_(test_house_ids))
            ).delete(synchronize_session=False)
            HouseImage.query.filter(HouseImage.house_id.in_(test_house_ids)).delete(
                synchronize_session=False
            )
            House.query.filter(House.id.in_(test_house_ids)).delete(
                synchronize_session=False
            )
        db.session.flush()

        # Insert test houses
        first_house = None
        for index, data in enumerate(TEST_HOUSES):
            if index == 0:
                data = {**data, "status": "rented"}
            house_data = {**data, "landlord_id": landlord.id}
            house = House(**house_data)
            db.session.add(house)
            db.session.flush()
            if first_house is None:
                first_house = house
            image_path = _download_demo_house_image(index)
            db.session.add(
                HouseImage(
                    house_id=house.id,
                    file_path=image_path,
                    caption="测试房源配图",
                    sort_order=0,
                    is_cover=True,
                )
            )

        if first_house:
            today = date.today()
            now = datetime.utcnow()
            db.session.add(
                Contract(
                    contract_no=DEMO_CONTRACT_NO,
                    house_id=first_house.id,
                    tenant_id=tenant.id,
                    landlord_id=landlord.id,
                    start_date=today,
                    end_date=today + timedelta(days=365),
                    monthly_rent=first_house.rent,
                    deposit=first_house.deposit,
                    status="active",
                    content="测试租客与测试房东的演示合同，用于报修和投诉流程。",
                    signed_by_landlord_at=now,
                    signed_by_tenant_at=now,
                )
            )

        db.session.commit()
        count = House.query.count()
        print(f"Inserted {len(TEST_HOUSES)} test houses. Total houses: {count}")
        print("Demo cover images are stored in app/static/uploads/houses")
        print()
        print("=" * 50)
        print("Test Account (房东)")
        print("  用户名: test_landlord")
        print("  密码:   123456")
        print("  角色:   landlord")
        print()
        print("Test Account (租客)")
        print("  用户名: test_tenant")
        print("  密码:   Password123")
        print("  角色:   tenant")
        print()
        print("Test Account (系统管理员)")
        print(f"  用户名: {SYSTEM_ADMIN_USERNAME}")
        print(f"  密码:   {SYSTEM_ADMIN_PASSWORD}")
        print("  角色:   system_admin")
        print("=" * 50)


if __name__ == "__main__":
    main()
