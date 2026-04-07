# CodeBuddy Skills 模板库

本目录包含团队共享的 CodeBuddy Skills 模板文件，用于标准化 AI 助手能力扩展。

## 模板文件说明

### template-base.md
基础技能模板，包含标准的 YAML 元数据结构和通用章节框架。适用于创建新技能时的起点。

### template-testcase.md
测试用例生成器专用模板，基于 IoT 平台设备统计模块的实际需求提炼。包含完整的用例编号规则、格式规范和验证标准。

## 使用指南

### 1. 创建新技能
1. 复制合适的模板到 `.codebuddy/agents/[技能名称].md`
2. 根据具体需求填充占位符：
   - `[技能名称]`：技能标识，建议使用英文或拼音
   - `[技能描述]`：清晰的功能描述
   - `[工具列表]`：技能需要的工具权限
   - `[具体章节]`：需求文档中的章节号
   - `[原型链接]`：产品原型链接
   - `[用例生成脚本]`：用例输出脚本路径
   - `[模块缩写]`：功能模块缩写

### 2. 个性化配置
- **agentMode**: `manual`（手动触发）或 `always`（始终启用）
- **enabled**: `true` 启用技能
- **enabledAutoRun**: `true` 允许自动运行（仅当 agentMode=always 时生效）

### 3. 激活技能
将创建好的 `.md` 文件放入 `.codebuddy/agents/` 目录即可激活，CodeBuddy 会自动加载。

## 模板维护原则

1. **通用性**：模板中使用 `[占位符]` 替代项目特定信息
2. **完整性**：包含所有必要的 YAML 字段和 SOP 章节
3. **一致性**：遵循相同的结构和编写风格
4. **版本控制**：模板文件纳入 Git 管理，个人技能文件通过 `.gitignore` 排除

## 贡献流程

1. 在 `templates/codebuddy-skills/` 中创建或更新模板
2. 提交 Pull Request
3. 团队评审通过后合并

## 相关文档

- [团队使用指南](../docs/codebuddy-skills-guide.md)
- CodeBuddy 官方文档