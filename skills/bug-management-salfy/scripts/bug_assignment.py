"""
缺陷指派模块
处理缺陷的自动指派操作
"""

from cloud_effect_login import CloudEffectLogin


class BugAssignment:
    """缺陷指派管理"""
    
    def __init__(self, config_path=".bug-management-config.json"):
        self.login_manager = CloudEffectLogin(config_path)
        self.config = self.login_manager.config
    
    def assign_bug(self, issue_id, assignee_email, comment=None):
        """将缺陷指派给指定人员"""
        # 登录系统
        if not self.login_manager.login():
            print("✗ 无法登录到云效系统")
            return False
        
        try:
            session = self.login_manager.get_session()
            base_url = self.config.get('cloudEffect', {}).get('baseUrl')
            
            # 构建指派数据
            payload = {
                'assigneeEmail': assignee_email
            }
            
            if comment:
                payload['comment'] = comment
            
            assign_url = f"{base_url}/api/issues/{issue_id}/assign"
            
            print(f"正在指派缺陷 {issue_id} 给 {assignee_email}...")
            response = session.post(
                assign_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code in [200, 201]:
                print(f"✓ 缺陷指派成功")
                print(f"  - 缺陷ID: {issue_id}")
                print(f"  - 指派人: {assignee_email}")
                
                if comment:
                    print(f"  - 备注: {comment}")
                
                return True
            else:
                print(f"✗ 缺陷指派失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ 指派缺陷异常: {str(e)}")
            return False
        finally:
            self.login_manager.logout()
    
    def assign_multiple(self, issue_assignments):
        """批量指派多个缺陷
        
        Args:
            issue_assignments: 列表，每项为 {'issue_id': '..', 'email': '..', 'comment': '...'}
        """
        success_count = 0
        fail_count = 0
        
        for assignment in issue_assignments:
            issue_id = assignment.get('issue_id')
            email = assignment.get('email')
            comment = assignment.get('comment')
            
            if self.assign_bug(issue_id, email, comment):
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n批量指派完成: 成功{success_count}个，失败{fail_count}个")
        return fail_count == 0
    
    def reassign_bug(self, issue_id, from_email, to_email, reason=None):
        """重新指派缺陷（转换负责人）"""
        comment = f"从 {from_email} 转换到 {to_email}"
        if reason:
            comment += f"，原因: {reason}"
        
        return self.assign_bug(issue_id, to_email, comment)
    
    def get_assignable_users(self):
        """获取可指派的用户列表"""
        if not self.login_manager.login():
            print("✗ 无法登录到云效系统")
            return []
        
        try:
            session = self.login_manager.get_session()
            base_url = self.config.get('cloudEffect', {}).get('baseUrl')
            project_id = self.config.get('cloudEffect', {}).get('projectId')
            
            users_url = f"{base_url}/api/projects/{project_id}/members"
            
            print("正在获取可指派的用户列表...")
            response = session.get(users_url, timeout=10)
            
            if response.status_code == 200:
                users = response.json().get('members', [])
                print(f"✓ 获取成功，共{len(users)}个成员")
                
                for user in users:
                    print(f"  - {user.get('name')} ({user.get('email')})")
                
                return users
            else:
                print(f"✗ 获取用户列表失败: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"✗ 获取用户列表异常: {str(e)}")
            return []
        finally:
            self.login_manager.logout()


def main():
    """测试缺陷指派功能"""
    assignment = BugAssignment()
    
    # 示例：获取可指派的用户
    print("获取可指派的用户:")
    users = assignment.get_assignable_users()
    
    # 示例：指派缺陷
    if users:
        first_user_email = users[0].get('email')
        issue_id = "TEST-12345"  # 示例缺陷ID
        
        print(f"\n尝试指派缺陷 {issue_id} 给 {first_user_email}:")
        assignment.assign_bug(issue_id, first_user_email, "自动指派测试")


if __name__ == "__main__":
    main()
