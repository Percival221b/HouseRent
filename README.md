# HouseRent

基于 Flask + MySQL 的智能房屋租赁系统课程项目。

## 技术栈

- Python 3.10+
- Flask
- MySQL
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-WTF

## 本地启动

1. 创建虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate
```

2. 安装依赖

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

3. 创建配置

```bash
cp .env.example .env
```

然后修改 `.env` 中的数据库连接。

4. 初始化数据库

```bash
flask db init
flask db migrate -m "init database"
flask db upgrade
```

5. 启动项目

```bash
flask run
```

## 项目结构

```text
HouseRent/
├── app/
│   ├── models/          # 数据模型
│   ├── routes/          # 蓝图和路由
│   ├── static/          # CSS、JS、上传文件
│   ├── templates/       # Jinja2 页面模板
│   ├── __init__.py      # Flask 应用工厂
│   ├── config.py        # 配置类
│   └── extensions.py    # Flask 扩展实例
├── database/            # SQL 脚本和数据库说明
├── docs/                # 项目文档
├── migrations/          # 数据库迁移目录
├── scripts/             # 管理脚本
├── tests/               # 测试用例
├── requirements.txt
├── requirements-dev.txt
├── run.py
└── wsgi.py
```

## 小组模块建议

- A：项目架构、数据库设计、集成、部署
- B：用户注册登录、权限、个人中心
- C：房源发布、图片上传、搜索、详情
- D：预约、合同、支付、维修、投诉
- E：页面、后台、新闻、报表、测试文档

