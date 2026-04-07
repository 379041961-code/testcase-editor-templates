# CodeBuddy Skills 团队使用指南

## 概述

CodeBuddy Skills 是项目级的 AI 扩展包，通过 Markdown 文件定义标准化的工作流程（SOP），使 AI 助手能够按照团队规范执行特定任务。本指南说明如何在团队中统一管理 Skills 模板和个人配置。

## 核心概念

### 1. Skills 文件结构
```
项目根目录/
├── .codebuddy/
│   ├── agents/           # 个人技能文件目录（不纳入 Git）
│   │   ├── README.md     # 占位文件（纳入 Git）
│   │   └── [个人技能].md # 个人技能文件（.gitignore 排除）
│   └── skills/           # （可选）历史遗留目录
├── templates/
│   └── codebuddy-skills/ # 团队模板目录（纳入 Git）
│       ├── template-base.md
│       ├── template-testcase.md
│       └── README.md
└── docs/
    └── codebuddy-skills-guide.md
```

### 2. 文件类型区分
- **团队模板**：`templates/codebuddy-skills/` 目录下的通用模板，包含 `[占位符]`，纳入版本控制
- **个人技能**：`.codebuddy/agents/` 目录下的具体技能文件，包含实际项目路径，通过 `.gitignore` 排除

## 工作流程

### 1. 新成员初始化
```powershell
# 克隆仓库
git clone <团队仓库地址>

# 创建个人技能目录
mkdir -p .codebuddy/agents

# 从模板创建个人技能
copy templates\codebuddy-skills\template-testcase.md .codebuddy\agents\测试用例生成.md

# 编辑技能文件，填充实际项目信息
# 1. 将 [需求文档路径] 替换为实际文档路径（如 IOT平台2.0.docx）
# 2. 将 [具体章节] 替换为实际章节（如 7.4）
# 3. 将 [原型链接] 替换为实际链接
# 4. 将 [用例生成脚本] 替换为实际脚本（如 gen_testcases.py）
# 5. 将 [模块缩写] 替换为实际缩写（如 DS）
```

### 2. 创建新技能模板
```powershell
# 基于现有个人技能创建新模板
copy .codebuddy\agents\新技能.md templates\codebuddy-skills\template-新功能.md

# 通用化处理：将项目特定信息替换为 [占位符]
# 1. 特定文件路径 → [文件路径]
# 2. 特定模块名称 → [模块名称]
# 3. 特定脚本名称 → [脚本名称]
# 4. 特定链接 → [链接]
```

### 3. 更新团队模板
1. 修改 `templates/codebuddy-skills/` 中的模板文件
2. 提交 Pull Request
3. 团队评审后合并
4. 团队成员同步更新

## Git 配置

### .gitignore 规则
```
# CodeBuddy 个人技能文件
.codebuddy/agents/*
!.codebuddy/agents/README.md
```

### 目录占位文件
在 `.codebuddy/agents/` 目录中创建 `README.md` 文件，内容如下：
```markdown
# 个人 CodeBuddy Skills 目录

此目录用于存放个人项目的 CodeBuddy Skills 文件。

## 注意事项
1. 本目录下的 `.md` 文件已被 `.gitignore` 排除，不会提交到版本控制
2. 团队共享模板位于 `templates/codebuddy-skills/`
3. 创建新技能时，请从团队模板复制并填充实际项目信息
```

## 最佳实践

### 1. 模板设计原则
- **完整性**：包含完整的 YAML 元数据和 SOP 章节
- **通用性**：使用 `[占位符]` 替代项目特定信息
- **明确性**：每个占位符都有清晰的说明和示例
- **可测试性**：模板应能直接运行（填充占位符后）

### 2. 命名规范
- 模板文件：`template-[功能].md`（如 `template-testcase.md`）
- 个人技能：`[功能描述].md`（如 `测试用例生成.md`）
- 技能名称：使用英文或拼音，避免特殊字符

### 3. 版本管理
- 模板文件变更需经过团队评审
- 重大变更时更新版本号或创建迁移指南
- 保持向后兼容性

## 常见问题

### Q1: 为什么个人技能文件不纳入 Git？
A: 个人技能包含项目特定的文件路径、链接等敏感信息，这些信息因人而异、因项目而异。纳入 Git 会导致冲突和信息泄露。

### Q2: 如何分享优秀的个人技能？
A: 将个人技能通用化（替换为占位符）后，提交到 `templates/codebuddy-skills/` 作为新模板。

### Q3: 技能文件不生效怎么办？
A: 检查以下事项：
1. 文件是否在 `.codebuddy/agents/` 目录中
2. YAML 元数据格式是否正确
3. 技能是否启用（enabled: true）
4. 是否需要重启 CodeBuddy

### Q4: 如何调试技能执行？
A: 在技能文件中添加调试信息，或检查 CodeBuddy 的日志输出。

## 联系与支持

- 模板问题：提交 Issue 或 Pull Request
- 使用问题：查阅本文档或联系团队负责人
- 功能建议：在团队会议中讨论