# 缺陷管理自动化工具

## 概述

这是一个集成阿里云效系统的**自动化缺陷管理工具**，可以帮助您快速、规范地提交BUG到云效系统。

该工具使用Selenium实现Web自动化，可以自动完成：
- ✅ 登录云效系统
- ✅ 导航到指定项目
- ✅ 创建缺陷并填写表单
- ✅ 上传问题截图
- ✅ 自动指派给负责人
- ✅ 保存所有过程的截图用于追踪

## 核心特性

| 功能 | 说明 |
|------|------|
| **自动登录** | 使用环境变量中的凭证自动登录阿里云效 |
| **智能表单填写** | 自动识别并填写缺陷表单字段 |
| **截图上传** | 自动上传用户提供的问题截图 |
| **自动指派** | 根据邮箱自动指派给指定负责人 |
| **过程记录** | 保存所有关键步骤的截图用于追踪 |
| **错误处理** | 遇到错误时自动保存错误截图 |

## 文件结构

```
bug-management/
├── SKILL.md                    # 完整功能说明文档
├── QUICKSTART.md               # 5分钟快速启动指南 ⭐ 从这里开始
├── README.md                   # 本文件
├── .bug-management-config.json # 配置文件模板
├── scripts/
│   ├── aliyun_bug_automation.py           # 核心Selenium自动化模块
│   ├── bug_management_web_workflow.py     # 主协调程序
│   ├── validation.py                      # 缺陷信息验证
│   ├── cloud_effect_login.py              # 旧版登录模块（可选）
│   ├── bug_submission.py                  # 旧版缺陷提交（可选）
│   ├── file_upload.py                     # 旧版文件上传（可选）
│   ├── bug_assignment.py                  # 旧版指派模块（可选）
│   └── bug_management_workflow.py         # 旧版主程序（可选）
├── references/
│   ├── bugs_best_practices.md     # 缺陷管理最佳实践
│   ├── api_reference.md           # API参考文档
│   └── faq.md                     # 常见问题解答
└── bug-submission-screenshots/   # 运行脚本时自动生成的截图目录
```

## 快速开始

### 1️⃣ 安装依赖

```bash
pip install selenium
# 下载ChromeDriver: https://chromedriver.chromium.org/
```

### 2️⃣ 配置环境变量

```bash
set CLOUD_EFFECT_USERNAME=nick1821010462
set CLOUD_EFFECT_PASSWORD=R20250918
# 设置环境变量，在终端输入
$env:CLOUD_EFFECT_USERNAME = "nick1821010462"
$env:CLOUD_EFFECT_PASSWORD = "R20250918"
```

### 3️⃣ 调用SKILL

在VS Code Copilot Chat中输入：
```
/bug-management
```

### 4️⃣ 填写交互式表单

按照提示输入：
- BUG标题
- 预期结果
- 实际结果
- 截图路径
- 项目名称
- 负责人邮箱

**完整示例：**
```
BUG标题: 用户列表页面加载缓慢
预期结果: 页面应在3秒内加载完成
实际结果: 页面需要30秒才能加载
截图路径: C:\Users\Desktop\bug.png
项目名称: IOT平台2.0
负责人: liu.ting@alibaba-inc.com 或 刘庭
```

## 使用方式

### 方式1: 通过Copilot（推荐）⭐

在VS Code Copilot Chat中：
```
/bug-management
```

### 方式2: 命令行

```bash
cd skills/bug-management/scripts
python bug_management_web_workflow.py
```

### 方式3: 直接导入

```python
from aliyun_bug_automation import AliyunCloudEffectAutomation

automation = AliyunCloudEffectAutomation("username", "password")
automation.start_driver()
automation.login()
automation.navigate_to_bug_section("IOT平台2.0")
automation.create_bug({
    'title': 'Bug Title',
    'expected_result': '...',
    'actual_result': '...',
    'attachment_path': '/path/to/screenshot.png'
})
automation.assign_bug("user@email.com")
automation.close_driver()
```

## 配置说明

### 环境变量

| 变量 | 说明 | 必需 |
|------|------|------|
| `CLOUD_EFFECT_USERNAME` | 阿里云账号 | ✅ |
| `CLOUD_EFFECT_PASSWORD` | 阿里云密码 | ✅ |

### 配置文件 (.bug-management-config.json)

```json
{
  "cloudEffect": {
    "baseUrl": "https://devops.aliyun.com",
    "projects": {
      "iot": "IOT平台2.0",
      "csmart": "C-smart 6.0"
    }
  },
  "automation": {
    "browser": "chrome",
    "headless": false,
    "timeout": 15,
    "screenshot_dir": "./bug-submission-screenshots"
  }
}
```

## 示例项目列表

常见的云效项目名称（精确拼写）：

- `IOT平台2.0`
- `C-smart 6.0`
- `幸福工作3.0`
- `CSMART5.0`

## 常见用户

常见的云效用户邮箱：

- liu.ting@alibaba-inc.com
- liu.xi@alibaba-inc.com
- li.sha@alibaba-inc.com
- ou.linhua@alibaba-inc.com

## 执行结果

运行成功时，您会看到：

```
【第一步】验证缺陷信息
✓ 信息验证通过

【第二步】启动自动化工具
【第三步】启动浏览器
✓ 浏览器已启动

【第四步】登录阿里云效系统
✓ 登录成功

【第五步】导航到项目缺陷页面: IOT平台2.0
✓ 已进入项目缺陷页面

【第六步】创建缺陷
✓ 缺陷创建成功

【第七步】为缺陷指派负责人
✓ 已指派给: liu.ting@alibaba-inc.com

【完成】缺陷管理工作流已完成
✓ 缺陷提交成功！
```

所有过程的截图将保存到 `./bug-submission-screenshots/` 目录。

## 常见问题

### Q: 如何快速开始？
**A:** 查看 [快速启动指南](./QUICKSTART.md) ⭐

### Q: ChromeDriver怎样安装？
**A:** 
1. 查看Chrome版本 (打开 chrome://version)
2. 从 https://chromedriver.chromium.org/ 下载对应版本
3. 将 chromedriver.exe 放在项目根目录或系统PATH中

### Q: 脚本运行出错怎么办？
**A:** 
1. 查看 `./bug-submission-screenshots/` 中的错误截图
2. 查看 [常见问题](./references/faq.md)
3. 尝试手动操作一遍了解流程

### Q: 如何查看完整文档？
**A:** 查看 [SKILL.md](./SKILL.md) 中的详细说明

### Q: 支持哪些项目？
**A:** 支持所有云效中的项目，常见的有 IOT平台2.0, C-smart 6.0 等

## 文档导航

- 📖 [完整功能说明](./SKILL.md)
- 🚀 [5分钟快速开始 ⭐](./QUICKSTART.md)
- 📋 [缺陷管理最佳实践](./references/bugs_best_practices.md)
- ❓ [常见问题解答](./references/faq.md)

## 技术栈

- **Python 3.6+**
- **Selenium 3.x/4.x** - Web自动化
- **Chrome/Chromium** - 浏览器
- **ChromeDriver** - 浏览器驱动

## 工作流程图

```
┌────────────────────────────────────────────────────┐
│ 用户在Copilot Chat中输入 /bug-management          │
└────────────────────┬───────────────────────────────┘
                     │
        ┌────────────▼──────────────┐
        │ 交互式提示输入缺陷信息      │
        │ - 标题                    │
        │ - 预期结果                │
        │ - 实际结果                │
        │ - 截图路径               │
        │ - 项目名称                │
        │ - 负责人邮箱              │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │ 验证缺陷信息               │
        │ (validation.py)           │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────────────────────┐
        │ 启动Selenium自动化脚本                     │
        │ (aliyun_bug_automation.py)               │
        │ ✓ 启动浏览器                             │
        │ ✓ 登录系统                               │
        │ ✓ 导航到项目                             │
        │ ✓ 创建缺陷、填表、上传截图               │
        │ ✓ 指派负责人                             │
        │ ✓ 保存截图                              │
        └────────────┬──────────────────────────────┘
                     │
        ┌────────────▼──────────────┐
        │ 输出完成报告               │
        │ 显示缺陷链接和处理结果      │
        └────────────┬──────────────┘
                     │
        ┌────────────▼──────────────┐
        │ 截图已保存                 │
        │ ./bug-submission-screenshots/
        └────────────────────────────┘
```

## 故障排除

如果遇到问题：

1. **查看保存的截图** - 位于 `./bug-submission-screenshots/`
2. **检查错误日志** - 控制台输出会显示具体错误
3. **查阅FAQ** - 见 [常见问题](./references/faq.md)
4. **手动测试** - 在浏览器中手动完成一遍流程

## 提示和建议

✅ **做这些：**
- 使用有线网络，提高稳定性
- 提供清晰的问题截图
- 使用准确的项目名称和邮箱
- 定期查看执行结果

❌ **避免这些：**
- 同时提交大量缺陷
- 在系统繁忙时段提交
- 输入不准确的项目名称
- 使用很大的截图文件

## 更新日志

### v2.0 (2026-04-16) ⭐ 当前版本
- ✨ 完全重写，使用Selenium Web自动化
- 支持Web界面自动操作
- 自动截图保存所有步骤
- 改进的错误处理和反馈
- 新增快速启动指南

### v1.0 (2026-04-15)
- 初始版本
- 使用API的纯Python实现

## 许可证

内部使用工具，仅限阿里集团内部人员使用。

## 联系方式

如有问题或改进建议，请联系项目维护者。

---

**🚀 立即开始：** 查看 [快速启动指南](./QUICKSTART.md)

**📖 了解更多：** 查看 [完整文档](./SKILL.md)
