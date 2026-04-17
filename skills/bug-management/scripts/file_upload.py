"""
文件上传模块
处理附件的上传到云效系统
"""

import os
import json
from pathlib import Path
from cloud_effect_login import CloudEffectLogin


class FileUpload:
    """文件上传管理"""
    
    def __init__(self, config_path=".bug-management-config.json"):
        self.login_manager = CloudEffectLogin(config_path)
        self.config = self.login_manager.config
        self._load_upload_config()
    
    def _load_upload_config(self):
        """加载上传配置"""
        upload_config = self.config.get('upload', {})
        self.max_file_size = upload_config.get('maxFileSize', 10485760)  # 10MB
        self.allowed_types = upload_config.get('allowedTypes', 
                                              ['jpg', 'png', 'gif', 'zip', 'txt', 'pdf'])
        self.upload_path = upload_config.get('uploadPath', './bug-attachments')
    
    def validate_file(self, file_path):
        """验证文件是否可以上传"""
        errors = []
        
        # 检查文件是否存在
        if not Path(file_path).exists():
            errors.append(f"文件不存在: {file_path}")
            return False, errors
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            errors.append(f"文件过大: {file_size} 字节 (最多{self.max_file_size})")
        
        # 检查文件类型
        file_ext = Path(file_path).suffix.lower().lstrip('.')
        if file_ext not in self.allowed_types:
            errors.append(f"不支持的文件类型: {file_ext}")
        
        return len(errors) == 0, errors
    
    def upload_file(self, issue_id, file_path):
        """上传文件到缺陷"""
        # 验证文件
        is_valid, errors = self.validate_file(file_path)
        if not is_valid:
            print(f"✗ 文件验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        # 登录系统
        if not self.login_manager.login():
            print("✗ 无法登录到云效系统")
            return False
        
        try:
            session = self.login_manager.get_session()
            base_url = self.config.get('cloudEffect', {}).get('baseUrl')
            
            file_name = Path(file_path).name
            
            # 准备文件上传
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f)}
                data = {'issueId': issue_id}
                
                upload_url = f"{base_url}/api/issues/{issue_id}/attachments"
                
                print(f"正在上传文件: {file_name}")
                response = session.post(
                    upload_url,
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code in [200, 201]:
                attachment_data = response.json()
                attachment_id = attachment_data.get('id') or attachment_data.get('attachmentId')
                
                print(f"✓ 文件上传成功")
                print(f"  - 文件名: {file_name}")
                print(f"  - 附件ID: {attachment_id}")
                print(f"  - 大小: {os.path.getsize(file_path)} 字节")
                
                return True
            else:
                print(f"✗ 文件上传失败: {response.status_code}")
                print(f"  错误信息: {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ 上传文件异常: {str(e)}")
            return False
        finally:
            self.login_manager.logout()
    
    def upload_multiple(self, issue_id, file_paths):
        """批量上传多个文件"""
        success_count = 0
        fail_count = 0
        
        for file_path in file_paths:
            if self.upload_file(issue_id, file_path):
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n批量上传完成: 成功{success_count}个，失败{fail_count}个")
        return fail_count == 0
    
    def ensure_upload_directory(self):
        """确保上传目录存在"""
        Path(self.upload_path).mkdir(parents=True, exist_ok=True)
        print(f"✓ 上传目录已就绪: {self.upload_path}")
    
    def get_upload_config(self):
        """获取上传配置信息"""
        config_info = {
            "max_file_size_mb": self.max_file_size / (1024 * 1024),
            "allowed_types": self.allowed_types,
            "upload_path": self.upload_path
        }
        return config_info


def main():
    """测试文件上传功能"""
    uploader = FileUpload()
    
    # 显示配置
    print("上传配置:")
    config = uploader.get_upload_config()
    for key, value in config.items():
        print(f"  - {key}: {value}")
    
    # 示例：验证文件
    test_file = "./screenshot_example.png"
    if Path(test_file).exists():
        is_valid, errors = uploader.validate_file(test_file)
        if is_valid:
            print(f"✓ 文件可以上传: {test_file}")
        else:
            print(f"✗ 文件不能上传: {test_file}")
            for error in errors:
                print(f"  - {error}")
    else:
        print(f"示例文件不存在: {test_file}")


if __name__ == "__main__":
    main()
