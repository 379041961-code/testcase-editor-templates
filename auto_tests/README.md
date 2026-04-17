# 🚀 IOT自动化测试文件夹

## 📁 文件结构

```
auto_tests/
├── 📍 核心脚本
│   ├── ui_automation_final.py ⭐ 【主脚本 - 推荐使用】
│   ├── ui_automation_test.py
│   └── read_excel.py
│
├── ⚙️ 配置文件
│   └── test_config.ini
│
├── 📋 输出文件
│   ├── test_log_*.txt （运行后生成）
│   ├── page_source_*.html （运行后生成）
│   ├── login_failed_*.html
│   ├── page_before_filter_*.html
│   ├── page_before_chart_*.html
│   └── device_detail_*.html
│
└── 📚 说明文件
    └── README.md 【本文件】
```

## 🚀 快速开始

### 方式1: Windows命令行运行
```bash
cd auto_tests
python ui_automation_final.py
```

### 方式2: PowerShell运行
```powershell
cd auto_tests
python .\ui_automation_final.py
```

### 方式3: 从任意位置运行
```bash
python "auto_tests\ui_automation_final.py"
```

## ⚠️ 重要提示

**文件路径已自动调整**:
- ✅ Excel文件路径：`../excel/设备统计_测试用例.xlsx`
- ✅ 日志文件：自动保存到本文件夹
- ✅ 页面快照：自动保存到本文件夹

**所有路径均已修改正确，可直接运行！**

## 📝 核心脚本说明

### `ui_automation_final.py` ⭐

**功能**：完整的UI自动化测试框架

**测试用例**：
1. TC_DS_001 - 登录测试
2. TC_DS_002 - 系统筛选
3. TC_DS_003 - PDF导出
4. TC_DS_004 - 设备统计

**运行方式**：
```bash
python ui_automation_final.py
```

**输出**：
- 控制台实时日志
- test_log_*.txt - 详细日志
- page_source_*.html - 页面快照

## ⚙️ 配置文件

文件：`test_config.ini`

包含所有可配置的参数：
- 登录信息（账号、密码、URL）
- 浏览器设置（头部模式、窗口大小）
- 测试选项
- 系统筛选参数
- 导出配置
- 日志输出设置

**编辑方法**：用任意文本编辑器打开

## 📊 输出文件

运行测试后自动生成：

1. **test_log_YYYYMMDD_HHMMSS.txt**
   - 详细的测试执行日志
   - 包含每个步骤的结果
   - 错误信息和异常跟踪

2. **page_source_YYYYMMDD_HHMMSS.html**
   - 页面快照用于调试
   - 包含完整的HTML结构

## 💡 常见问题

**Q: 如何修改登录账号？**
A: 编辑 `test_config.ini` 中的 `[LOGIN]` 部分

**Q: 如何后台运行？**
A: 在脚本中将 `headless=False` 改为 `headless=True`

**Q: 如何查看日志？**
A: 打开生成的 `test_log_*.txt` 文件

**Q: Excel找不到？**
A: 确保 `excel/` 文件夹在项目根目录（auto_tests的上一级）

## 🔗 相关文件位置

- **Excel测试用例**：`../excel/设备统计_测试用例.xlsx`
- **其他文档**：请参考上级目录的文档

---

**版本**：1.0  
**日期**：2026-04-14  
**状态**：✅ 所有路径已调整，可直接运行
