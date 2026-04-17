---
name: bug-management
description: '自动化缺陷管理工作流。根据BUG标题、图片、预期结果、负责人信息，自动登录阿里云效系统，提交BUG并指派给相应负责人。适用于快速批量提交测试缺陷。'
argument-hint: '输入BUG标题 | 图片路径 | 预期结果 | 负责人邮箱'
user-invocable: true
---

# 缺陷管理自动化工作流

## 功能概述

该工作流使用Selenium自动化操作阿里云效BUG系统Web界面，实现以下自动化操作：
- **Web自动登录**：自动登录阿里云效系统Web界面
- **自动导航**：自动找到项目、选择缺陷模块
- **表单填写**：自动填写缺陷标题、预期结果、实际结果
- **截图上传**：自动上传用户提供的问题截图
- **自动指派**：自动将缺陷指派给指定负责人
- **截图保存**：提交完成后截图保存，方便追踪

## 何时使用

- 需要快速提交测试缺陷到阿里云效系统（Web界面）
- 在本地自动化测试中提交发现的问题
- 需要规范化的缺陷记录、填写和指派流程
- 希望自动保存提交结果截图用于追踪

## 使用方式

### 1. 环境准备

#### 安装必需组件

```bash
# 安装Python依赖
pip install selenium

# 安装ChromeDriver
# 从 https://chromedriver.chromium.org/ 下载对应版本
# 或使用包管理器：
# Windows: choco install chromedriver
# Mac: brew install chromedriver
# Linux: apt-get install chromium-chromedriver
```

#### 配置环境变量

```bash
# Windows PowerShell
$env:CLOUD_EFFECT_USERNAME = "nick1821010462"
$env:CLOUD_EFFECT_PASSWORD = "R20250918"

# Windows CMD
set CLOUD_EFFECT_USERNAME=nick1821010462
set CLOUD_EFFECT_PASSWORD=R20250918

# Linux/Mac
export CLOUD_EFFECT_USERNAME=nick1821010462
export CLOUD_EFFECT_PASSWORD=R20250918
```

### 2. 调用工作流

在VS Code Copilot Chat中使用以下命令：

```
/bug-management
```

### 3. 交互式输入信息

系统将提示您输入以下信息（\* 表示必需，○ 表示可选）：

| 信息项 | 必需 | 说明 |
|--------|------|------|
| \* BUG标题 | ✅ | 缺陷的简明标题，建议40字以内 |
| \* 预期结果 | ✅ | 功能应该表现的正确行为 |
| \* 实际结果 | ✅ | 当前观察到的错误行为 |
| \* 项目名称 | ✅ | 如 IOT平台2.0, C-smart 6.0 等 |
| 环境 | ○ | 测试环境，默认为"测试"（可选） |
| 重现步骤 | ○ | 问题重现的详细步骤（可选） |
| BUG截图 | ○ | 问题现象的本地文件路径（可选） |
| 负责人 | ○ | 邮箱或姓名，如 liu.ting@alibaba-inc.com 或 刘庭（可选）|

### 4. 自动执行流程

工作流将按照以下步骤自动执行：

1. **信息验证** - 验证输入的必需字段是否完整
2. **启动浏览器** - 启动Chrome浏览器驱动
3. **系统登录** - 使用环境变量中的凭证自动登录
4. **导航到项目** - 自动导航到指定项目的缺陷页面
5. **创建缺陷** - 自动填写缺陷表单并上传截图
6. **指派负责人** - 自动将缺陷指派给指定负责人
7. **保存截图** - 整个过程的关键步骤将被截图保存

## 配置要求

### 云效系统凭证

需要在系统中配置环境变量：

```bash
# Windows PowerShell 或 CMD
set CLOUD_EFFECT_USERNAME=nick1821010462
set CLOUD_EFFECT_PASSWORD=R20250918
```

**获取账号密码**：
- 这是您的阿里云账号
- 确保账号有权限在阿里云效系统中创建缺陷

### 浏览器驱动配置

需要安装ChromeDriver以支持Selenium自动化：

1. **下载ChromeDriver**
   - 访问: https://chromedriver.chromium.org/
   - 选择与您的Chrome浏览器版本匹配的驱动
   - 下载后将其放在系统PATH中

2. **验证安装**
   ```bash
   chromedriver --version
   ```

3. **安装Selenium**
   ```bash
   pip install selenium
   ```

### 项目配置文件

在项目根目录创建 `.bug-management-config.json`：

```json
{
  "cloudEffect": {
    "baseUrl": "https://devops.aliyun.com",
    "projects": {
      "iot": "IOT平台2.0",
      "csmart": "C-smart 6.0",
      "work": "幸福工作3.0",
      "csmart5": "CSMART5.0"
    }
  },
  "automation": {
    "browser": "chrome",
    "headless": false,
    "timeout": 15,
    "screenshot_dir": "./bug-submission-screenshots"
  }
}
}
```

## 执行流程示例

### 示例：提交一个IOT平台的BUG

**输入提示：**
```
BUG标题: 用户列表页面加载缓慢
预期结果: 页面应在3秒内加载完成
实际结果: 页面需要30秒才能完全加载
截图路径: C:\Users\Desktop\iot_slow_loading.png
项目名称: IOT平台2.0
负责人: liu.ting@alibaba-inc.com 或 刘庭
```

**自动执行流程：**
```
【第一步】验证缺陷信息
========================================
✓ 信息验证通过

【第二步】启动自动化工具
========================================

【第三步】启动浏览器
========================================
✓ 浏览器已启动

【第四步】登录阿里云效系统
========================================
✓ 正在登录阿里云效系统...
✓ 已打开登录页面
✓ 输入用户名: nick1821010462
✓ 输入密码
✓ 点击登录按钮
✓ 登录成功
✓ 截图已保存: ./bug-submission-screenshots/bug_login_success_20260416_143022.png

【第五步】导航到项目缺陷页面: IOT平台2.0
========================================
✓ 已点击项目协作菜单
✓ 已点击'我参与的'
✓ 已进入项目: IOT平台2.0
✓ 已进入缺陷模块
✓ 截图已保存: ./bug-submission-screenshots/bug_bug_section_20260416_143025.png

【第六步】创建缺陷
========================================
✓ 已点击新建按钮
✓ 已填写标题: 用户列表页面加载缓慢
✓ 已填写预期结果
✓ 已填写实际结果
✓ 已上传附件: C:\Users\Desktop\iot_slow_loading.png
✓ 已点击新建按钮提交
✓ 截图已保存: ./bug-submission-screenshots/bug_bug_created_20260416_143030.png

【第七步】为缺陷指派负责人
========================================
✓ 已点击负责人输入框
✓ 已输入负责人邮箱: liu.ting@alibaba-inc.com
✓ 已选择负责人: liu.ting@alibaba-inc.com
✓ 截图已保存: ./bug-submission-screenshots/bug_bug_assigned_20260416_143035.png

【完成】缺陷管理工作流已完成
========================================

✓ 缺陷提交成功！

【缺陷信息摘要】
  标题:         用户列表页面加载缓慢
  预期结果:     页面应在3秒内加载完成
  实际结果:     页面需要30秒才能完全加载
  项目:         IOT平台2.0
  负责人:       liu.ting@alibaba-inc.com (刘庭)

【截图信息】
  所有操作截图已保存到: ./bug-submission-screenshots/
```

## 脚本参考

工作流使用以下脚本完成操作：

- [Web自动化脚本](./scripts/aliyun_bug_automation.py) - 核心Selenium自动化逻辑
- [主协调程序](./scripts/bug_management_web_workflow.py) - 工作流协调和交互式提示
- [数据验证脚本](./scripts/validation.py) - 输入信息验证

## 运行方式

### 方式1: 通过Copilot调用（推荐）

在VS Code Copilot Chat中：
```
/bug-management
```

### 方式2: 命令行直接运行

```bash
cd skills/bug-management/scripts
python bug_management_web_workflow.py
```

### 方式3: 导入为模块使用

```python
from aliyun_bug_automation import AliyunCloudEffectAutomation

automation = AliyunCloudEffectAutomation("username", "password")
automation.start_driver()
automation.login()
automation.navigate_to_bug_section("IOT平台2.0")
automation.create_bug({...})
automation.assign_bug("user@email.com")
automation.close_driver()
```

## 故障排除

### 问题：ChromeDriver未找到或版本不匹配

**可能原因：**
- 未安装ChromeDriver
- ChromeDriver版本与Chrome浏览器不匹配
- ChromeDriver不在系统PATH中

**解决方案：**
1. 检查Chrome浏览器版本 (打开chrome://version)
2. 从 https://chromedriver.chromium.org/ 下载对应版本
3. 将chromedriver.exe放在系统PATH中或项目根目录
4. 运行: `chromedriver --version` 验证安装

### 问题：登录失败

**可能原因：**
- 用户名或密码错误
- 环境变量设置不正确
- 账户被锁定或禁用
- 网络连接问题

**解决方案：**
1. 验证环境变量设置: `echo %CLOUD_EFFECT_USERNAME%`
2. 确认用户名密码正确
3. 在浏览器中手动测试登录
4. 检查网络连接

### 问题：无法导航到项目

**可能原因：**
- 输入的项目名称不正确
- 项目名称中有特殊字符
- 账户无权限访问该项目
- 页面加载缓慢

**解决方案：**
1. 检查项目名称拼写（例如 "IOT平台2.0"）
2. 在云效系统中核实账户是否已加入项目
3. 增加超时时间 (在config中修改 timeout 值)
4. 查看保存的截图了解具体情况

### 问题：缺陷创建失败

**可能原因：**
- 表单字段找不到
- 必填字段缺少必需值
- 截图上传失败
- 页面元素加载缓慢

**解决方案：**
1. 查看保存的截图确认页面状态
2. 确保必填信息（标题、预期结果、实际结果）都已填写
3. 检查截图文件路径是否正确
4. 尝试手动创建一个缺陷以了解流程

### 问题：指派失败

**可能原因：**
- 邮箱格式不正确
- 用户不在项目成员列表中
- 指派人无权限
- 页面元素查找超时

**解决方案：**
1. 确认邮箱格式正确（例如 user@alibaba-inc.com）
2. 在云效系统中验证该成员已加入项目
3. 查看截图验证是否找到了负责人字段
4. 手动指派一次以了解流程

### 问题：无法上传截图

**可能原因：**
- 文件路径不存在
- 文件路径包含中文或特殊字符
- 文件太大
- 云效系统不支持该文件格式

**解决方案：**
1. 验证文件路径存在: `Test-Path "path\to\file.png"`
2. 使用绝对路径而不是相对路径
3. 避免路径中包含特殊字符
4. 确保文件大小合理（不超过50MB）
5. 支持的格式：jpg, png, gif, pdf 等

### 问题：浏览器窗口未自动关闭

**可能原因：**
- 脚本中途出错
- 用户中断执行
- 浏览器驱动未正确关闭

**解决方案：**
1. 手动关闭浏览器窗口
2. 运行: `taskkill /IM chromedriver.exe /F` 关闭所有chromedriver进程
3. 重启Python脚本

### 问题：截图保存失败

**可能原因：**
- 目录权限不足
- 磁盘空间不足
- 路径包含非法字符

**解决方案：**
1. 检查 ./bug-submission-screenshots 目录权限
2. 确保磁盘有足够空间
3. 运行PowerShell时以管理员身份运行

## 高级用法

### 自定义浏览器选项

编辑 [aliyun_bug_automation.py](./scripts/aliyun_bug_automation.py) 中的 `start_driver()` 方法：

```python
# 启用无头模式（不显示浏览器窗口）
options.add_argument('--headless')

# 设置窗口大小
options.add_argument('--window-size=1920,1080')

# 禁用图片加载（加快速度）
options.add_argument('--blink-settings=imagesEnabled=false')
```

### 扩展自动化流程

创建子类扩展功能：

```python
from aliyun_bug_automation import AliyunCloudEffectAutomation

class CustomBugAutomation(AliyunCloudEffectAutomation):
    def custom_workflow(self):
        """自定义工作流"""
        self.start_driver()
        self.login()
        # ... 添加自定义逻辑
        self.close_driver()
```

### 集成到CI/CD

在Jenkins或GitLab CI中集成自动化缺陷提交：

```yaml
# .gitlab-ci.yml 示例
submit_bug:
  stage: test
  script:
    - pip install selenium
    - python scripts/bug_management_web_workflow.py
  environment: production
  only:
    - tags
```

### 批量提交缺陷

创建脚本处理多个缺陷：

```python
bugs_list = [
    {
        'title': 'Bug 1',
        'expected_result': '...',
        'actual_result': '...',
        'attachment_path': '/path/to/img1.png',
        'project_name': 'IOT平台2.0'
    },
    # ... 更多缺陷
]

for bug in bugs_list:
    workflow = BugManagementWorkflow()
    workflow.submit_bug(bug, assignee_email)
    time.sleep(5)  # 等待处理
```

## 最佳实践

### 关于自动化脚本

1. **定期检查截图** - 自动化过程中所有关键步骤都会被截图，便于调试
2. **验证缺陷信息** - 提交前脚本会自动验证所有必需字段
3. **合理设置超时** - 根据网络情况调整超时时间
4. **避免并发提交** - 避免同时提交多个缺陷，容易导致冲突
5. **定期更新ChromeDriver** - 保持与Chrome浏览器版本同步

### 关于缺陷信息

1. **标题准确** - 准确、清晰、简洁的标题有助于快速定位问题
2. **详细的预期结果** - 清楚地说明正确行为应该是什么
3. **清晰的实际结果** - 明确描述当前的错误表现
4. **高质量的截图** - 清晰的截图能显著提升解决效率
5. **正确的项目名称** - 确保将缺陷提交到正确的项目

### 关于负责人指派

1. **准确的邮箱** - 确保邮箱格式正确（user@alibaba-inc.com）
2. **验证成员** - 确认该成员已加入目标项目
3. **及时指派** - 创建缺陷后立即指派，便于快速响应
4. **保存截图** - 保留指派成功的截图作为证明

### 关于流程监控

1. **查看保存的截图** - 位于 `./bug-submission-screenshots/` 目录
2. **检查错误日志** - 如果脚本失败，查看对应的错误截图
3. **手动验证** - 提交完成后登录云效系统手动验证缺陷信息

### 系统优化建议

1. **使用有线网络** - 比WiFi更稳定，减少超时风险
2. **关闭VPN** - 某些VPN可能导致页面加载缓慢
3. **避免高峰期** - 在系统较空闲时提交，提高成功率
4. **预先登录** - 如果首次使用，可先在浏览器中手动登录一次

## 相关资源

### 官方文档
- [阿里云效系统账户登录](https://account.aliyun.com/login/login.htm)
- [Selenium Python文档](https://selenium-python.readthedocs.io/)
- [ChromeDriver下载](https://chromedriver.chromium.org/)

### 最佳实践指南
- [缺陷管理最佳实践指南](./references/bugs_best_practices.md) - 如何提交高质量缺陷
- [常见问题解答](./references/faq.md) - 常见问题和解决方案

### 脚本文件
- [Web自动化主模块](./scripts/aliyun_bug_automation.py) - 核心自动化实现
- [工作流协调程序](./scripts/bug_management_web_workflow.py) - 完整工作流
- [数据验证模块](./scripts/validation.py) - 输入验证

## 支持和反馈

如有问题或建议，请：

1. **查看保存的截图** - 在 `./bug-submission-screenshots/` 中找到问题步骤的截图
2. **查阅FAQ** - 在 [常见问题解答](./references/faq.md) 中查找解决方案
3. **手动测试** - 在浏览器中手动操作一遍，了解正确的流程
4. **检查日志** - 运行脚本时仔细查看控制台输出的错误信息
