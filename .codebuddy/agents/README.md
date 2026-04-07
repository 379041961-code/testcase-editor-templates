# 个人 CodeBuddy Skills 目录

此目录用于存放个人项目的 CodeBuddy Skills 文件。

## 注意事项
1. 本目录下的 `.md` 文件已被 `.gitignore` 排除，不会提交到版本控制
2. 团队共享模板位于 `templates/codebuddy-skills/`
3. 创建新技能时，请从团队模板复制并填充实际项目信息
4. 确保目录中存在至少一个文件（本 README），以便 Git 能跟踪此目录

## 使用步骤
1. 从 `templates/codebuddy-skills/` 复制所需模板到此目录
2. 重命名为有意义的名称（如 `测试用例生成.md`）
3. 编辑文件，将所有 `[占位符]` 替换为实际项目信息
4. CodeBuddy 会自动加载新技能

## 示例
```powershell
# 创建测试用例生成技能
copy ..\..\templates\codebuddy-skills\template-testcase.md 测试用例生成.md

# 编辑文件，替换占位符：
# [需求文档路径] → IOT平台2.0.docx
# [具体章节] → 7.4
# [原型链接] → https://modao.cc/app/y9owp5mart4ew4zG1I0JJGM#screen=smbg1y7yoz4fm0
# [用例生成脚本] → gen_testcases.py
# [模块缩写] → DS
```