"""
阿里云效系统登录模块
处理云效系统的身份认证和会话管理
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path


class CloudEffectLogin:
    """云效系统登录管理"""
    
    def __init__(self, config_path=".bug-management-config.json"):
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.token = None
        self.token_expiry = None
        
    def _load_config(self, config_path):
        """加载配置文件"""
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"cloudEffect": {"baseUrl": os.getenv('CLOUD_EFFECT_BASE_URL', '')}}
    
    def _get_credentials(self):
        """从环境变量获取凭证"""
        username = os.getenv('CLOUD_EFFECT_USERNAME')
        password = os.getenv('CLOUD_EFFECT_PASSWORD')
        
        if not username or not password:
            raise ValueError("缺少环境变量: CLOUD_EFFECT_USERNAME 或 CLOUD_EFFECT_PASSWORD")
        
        return username, password
    
    def login(self):
        """登录云效系统"""
        try:
            username, password = self._get_credentials()
            base_url = self.config.get('cloudEffect', {}).get('baseUrl')
            
            if not base_url:
                raise ValueError("未配置云效系统地址")
            
            login_url = f"{base_url}/api/auth/login"
            
            payload = {
                "username": username,
                "password": password
            }
            
            print(f"正在连接到云效系统: {base_url}")
            response = self.session.post(
                login_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get('token')
                self.token_expiry = datetime.now() + timedelta(hours=8)
                
                self.session.headers.update({
                    'Authorization': f'Bearer {self.token}',
                    'Content-Type': 'application/json'
                })
                
                print(f"✓ 成功登录到云效系统")
                return True
            else:
                print(f"✗ 登录失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"✗ 登录异常: {str(e)}")
            return False
    
    def is_logged_in(self):
        """检查是否已登录"""
        if not self.token or not self.token_expiry:
            return False
        
        if datetime.now() >= self.token_expiry:
            print("Token已过期，需要重新登录")
            return False
        
        return True
    
    def get_session(self):
        """获取会话对象"""
        if not self.is_logged_in():
            self.login()
        return self.session
    
    def logout(self):
        """登出系统"""
        base_url = self.config.get('cloudEffect', {}).get('baseUrl')
        logout_url = f"{base_url}/api/auth/logout"
        
        try:
            self.session.post(logout_url, timeout=5)
            print("✓ 已从云效系统登出")
        except Exception as e:
            print(f"✗ 登出失败: {str(e)}")
        finally:
            self.token = None
            self.token_expiry = None
            self.session.close()


def main():
    """测试登录功能"""
    try:
        login_manager = CloudEffectLogin()
        if login_manager.login():
            print("登录成功，已就绪")
            login_manager.logout()
        else:
            print("登录失败")
    except Exception as e:
        print(f"错误: {str(e)}")


if __name__ == "__main__":
    main()
