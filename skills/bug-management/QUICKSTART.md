# 快速启动指南

## 5分钟快速开始

### 第1步：安装依赖（1分钟）

```bash
# 安装Selenium
pip install selenium

# 下载ChromeDriver (对应您的Chrome版本)
# https://chromedriver.chromium.org/
# 下载后放在项目根目录或添加到系统PATH

# 验证安装
chromedriver --version
python -c "import selenium; print(selenium.__version__)"
```

### 第2步：配置环境变量（1分钟）

**Windows PowerShell:**
```powershell
$env:CLOUD_EFFECT_USERNAME = "nick1821010462"
$env:CLOUD_EFFECT_PASSWORD = "R20250918"
```

**Windows CMD:**
```cmd
set CLOUD_EFFECT_USERNAME=nick1821010462
set CLOUD_EFFECT_PASSWORD=R20250918
```

**验证配置：**
```bash
echo %CLOUD_EFFECT_USERNAME%
echo %CLOUD_EFFECT_PASSWORD%
```

### 第3步：准备缺陷截图（1分钟）

- 获取问题现象的截图
- 保存到本地，记住路径（如 `C:\Users\Desktop\bug_screenshot.png`）

### 第4步：调用SKILL并填写信息（2分钟）

**在VS Code中：**
1. 打开Copilot Chat
2. 输入：`/bug-management`
3. 按照提示填写：
   - BUG标题
   - 预期结果
   - 实际结果
   - 截图路径
   - 项目名称（如 IOT平台2.0）
   - **负责人（邮箱或姓名）** - 可输入 `liu.ting@alibaba-inc.com` 或 `刘庭`

**或通过命令行：**
```bash
cd skills/bug-management/scripts
python bug_management_web_workflow.py
```

## 常见项目名称

| 项目 | 名称（精确拼写） |
|------|-----------------|
| IOT平台 | IOT平台2.0 |
| C-smart | C-smart 6.0 |
| 幸福工作 | 幸福工作3.0 |
| CSMART | CSMART5.0 |

## 常见用户邮箱

| 姓名 | 邮箱 |
|------|------|
| 刘庭 | liu.ting@alibaba-inc.com |
| 刘西 | liu.xi@alibaba-inc.com |
| 李莎 | li.sha@alibaba-inc.com |
| 欧琳华 | ou.linhua@alibaba-inc.com |

## 验证成功标志

✓ 当看到以下输出时，说明提交成功：

```
✓ 登录成功
✓ 已进入项目缺陷页面
✓ 缺陷创建成功
✓ 已指派给: user@alibaba-inc.com
✓ 所有操作截图已保存到: ./bug-submission-screenshots/
```

## 如果出错了

1. **查看生成的截图** 
   - 打开 `./bug-submission-screenshots/` 目录
   - 查看带有 `error`、`timeout` 或 `failed` 的截图
   - 这些截图会显示出错时的页面状态

2. **检查常见问题**
   - ChromeDriver版本不匹配：运行 `chromedriver --version`
   - 环境变量未设置：重新设置并重启PowerShell
   - 网络连接问题：使用有线网络，关闭VPN

3. **手动测试**
   - 在浏览器中手动完成一遍流程
   - 这样可以帮您理解步骤并发现问题

## 下一步

- 了解更多：查看 [完整文档](../SKILL.md)
- 最佳实践：阅读 [缺陷管理最佳实践](../references/bugs_best_practices.md)
- 常见问题：查阅 [FAQ](../references/faq.md)

## 需要帮助？

1. 查看本指南中的"如果出错了"部分
2. 查看生成的错误截图
3. 检查 [FAQ](../references/faq.md) 中的常见问题
4. 阅读脚本中的注释理解工作流程
