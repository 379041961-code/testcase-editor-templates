# 缺陷管理API参考文档

## 概述

该文档提供缺陷管理工作流所使用的核心API和集成接口参考。

## 认证

### 登录接口

获取API令牌进行后续认证。

**端点**: `POST /api/auth/login`

**请求体**:
```json
{
  "username": "your-username",
  "password": "your-password"
}
```

**响应**:
```json
{
  "token": "eyJ...",
  "expiresIn": 28800,
  "user": {
    "id": "user123",
    "name": "Your Name",
    "email": "your@email.com"
  }
}
```

**错误代码**:
- `401` - 认证失败（用户名或密码错误）
- `403` - 账户被禁用
- `429` - 请求过于频繁

**在请求头中使用Token**:
```
Authorization: Bearer {token}
Content-Type: application/json
```

## 缺陷管理接口

### 创建缺陷

**端点**: `POST /api/issues/create`

**请求体**:
```json
{
  "title": "缺陷标题",
  "environment": "测试",
  "projectId": "PROJ-001",
  "priority": "P1",
  "status": "新建",
  "expectedResult": "预期结果描述",
  "actualResult": "实际结果描述",
  "reproductionSteps": "重现步骤",
  "frequency": "100%稳定复现",
  "description": "详细描述（Markdown格式）"
}
```

**响应成功**:
```json
{
  "id": "PROJ-12345",
  "issueId": "PROJ-12345",
  "title": "缺陷标题",
  "createdAt": "2026-04-16T10:30:00Z",
  "createdBy": "user123",
  "url": "https://work.alibaba-inc.com/issues/PROJ-12345"
}
```

**错误代码**:
- `400` - 请求参数不完整或格式错误
- `401` - 认证失败
- `409` - 缺陷标题重复
- `500` - 服务器错误

### 获取缺陷详情

**端点**: `GET /api/issues/{issueId}`

**路径参数**:
- `issueId` - 缺陷ID（例：PROJ-12345）

**响应**:
```json
{
  "id": "PROJ-12345",
  "title": "缺陷标题",
  "environment": "测试",
  "priority": "P1",
  "status": "处理中",
  "assignee": {
    "id": "user456",
    "name": "张三",
    "email": "zhang.san@alibaba-inc.com"
  },
  "createdAt": "2026-04-16T10:30:00Z",
  "updatedAt": "2026-04-16T14:00:00Z",
  "expectedResult": "...",
  "actualResult": "...",
  "reproductionSteps": "..."
}
```

### 更新缺陷

**端点**: `PUT /api/issues/{issueId}`

**请求体** (所有字段可选):
```json
{
  "title": "新标题",
  "priority": "P2",
  "status": "处理中",
  "description": "更新的描述"
}
```

**响应**:
```json
{
  "id": "PROJ-12345",
  "updated": true,
  "message": "缺陷已更新"
}
```

### 搜索缺陷

**端点**: `GET /api/issues/search`

**查询参数**:
```
?title=keyword              # 按标题搜索
&status=处理中              # 按状态筛选
&priority=P1                # 按优先级筛选
&assignee=user@email.com    # 按指派人筛选
&projectId=PROJ-001         # 按项目筛选
&createdFrom=2026-04-01     # 创建时间范围（开始）
&createdTo=2026-04-30       # 创建时间范围（结束）
&page=1                     # 分页（默认1）
&pageSize=20                # 每页记录数（默认20）
```

**响应**:
```json
{
  "total": 150,
  "page": 1,
  "pageSize": 20,
  "items": [
    {
      "id": "PROJ-12345",
      "title": "...",
      "priority": "P1",
      "status": "处理中"
    }
  ]
}
```

## 指派接口

### 指派缺陷

**端点**: `POST /api/issues/{issueId}/assign`

**请求体**:
```json
{
  "assigneeEmail": "zhang.san@alibaba-inc.com",
  "comment": "指派原因或备注"
}
```

**响应**:
```json
{
  "id": "PROJ-12345",
  "assignee": {
    "email": "zhang.san@alibaba-inc.com",
    "name": "张三"
  },
  "assignedAt": "2026-04-16T10:35:00Z",
  "message": "缺陷已指派"
}
```

### 重新指派缺陷

**端点**: `POST /api/issues/{issueId}/reassign`

**请求体**:
```json
{
  "fromEmail": "old@email.com",
  "toEmail": "new@email.com",
  "reason": "重新指派原因"
}
```

## 附件接口

### 上传附件

**端点**: `POST /api/issues/{issueId}/attachments`

**请求类型**: `multipart/form-data`

**表单字段**:
- `file` - 文件内容
- `description` (可选) - 附件描述

**支持的文件类型**:
- 图片: jpg, png, gif, webp (最多10MB)
- 文档: pdf, txt, docx, xlsx (最多50MB)
- 归档: zip, rar (最多100MB)

**响应**:
```json
{
  "id": "attach123",
  "attachmentId": "attach123",
  "fileName": "screenshot.png",
  "size": 245632,
  "mimeType": "image/png",
  "url": "https://...",
  "uploadedAt": "2026-04-16T10:40:00Z"
}
```

**错误代码**:
- `413` - 文件过大
- `415` - 不支持的文件类型

### 列出附件

**端点**: `GET /api/issues/{issueId}/attachments`

**响应**:
```json
{
  "total": 2,
  "attachments": [
    {
      "id": "attach123",
      "fileName": "screenshot.png",
      "size": 245632,
      "uploadedAt": "2026-04-16T10:40:00Z",
      "uploadedBy": "user123"
    }
  ]
}
```

### 删除附件

**端点**: `DELETE /api/issues/{issueId}/attachments/{attachmentId}`

**响应**:
```json
{
  "deleted": true,
  "message": "附件已删除"
}
```

## 评论接口

### 添加评论

**端点**: `POST /api/issues/{issueId}/comments`

**请求体**:
```json
{
  "content": "评论内容（支持Markdown）",
  "mention": ["user456", "user789"]
}
```

**响应**:
```json
{
  "id": "comment123",
  "issueId": "PROJ-12345",
  "content": "...",
  "author": {
    "id": "user123",
    "name": "Your Name"
  },
  "createdAt": "2026-04-16T10:45:00Z"
}
```

### 更新评论

**端点**: `PUT /api/issues/{issueId}/comments/{commentId}`

**请求体**:
```json
{
  "content": "更新的评论内容"
}
```

### 删除评论

**端点**: `DELETE /api/issues/{issueId}/comments/{commentId}`

## 项目和成员接口

### 获取项目成员列表

**端点**: `GET /api/projects/{projectId}/members`

**查询参数**:
```
?role=developer    # 按角色筛选 (developer, qa, manager, admin)
&status=active     # 按状态筛选 (active, inactive)
&page=1            # 分页
```

**响应**:
```json
{
  "total": 25,
  "members": [
    {
      "id": "user456",
      "name": "张三",
      "email": "zhang.san@alibaba-inc.com",
      "role": "developer",
      "status": "active"
    }
  ]
}
```

### 获取项目信息

**端点**: `GET /api/projects/{projectId}`

**响应**:
```json
{
  "id": "PROJ-001",
  "name": "项目名称",
  "owner": "project-owner@email.com",
  "createdAt": "2026-01-01T00:00:00Z",
  "memberCount": 25
}
```

## 工作流状态接口

### 获取可用的状态转移

**端点**: `GET /api/issues/{issueId}/workflows`

**响应**:
```json
{
  "currentStatus": "处理中",
  "availableTransitions": [
    {
      "to": "已修复",
      "description": "标记为已修复"
    },
    {
      "to": "已拒绝",
      "description": "拒绝此缺陷"
    }
  ]
}
```

### 转移缺陷状态

**端点**: `POST /api/issues/{issueId}/transition`

**请求体**:
```json
{
  "to": "已修复",
  "comment": "状态转移备注"
}
```

**响应**:
```json
{
  "id": "PROJ-12345",
  "status": "已修复",
  "transitionedAt": "2026-04-16T15:00:00Z"
}
```

## 通知接口

### 获取通知

**端点**: `GET /api/notifications`

**查询参数**:
```
?unread=true       # 仅未读
&type=issue        # 通知类型
&page=1            # 分页
```

## 错误处理

### 标准错误响应格式

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "请求参数不合法",
    "details": {
      "field": "title",
      "reason": "标题不能为空"
    }
  }
}
```

### 常见错误码

| 代码 | HTTP状态 | 含义 |
|------|---------|------|
| UNAUTHORIZED | 401 | 未认证或认证失败 |
| FORBIDDEN | 403 | 无权限访问 |
| NOT_FOUND | 404 | 资源不存在 |
| INVALID_REQUEST | 400 | 请求参数不合法 |
| CONFLICT | 409 | 资源冲突 |
| RATE_LIMIT | 429 | 请求过于频繁 |
| SERVER_ERROR | 500 | 服务器内部错误 |

## 速率限制

- 标准账户: 1000请求/小时
- 高级账户: 10000请求/小时

响应头包含速率限制信息:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1713240000
```

## 分页

所有列表API均支持分页:

**查询参数**:
```
?page=1              # 页码（从1开始）
&pageSize=20         # 每页记录数（默认20，最大100）
&sortBy=createdAt    # 排序字段
&sortOrder=desc      # 排序方向 (asc/desc)
```

**响应**:
```json
{
  "page": 1,
  "pageSize": 20,
  "total": 1500,
  "totalPages": 75,
  "items": [...]
}
```

## 示例代码

### Python示例

```python
import requests

BASE_URL = "https://work.alibaba-inc.com/api"
USERNAME = "your-username"
PASSWORD = "your-password"

# 登录
response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": USERNAME,
    "password": PASSWORD
})
token = response.json()["token"]

headers = {"Authorization": f"Bearer {token}"}

# 创建缺陷
bug_data = {
    "title": "登录页面验证码显示错误",
    "environment": "测试",
    "projectId": "PROJ-001",
    "priority": "P1",
    "expectedResult": "显示清晰的验证码",
    "actualResult": "显示黑色方块"
}

response = requests.post(f"{BASE_URL}/issues/create", json=bug_data, headers=headers)
issue_id = response.json()["id"]

# 上传附件
with open("screenshot.png", "rb") as f:
    files = {"file": f}
    requests.post(f"{BASE_URL}/issues/{issue_id}/attachments", 
                  files=files, headers=headers)

# 指派缺陷
requests.post(f"{BASE_URL}/issues/{issue_id}/assign", json={
    "assigneeEmail": "zhang.san@alibaba-inc.com",
    "comment": "请处理此缺陷"
}, headers=headers)
```

### cURL示例

```bash
# 登录
curl -X POST "https://work.alibaba-inc.com/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# 创建缺陷
curl -X POST "https://work.alibaba-inc.com/api/issues/create" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"title":"Bug Title","environment":"测试"}'

# 上传附件
curl -X POST "https://work.alibaba-inc.com/api/issues/PROJ-12345/attachments" \
  -H "Authorization: Bearer {token}" \
  -F "file=@screenshot.png"
```
