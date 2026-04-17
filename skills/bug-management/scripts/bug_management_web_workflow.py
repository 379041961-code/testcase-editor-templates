"""
缺陷管理主协调程序（Web自动化版本）
使用Selenium自动化操作阿里云效Web系统
"""

import os
import json
import sys
from pathlib import Path

from aliyun_bug_automation import AliyunCloudEffectAutomation
from validation import BugValidator


class BugManagementWorkflow:
    """缺陷管理工作流协调器（Web版本）"""
    
    def __init__(self, config_path=".bug-management-config.json"):
        self.config_path = config_path
        self.validator = BugValidator()
        self.automation = None
        self.workflow_log = []
    
    def submit_bug_interactive(self):
        """交互式缺陷提交 - 单行输入模式"""
        
        print("\n" + "="*70)
        print("欢迎使用阿里云效缺陷管理自动化工具")
        print("="*70 + "\n")
        
        print("【输入格式说明】")
        print("-" * 70)
        print("用句号（。）分割多个字段，按顺序输入：")
        print("项目名。BUG标题。预期结果。负责人。[文件路径1,文件路径2,...]")
        print("\n示例：")
        print(r"IOT平台 2.0。登录按钮无响应。预期结果：点击按钮跳转页面[ 实际结果：点击按钮无响应(方括号里可填可不填)]。李明。/path/to/image1.png,/path/to/image2.jpg")
        print("\n注意：")
        print("  - 必填字段：项目名、BUG标题、预期结果、负责人")
        print("  - 可选字段：文件路径（支持多个，用逗号分割）")
        print("-" * 70 + "\n")
        
        # 一次性输入
        user_input = input("请输入缺陷信息 (用句号分割): ").strip()
        
        if not user_input:
            print("✗ 输入不能为空")
            return False
        
        # 解析输入
        fields = [f.strip() for f in user_input.split('。')]
        
        # 检查最少字段数（4个必填字段）
        if len(fields) < 4:
            print("✗ 信息不完整，必须输入4个必填字段（项目名、标题、预期、负责人）")
            return False
        
        bug_info = {}
        
        try:
            # 必填字段
            bug_info['project_name'] = fields[0]
            bug_info['title'] = fields[1]
            bug_info['expected_result'] = fields[2]
            bug_info['assignee_info'] = fields[3]
            
            # 检查必填字段不能为空
            for key in ['project_name', 'title', 'expected_result', 'assignee_info']:
                if not bug_info[key]:
                    print(f"✗ {key} 不能为空")
                    return False
            
            # 可选字段
            attachment_paths_str = fields[4] if len(fields) > 4 and fields[4] else ""
            
            # 支持多个文件路径，用逗号分割
            if attachment_paths_str:
                bug_info['attachment_paths'] = [p.strip() for p in attachment_paths_str.split(',') if p.strip()]
            
        except Exception as e:
            print(f"✗ 解析输入失败: {str(e)}")
            return False
        
        # 显示输入的信息
        print("\n" + "="*70)
        print("【解析的缺陷信息】")
        print("="*70)
        print(f"项目:        {bug_info.get('project_name')}")
        print(f"标题:        {bug_info.get('title')}")
        print(f"预期结果:    {bug_info.get('expected_result')}")
        print(f"负责人:      {bug_info.get('assignee_info')}")
        if 'attachment_paths' in bug_info:
            print(f"文件数量:    {len(bug_info['attachment_paths'])} 个")
            for i, path in enumerate(bug_info['attachment_paths'], 1):
                print(f"  {i}. {path}")
        if 'attachment_path' in bug_info:
            print(f"文件路径:    {bug_info.get('attachment_path')}")
        
        # 验证缺陷信息
        print("\n" + "="*70)
        print("【验证缺陷信息】")
        print("="*70)
        
        is_valid, errors, warnings = self.validator.validate(bug_info)
        
        if errors:
            print("✗ 验证失败:\n")
            for error in errors:
                print(f"  {error}")
            return False
        
        print("✓ 信息验证通过")
        
        if warnings:
            print("\n⚠ 警告信息:")
            for key, warning in warnings.items():
                print(f"  {warning}")
        
        self.workflow_log.append('validation_passed')
        
        # 执行自动化操作
        print("\n" + "="*70)
        print("【启动自动化工具】")
        print("="*70)
        
        username = os.getenv('CLOUD_EFFECT_USERNAME', 'nick1821010462')
        password = os.getenv('CLOUD_EFFECT_PASSWORD', 'R20250918')
        
        if not username or not password:
            print("✗ 缺少环境变量: CLOUD_EFFECT_USERNAME 或 CLOUD_EFFECT_PASSWORD")
            return False
        
        self.automation = AliyunCloudEffectAutomation(username, password)
        
        try:
            # 启动浏览器
            print("\n【启动浏览器】")
            print("="*70)
            if not self.automation.start_driver():
                print("✗ 启动浏览器失败")
                self.workflow_log.append('browser_startup_failed')
                return False
            
            print("✓ 浏览器已启动")
            self.workflow_log.append('browser_started')
            
            # 登录系统
            print("\n【登录系统】")
            print("="*70)
            if not self.automation.login():
                print("✗ 登录失败")
                self.workflow_log.append('login_failed')
                return False
            
            print("✓ 登录成功")
            self.workflow_log.append('login_success')
            
            # 导航到缺陷页面
            print(f"\n【导航到项目缺陷页面】")
            print("="*70)
            if not self.automation.navigate_to_bug_section(bug_info['project_name']):
                print(f"✗ 导航到项目失败")
                self.workflow_log.append('navigation_failed')
                return False
            
            print(f"✓ 已进入项目缺陷页面")
            self.workflow_log.append('navigation_success')
            
            # 创建缺陷
            print("\n【第六步】创建缺陷")
            print("="*70)
            if not self.automation.create_bug(bug_info):
                print("✗ 创建缺陷失败")
                self.workflow_log.append('bug_creation_failed')
                return False
            
            print("✓ 缺陷创建成功")
            self.workflow_log.append('bug_created')
            
            # 指派负责人
            print("\n【指派负责人】")
            print("="*70)
            if not self.automation.assign_bug(bug_info['assignee_info']):
                print(f"⚠ 指派负责人失败，但缺陷已创建")
                self.workflow_log.append('assignment_failed')
            else:
                print(f"✓ 已指派给: {bug_info['assignee_info']}")
                self.workflow_log.append('assignment_success')
            
            # 生成完成报告
            print("\n" + "="*70)
            print("【完成】缺陷管理工作流已完成")
            print("="*70)
            
            self._print_completion_report(bug_info, bug_info['assignee_info'])
            
            return True
            
        except Exception as e:
            print(f"✗ 执行异常: {str(e)}")
            self.workflow_log.append(f'error_{str(e)[:20]}')
            return False
        
        finally:
            if self.automation:
                self.automation.close_driver()
    
    def _print_completion_report(self, bug_info, assignee_info):
        """打印完成报告"""
        screenshots_dir = self.automation.get_screenshots_dir()
        
        report = f"""
✓ 缺陷提交成功！

【缺陷信息摘要】
  标题:         {bug_info.get('title')}
  预期结果:     {bug_info.get('expected_result')[:50]}...
  项目:         {bug_info.get('project_name')}
  负责人:       {assignee_info}
  
【截图信息】
  所有操作截图已保存到: {screenshots_dir}
  
【执行步骤】
  ✓ 1. 信息验证通过
  ✓ 2. 启动浏览器
  ✓ 3. 登录系统
  ✓ 4. 导航到项目缺陷页面
  ✓ 5. 创建缺陷
"""
        
        if 'assignment_success' in self.workflow_log:
            report += "  ✓ 6. 指派负责人\n"
        else:
            report += "  ⚠ 6. 指派负责人（失败）\n"
        
        report += f"""
【后续操作】
  请在浏览器中查看缺陷详情，确认信息完整。
  
"""
        print(report)
    
    def create_config_template(self):
        """创建默认配置模板"""
        config_template = {
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
                "headless": False,
                "timeout": 15,
                "screenshot_dir": "./bug-submission-screenshots"
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_template, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 配置模板已生成: {self.config_path}")
        return config_template


def interactive_submit():
    """交互式缺陷提交入口"""
    workflow = BugManagementWorkflow()
    
    # 检查必需的环境变量
    # if not os.getenv('CLOUD_EFFECT_USERNAME'):
    #     print("\n⚠ 未设置 CLOUD_EFFECT_USERNAME 环境变量")
    #     print("  请先设置环境变量:")
    #     print("  set CLOUD_EFFECT_USERNAME=your-username")
    #     return
    #
    # if not os.getenv('CLOUD_EFFECT_PASSWORD'):
    #     print("\n⚠ 未设置 CLOUD_EFFECT_PASSWORD 环境变量")
    #     print("  请先设置环境变量:")
    #     print("  set CLOUD_EFFECT_PASSWORD=your-password")
    #     return
    
    # 检查Selenium和WebDriver
    try:
        from selenium import webdriver
        print("✓ Selenium已安装")
    except ImportError:
        print("\n✗ 未安装Selenium")
        print("  请运行: pip install selenium")
        return
    
    # 开始交互式提交
    success = workflow.submit_bug_interactive()
    
    if not success:
        print("\n✗ 缺陷提交失败")
        sys.exit(1)
    else:
        print("\n✓ 缺陷提交成功")
        sys.exit(0)


def main():
    """主入口"""
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        interactive_submit()
    else:
        interactive_submit()


if __name__ == "__main__":
    main()
