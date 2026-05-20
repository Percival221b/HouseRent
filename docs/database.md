# 数据库设计说明

本项目使用 MySQL 作为主数据库，Flask 后端通过 Flask-SQLAlchemy 访问数据库。统一数据库名为 `house_rent`。

## 初始化方式

先确认 MySQL 服务已启动，然后执行：

```bash
mysql -u root -p < database/schema.sql
```

执行后会自动创建数据库 `house_rent` 以及项目所需的数据表。

然后在 `.env` 中配置数据库连接：

```text
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/house_rent?charset=utf8mb4
```

如果使用 Flask-Migrate，则以 `app/models/` 中的 SQLAlchemy 模型为准：

```bash
flask db init
flask db migrate -m "init database"
flask db upgrade
```

## 表结构总览

| 表名 | 负责人建议 | 用途 |
|---|---|---|
| `users` | B | 用户、角色、登录认证、个人资料 |
| `houses` | C | 房源基础信息、搜索字段、出租状态 |
| `house_images` | C | 房源图片 |
| `appointments` | D | 租客预约看房、房东审核 |
| `messages` | D/E | 租客与房东留言、自动回复 |
| `contracts` | D | 电子租赁合同 |
| `payments` | D | 租金、押金、模拟支付记录 |
| `repair_requests` | D | 维修申请 |
| `complaints` | D/E | 投诉处理 |
| `news` | E | 房东或管理员发布租赁/维修通知 |
| `system_logs` | A/E | 登录、操作、后台监控日志 |

## 关键字段约定

### users

- `role`：`tenant` 租客，`landlord` 房东，`admin` 管理员。
- `status`：`active` 正常，`disabled` 禁用，`pending` 待审核。
- `password_hash`：只保存加密后的密码，不保存明文密码。
- `two_factor_enabled`：是否开启模拟双因素认证。

### houses

- `landlord_id`：关联 `users.id`，表示发布房源的房东。
- `district`：区域，用于“按地区搜索”。
- `business_area`：商圈，用于扩展搜索。
- `layout`：户型，例如 `2室1厅`，用于“按户型搜索”。
- `facilities`：JSON 字段，可保存 `["空调", "冰箱", "洗衣机"]`。
- `status`：`vacant` 空置，`rented` 已出租，`maintenance` 维修中，`offline` 下架。

### appointments

- `status`：`pending` 待确认，`approved` 已同意，`rejected` 已拒绝，`cancelled` 已取消，`completed` 已完成。
- `remark`：租客预约备注。
- `reply`：房东回复。

### messages

- `message_type`：`text` 普通留言，`system` 系统消息，`auto_reply` 智能代理自动回复。
- `is_read` 和 `read_at`：用于消息已读状态。

### contracts

- `contract_no`：合同编号，必须唯一。
- `status`：`draft` 草稿，`pending_signed` 待签署，`active` 生效中，`ended` 已结束，`cancelled` 已取消。
- `signed_by_landlord_at`、`signed_by_tenant_at`：双方签署时间。

### payments

- `payment_type`：`rent` 租金，`deposit` 押金，`other` 其他。
- `payment_method`：`mock` 模拟支付，`cash` 现金，`alipay` 支付宝，`wechat` 微信，`bank_card` 银行卡。
- `status`：`pending` 待支付，`paid` 已支付，`overdue` 逾期，`refunded` 已退款，`cancelled` 已取消。

### repair_requests

- `handler_id`：处理人，可以是房东或管理员。
- `status`：`pending` 待处理，`processing` 处理中，`finished` 已完成，`rejected` 已拒绝。
- `result`：处理结果。

### complaints

- `target_user_id`：被投诉用户，可以为空。
- `handler_id`：管理员处理人。
- `status`：`pending` 待处理，`processing` 处理中，`resolved` 已解决，`rejected` 已驳回。

### news

- `author_id`：发布者，通常为房东或管理员。
- `category`：新闻分类，例如 `租赁通知`、`维修通知`、`系统公告`。
- `is_published`：是否发布。

### system_logs

- `action`：操作名称，例如 `login`、`create_house`、`pay_rent`。
- `method`、`path`、`ip_address`、`user_agent`：用于系统监控和问题排查。

## 开发约定

1. 后端代码统一使用 `app/models/` 中的模型类，不要在路由中手写表名。
2. 新增字段时，先修改 SQLAlchemy 模型，再同步修改 `database/schema.sql` 和本说明文档。
3. 金额字段统一使用 `DECIMAL(10, 2)`，不要使用浮点数保存金额。
4. 图片和视频只在数据库保存相对路径或 URL，文件本体放在 `app/static/uploads/`。
5. 删除用户时不建议物理删除，优先把 `users.status` 改为 `disabled`。
6. 报表统计不单独建表，优先通过 `houses`、`contracts`、`payments`、`system_logs` 查询统计。

