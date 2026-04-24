# IOT 2.0 设备统计 UI 自动化测试

## 文件结构说明

```text
auto_tests/readme/device_stats_ui/
├── device_stats_ui_automation.py   主测试脚本
├── run_test.bat                    Windows 一键运行脚本
├── README.md                       说明文档
├── 快速开始.md                      快速上手指南
├── html/                           运行时生成的页面快照目录
└── log/                            运行时生成的测试日志目录
```

## 测试用例覆盖

| 用例ID | 用例标题 | 优先级 |
|--------|----------|--------|
| TC_DS_001 | 已登录 IOT 平台 | 高 |
| TC_DS_002 | 全局筛选 - 系统切换展示正确 | 高 |
| TC_DS_003 | 导出 PDF 文件 | 高 |
| TC_DS_004 | 设备状态分布柱状图点击 | 高 |

## 测试用例来源路径

- ../../excel/设备统计_测试用例.xlsx

## 前置条件

- Python 3.8+
- Google Chrome 浏览器
- Python 依赖包：selenium、webdriver-manager、openpyxl

安装命令：

```bash
pip install selenium webdriver-manager openpyxl
```

## 运行方式

1. bat 双击：双击 run_test.bat。
2. 命令行运行：

```bash
cd auto_tests/readme/device_stats_ui
python device_stats_ui_automation.py
```

3. 根目录运行：

```bash
python auto_tests/readme/device_stats_ui/device_stats_ui_automation.py
```

## 验证码说明

- 脚本自动打开登录页并填写账号密码。
- 验证码需要在浏览器中手动输入。
- 脚本自动检测验证码输入状态，最多等待 15 秒，无需按键确认。

## 输出说明

- 日志文件：log/test_log_YYYYMMDD_HHMMSS.txt
- 快照文件：html/{阶段名}_HHMMSS.html

## 相关配置

| 配置项 | 值 |
|--------|----|
| 登录地址 | https://iot.csmart-test.com/#/login |
| 测试目标系统 | 海宏 IOT2.0 测试环境 |
| 账号环境变量 | IOT_TEST_USERNAME |
| 密码环境变量 | IOT_TEST_PASSWORD |
| 用例文件 | excel/设备统计_测试用例.xlsx |

## 登录凭据配置

运行前请在当前终端先设置环境变量：

```bat
set IOT_TEST_USERNAME=你的账号
set IOT_TEST_PASSWORD=你的密码
```
