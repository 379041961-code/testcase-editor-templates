"""
缺陷创建和提交模块
处理缺陷信息的收集、验证和提交
"""

import json
import re
from datetime import datetime
from cloud_effect_login import CloudEffectLogin


class BugSubmission:
    """缺陷提交管理"""
    
    def __init__(self, config_path=".bug-management-config.json"):
        self.login_manager = CloudEffectLogin(config_path)
        self.config = self.login_manager.config
        self.bug_data = {}
    
    def validate_bug_info(self, bug_info):
        """验证缺陷信息的完整性"""
        errors = []
        
        # 必填字段
        required_fields = {
            'title': '缺陷标题',
            'environment': '环境',
            'expected_result': '预期结果',
            'actual_result': '实际结果',
            'reproduction_steps': '重现步骤',
            'assignee_email': '负责人邮箱'
        }
        
        for field, label in required_fields.items():
            if not bug_info.get(field, '').strip():
                errors.append(f"缺少必填项: {label}")
        
        # 验证邮箱格式
        email = bug_info.get('assignee_email', '').strip()
        if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append(f"邮箱格式不正确: {email}")
        
        # 验证优先级
        priority = bug_info.get('priority', 'P2')
        if priority not in ['P0', 'P1', 'P2', 'P3']:
            errors.append(f"优先级无效: {priority}，应为 P0/P1/P2/P3")
        
        # 验证标题长度
        title = bug_info.get('title', '')
        if len(title) > 100:
            errors.append(f"标题过长: {len(title)} 字符（最多100字）")
        
        return len(errors) == 0, errors
    
    def create_bug(self, bug_info):
        """提交缺陷到云效系统"""
        # 验证信息
        is_valid, errors = self.validate_bug_info(bug_info)
        if not is_valid:
            print("✗ 缺陷信息验证失败:")
            for error in errors:
                print(f"  - {error}")
            return None
        
        # 登录系统
        if not self.login_manager.login():
            print("✗ 无法登录到云效系统")
            return None
        
        try:
            session = self.login_manager.get_session()
            base_url = self.config.get('cloudEffect', {}).get('baseUrl')
            project_id = self.config.get('cloudEffect', {}).get('projectId')
            
            # 构建缺陷数据
            payload = {
                "title": bug_info.get('title'),
                "environment": bug_info.get('environment'),
                "expectedResult": bug_info.get('expected_result'),
                "actualResult": bug_info.get('actual_result'),
                "reproductionSteps": bug_info.get('reproduction_steps'),
                "priority": bug_info.get('priority', 'P2'),
                "frequency": bug_info.get('frequency', '稳定复现'),
                "description": self._build_description(bug_info),
                "projectId": project_id,
                "status": "新建"
            }
            
            # 如果有附件路径，添加到负载
            attachment_path = bug_info.get('attachment_path')
            if attachment_path:
                payload['attachmentPath'] = attachment_path
            
            # 提交缺陷
            create_url = f"{base_url}/api/issues/create"
            response = session.post(create_url, json=payload, timeout=15)
            
            if response.status_code in [200, 201]:
                issue_data = response.json()
                issue_id = issue_data.get('id') or issue_data.get('issueId')
                
                print(f"✓ 缺陷创建成功")
                print(f"  - 缺陷ID: {issue_id}")
                print(f"  - 标题: {bug_info.get('title')}")
                
                self.bug_data = {
                    'issue_id': issue_id,
                    'title': bug_info.get('title'),
                    'created_at': datetime.now().isoformat()
                }
                
                return issue_id
            else:
                print(f"✗ 缺陷创建失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return None
                
        except Exception as e:
            print(f"✗ 创建缺陷异常: {str(e)}")
            return None
        finally:
            self.login_manager.logout()
    
    def _build_description(self, bug_info):
        """构建缺陷描述"""
        description = f"""## 缺陷信息

### 基本信息
- **标题**: {bug_info.get('title')}
- **环境**: {bug_info.get('environment')}
- **优先级**: {bug_info.get('priority', 'P2')}
- **重现频率**: {bug_info.get('frequency', '稳定复现')}

### 问题描述
**预期结果:**
{bug_info.get('expected_result')}

**实际结果:**
{bug_info.get('actual_result')}

### 重现步骤
{bug_info.get('reproduction_steps')}

### 附加信息
- **产品线**: {bug_info.get('product_line', '未指定')}
- **模块**: {bug_info.get('module', '未指定')}
- **提交时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
        
        if bug_info.get('notes'):
            description += f"### 备注\n{bug_info.get('notes')}\n"
        
        return description


def main():
    """测试缺陷创建功能"""
    bug_info = {
        'title': '登录页面验证码无法正确显示',
        'environment': '测试环境',
        'expected_result': '验证码应显示清晰的数字和字母组合',
        'actual_result': '验证码显示为黑色方块，无法识别',
        'reproduction_steps': '1. 打开登录页面\n2. 查看验证码区域\n3. 观察显示效果',
        'assignee_email': 'zhang.san@alibaba-inc.com',
        'priority': 'P1',
        'frequency': '100%稳定复现',
        'product_line': '登录模块',
        'module': 'UI',
    }
    
    submission = BugSubmission()
    issue_id = submission.create_bug(bug_info)
    
    if issue_id:
        print(f"\n成功创建缺陷，ID: {issue_id}")
    else:
        print("\n缺陷创建失败")


if __name__ == "__main__":
    main()
