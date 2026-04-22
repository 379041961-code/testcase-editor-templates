# IOT 2.0 设备统计 UI 自动化测试

## 📁 文件结构

```
auto_tests/iot/
├── device_stats_ui_automation.py   ⭐ 主测试脚本
├── run_test.bat                    一键运行脚本（Windows）
├── README.md                       本说明文件
├── 快速开始.md                      快速上手指南
└── test_log_*.txt                  运行后自动生成的日志文件
```

## 📋 测试用例覆盖

| 用例ID | 用例标题 | 优先级 |
|--------|----------|--------|
| TC_DS_001 | 已登录 IOT 平台 | 高 |
| TC_DS_002 | 全局筛选 - 系统切换展示正确 | 高 |
| TC_DS_003 | 导出 PDF 文件 | 高 |
| TC_DS_004 | 设备状态分布柱状图点击 | 高 |

测试用例来源：`../../excel/设备统计_测试用例.xlsx`

## 🔧 前置条件

- Python 3.8+
- Google Chrome 浏览器
- 以下 Python 依赖包：

```
selenium
webdriver-manager
openpyxl
```

安装依赖：
```bash
pip install selenium webdriver-manager openpyxl
```

## 🚀 运行方式

### 方式1：双击运行（推荐）
双击 `run_test.bat`

### 方式2：命令行运行
```bash
cd auto_tests/iot
python device_stats_ui_automation.py
```

### 方式3：从项目根目录运行
```bash
python auto_tests/iot/device_stats_ui_automation.py
```

## ⚠️ 验证码说明

- 脚本启动后会自动打开浏览器、输入账号密码
- 需要在浏览器窗口中**手动输入图形验证码**
- 脚本最多等待 **15 秒**，检测到输入后自动继续
- 15 秒内未输入则自动尝试登录

## 📊 输出说明

运行后自动生成：
- `test_log_YYYYMMDD_HHMMSS.txt`：详细执行日志，包含每步骤结果
- `*.html`：失败时自动保存的页面快照（用于调试）

## 🔗 相关配置

| 配置项 | 值 |
|--------|----|
| 登录地址 | https://iot.csmart-test.com/#/login |
| 账号 | raolekang |
| 测试系统 | C-Smart内部盘 → 市场化盘 |
