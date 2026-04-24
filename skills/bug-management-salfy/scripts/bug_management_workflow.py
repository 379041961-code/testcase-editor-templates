"""
缺陷管理主协调程序
集成所有模块完成端到端的缺陷管理工作流
"""

import json
import sys
from pathlib import Path

from cloud_effect_login import CloudEffectLogin
from bug_submission import BugSubmission
from file_upload import FileUpload
from bug_assignment import BugAssignment
from validation import BugValidator


class BugManagementWorkflow:
    """缺陷管理工作流协调器"""
    
    def __init__(self, config_path=".bug-management-config.json"):
        self.config_path = config_path
        self.validator = BugValidator()
        self.submission = BugSubmission(config_path)
        self.uploader = FileUpload(config_path)
        self.assigner = BugAssignment(config_path)
        self.issue_id = None
        self.workflow_log = []
    
    def submit_bug(self, bug_info):
        """完整的缺陷提交工作流
        
        Args:
            bug_info: 包含以下键的字典
                - title: 缺陷标题
                - environment: 环境
                - expected_result: 预期结果
                - actual_result: 实际结果
                - reproduction_steps: 重现步骤
                - assignee_email: 负责人邮箱
                - priority: 优先级 (可选, 默认P2)
                - frequency: 重现频率 (可选)
                - attachment_path: 附件路径 (可选)
                - notes: 备注 (可选)
        
        Returns:
            Dict: 工作流执行结果
        """
        result = {
            'success': False,
            'issue_id': None,
            'errors': [],
            'warnings': [],
            'log': []
        }
        
        # 1. 验证缺陷信息
        print("\n" + "="*60)
        print("【第一步】验证缺陷信息")
        print("="*60)
        
        is_valid, errors, warnings = self.validator.validate(bug_info)
        
        if errors:
            print("✗ 验证失败:\n")
            for error in errors:
                print(f"  {error}")
            result['errors'] = errors
            result['log'].append('validation_failed')
            return result
        
        print("✓ 信息验证通过")
        result['warnings'] = warnings
        
        if warnings:
            print("\n⚠ 警告信息:")
            for key, warning in warnings.items():
                print(f"  {warning}")
        
        result['log'].append('validation_passed')
        
        # 2. 创建缺陷
        print("\n" + "="*60)
        print("【第二步】创建缺陷")
        print("="*60)
        
        self.issue_id = self.submission.create_bug(bug_info)
        
        if not self.issue_id:
            result['errors'].append('缺陷创建失败')
            result['log'].append('bug_creation_failed')
            return result
        
        result['issue_id'] = self.issue_id
        result['log'].append('bug_created')
        
        # 3. 上传附件 (如果提供)
        if bug_info.get('attachment_path'):
            print("\n" + "="*60)
            print("【第三步】上传附件")
            print("="*60)
            
            attachment_path = bug_info.get('attachment_path')
            if self.uploader.upload_file(self.issue_id, attachment_path):
                result['log'].append('attachment_uploaded')
            else:
                result['warnings'].append('附件上传失败，但缺陷已创建')
                result['log'].append('attachment_upload_failed')
        else:
            print("\n【跳过】未提供附件")
            result['log'].append('attachment_skipped')
        
        # 4. 指派缺陷
        print("\n" + "="*60)
        print("【第四步】指派缺陷")
        print("="*60)
        
        assignee_email = bug_info.get('assignee_email')
        comment = f"自动指派: {bug_info.get('title', '')}"
        
        if self.assigner.assign_bug(self.issue_id, assignee_email, comment):
            result['log'].append('bug_assigned')
        else:
            result['warnings'].append('缺陷指派失败，但缺陷已创建')
            result['log'].append('bug_assignment_failed')
        
        # 5. 生成完成报告
        print("\n" + "="*60)
        print("【完成】缺陷管理工作流")
        print("="*60)
        
        result['success'] = True
        self._print_completion_report(result, bug_info)
        
        return result
    
    def _print_completion_report(self, result, bug_info):
        """打印完成报告"""
        report = f"""
✓ 缺陷提交成功！

【缺陷信息摘要】
  缺陷ID:       {result['issue_id']}
  标题:         {bug_info.get('title')}
  环境:         {bug_info.get('environment')}
  优先级:       {bug_info.get('priority', 'P2')}
  负责人:       {bug_info.get('assignee_email')}
  
【执行步骤】
"""
        for i, log in enumerate(result['log'], 1):
            status_map = {
                'validation_passed': '✓ 信息验证通过',
                'bug_created': '✓ 缺陷已创建',
                'attachment_uploaded': '✓ 附件已上传',
                'attachment_skipped': '○ 附件已跳过',
                'attachment_upload_failed': '⚠ 附件上传失败',
                'bug_assigned': '✓ 缺陷已指派',
                'bug_assignment_failed': '⚠ 缺陷指派失败',
            }
            report += f"  {i}. {status_map.get(log, log)}\n"
        
        if result['warnings']:
            report += f"\n【警告信息】\n"
            for warning in result['warnings']:
                report += f"  ⚠ {warning}\n"
        
        report += f"""
【后续操作】
    请在测试环境的缺陷系统中搜索缺陷 ID 继续跟踪:
    {result['issue_id']}
  
  负责人将收到自动指派通知并开始处理。
"""
        print(report)
    
    def create_config_template(self):
        """创建默认配置模板"""
        config_template = {
            "cloudEffect": {
                "baseUrl": "",
                "projectId": "your-project-id",
                "defaultPriority": "P2",
                "defaultAssignee": "owner@example.com"
            },
            "upload": {
                "maxFileSize": 10485760,
                "allowedTypes": ["jpg", "png", "gif", "zip", "txt", "pdf"],
                "uploadPath": "./bug-attachments"
            }
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config_template, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 配置模板已生成: {self.config_path}")
        print("  请编辑此文件并填入实际的云效系统信息")
        return config_template


def interactive_submit():
    """交互式提交缺陷"""
    workflow = BugManagementWorkflow()
    
    print("\n" + "="*60)
    print("欢迎使用缺陷管理自动化工具")
    print("="*60 + "\n")
    
    # 检查配置文件
    if not Path(".bug-management-config.json").exists():
        print("⚠ 未找到配置文件 .bug-management-config.json")
        response = input("是否创建默认配置模板? (y/n): ").strip().lower()
        if response == 'y':
            workflow.create_config_template()
            print("\n请编辑 .bug-management-config.json 后重新运行此程序")
            return
        else:
            print("取消操作")
            return
    
    # 收集缺陷信息
    bug_info = {}
    
    print("请输入以下信息 (必填项用 * 标记):\n")
    
    # 必填字段
    bug_info['title'] = input("* 缺陷标题: ").strip()
    if not bug_info['title']:
        print("✗ 标题不能为空")
        return
    
    print("\n环境选项: 开发, 测试, 预发, 线上")
    bug_info['environment'] = input("* 环境: ").strip()
    if not bug_info['environment']:
        print("✗ 环境不能为空")
        return
    
    print("\n请详细描述问题:")
    bug_info['expected_result'] = input("* 预期结果: ").strip()
    if not bug_info['expected_result']:
        print("✗ 预期结果不能为空")
        return
    
    bug_info['actual_result'] = input("* 实际结果: ").strip()
    if not bug_info['actual_result']:
        print("✗ 实际结果不能为空")
        return
    
    bug_info['reproduction_steps'] = input("* 重现步骤 (多行，输入END结束):\n").strip()
    if not bug_info['reproduction_steps']:
        print("✗ 重现步骤不能为空")
        return
    
    print("\n优先级选项: P0, P1, P2 (默认), P3")
    priority = input("优先级 [P2]: ").strip() or "P2"
    bug_info['priority'] = priority
    
    print("\n重现频率选项: 100%稳定复现, 90%以上, 50-90%, 50%以下")
    bug_info['frequency'] = input("重现频率 [100%稳定复现]: ").strip() or "100%稳定复现"
    
    bug_info['assignee_email'] = input("* 负责人邮箱: ").strip()
    if not bug_info['assignee_email']:
        print("✗ 负责人邮箱不能为空")
        return
    
    attachment_path = input("\n附件路径 (可选): ").strip()
    if attachment_path:
        bug_info['attachment_path'] = attachment_path
    
    bug_info['notes'] = input("备注 (可选): ").strip()
    if bug_info['notes']:
        pass
    
    # 执行工作流
    result = workflow.submit_bug(bug_info)
    
    if not result['success']:
        print("\n✗ 缺陷提交失败")
        for error in result['errors']:
            print(f"  - {error}")


def main():
    """主入口"""
    if len(sys.argv) > 1:
        # 命令行模式
        config_file = sys.argv[1] if sys.argv[1] != '--interactive' else ".bug-management-config.json"
        
        if '--interactive' in sys.argv:
            interactive_submit()
        else:
            print("暂不支持命令行模式，请使用交互模式")
    else:
        # 交互模式
        interactive_submit()


if __name__ == "__main__":
    main()
