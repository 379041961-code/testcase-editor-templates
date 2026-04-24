"""
阿里云效Web自动化模块
使用Selenium自动化操作阿里云效BUG系统Web界面
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def _read_env(name: str) -> str:
    return os.getenv(name, '').strip().strip('"').strip("'")

try:
    import pyautogui
    import pyperclip
    PYAUTOGUI_AVAILABLE = True
except ImportError as e:
    PYAUTOGUI_AVAILABLE = False
    print(f"⚠ 警告: PyAutoGUI模块不可用 ({str(e)})")
    print("  请运行: pip install pyautogui pyperclip")
    pyautogui = cast(Any, None)
    pyperclip = cast(Any, None)


class AliyunCloudEffectAutomation:
    """阿里云效Web自动化控制"""
    
    def __init__(self, username, password, config_path=".bug-management-config.json"):
        """
        初始化自动化控制
        
        Args:
            username: 阿里云账号
            password: 阿里云密码
            config_path: 配置文件路径
        """
        self.username = username
        self.password = password
        self.config = self._load_config(config_path)
        self._driver: WebDriver | None = None
        self._wait: WebDriverWait | None = None
        self.screenshots_dir = Path("./bug-submission-screenshots")
        self.screenshots_dir.mkdir(exist_ok=True)

    @property
    def driver(self) -> WebDriver:
        """返回已初始化的浏览器驱动，未初始化时抛出明确错误。"""
        if self._driver is None:
            raise RuntimeError("浏览器驱动未初始化，请先调用 start_driver()")
        return self._driver

    @property
    def wait(self) -> WebDriverWait:
        """返回已初始化的显式等待对象，未初始化时抛出明确错误。"""
        if self._wait is None:
            raise RuntimeError("等待器未初始化，请先调用 start_driver()")
        return self._wait
    
    def _load_config(self, config_path):
        """加载配置文件"""
        config = {"cloudEffect": {"baseUrl": ""}}
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

        base_url = _read_env('CLOUD_EFFECT_BASE_URL')
        config.setdefault('cloudEffect', {})
        if base_url:
            config['cloudEffect']['baseUrl'] = base_url
        return config
    
    def _click_with_retry(self, by, value, max_retries=3):
        """带重试的点击，处理元素过时问题"""
        for attempt in range(max_retries):
            try:
                element = self.wait.until(EC.element_to_be_clickable((by, value)))
                element.click()
                return True
            except StaleElementReferenceException:
                print(f"  ⚠ 元素过时，重试 ({attempt + 1}/{max_retries})...")
                time.sleep(1)
            except Exception as e:
                print(f"  ✗ 点击失败: {str(e)}")
                return False
        return False
    
    def _take_screenshot(self, name):
        """拍摄截图"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bug_{name}_{timestamp}.png"
        filepath = self.screenshots_dir / filename
        
        try:
            self.driver.save_screenshot(str(filepath))
            print(f"✓ 截图已保存: {filepath}")
            return filepath
        except Exception as e:
            print(f"✗ 截图失败: {str(e)}")
            return None
    
    def start_driver(self):
        """启动浏览器驱动"""
        try:
            # 设置 Chrome 启动参数
            options = Options()
            # 无头模式（后台运行，不显示浏览器窗口）
            # options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")

            # 关键：隐藏自动化特征
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            # 添加真实浏览器的 user-agent
            options.add_argument(
                'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

            self._driver = webdriver.Chrome(options=options)
            # 关键：启动后立即执行 JS 隐藏 webdriver 属性
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
            })
            self.driver.maximize_window()
            self._wait = WebDriverWait(self.driver, 60)  # 增加到60秒超时
            print("✓ 浏览器驱动已启动（无头模式）")
            return True
        except Exception as e:
            print(f"✗ 启动浏览器驱动失败: {str(e)}")
            print("  请确保已安装ChromeDriver: https://chromedriver.chromium.org/")
            return False
    
    def login(self):
        """登录阿里云效系统"""
        try:
            print("正在登录阿里云效系统...")

            cloud_effect = self.config.get('cloudEffect', {})
            login_url = cloud_effect.get('loginUrl') or cloud_effect.get('baseUrl')
            if not login_url:
                print("✗ 未配置测试环境登录地址，请设置 CLOUD_EFFECT_LOGIN_URL 或 CLOUD_EFFECT_BASE_URL")
                return False
            
            self.driver.get(login_url)
            print("✓ 已打开登录页面")
            
            time.sleep(1)  # 减少到1秒
            # 切换到登录表单所在的 iframe
            print("正在切换到登录 iframe (alibaba-login-box)...")
            time.sleep(2)

            iframe = self.wait.until(
                EC.presence_of_element_located((By.ID, 'alibaba-login-box'))
            )
            self.driver.switch_to.frame(iframe)
            print("成功切换到 iframe")
            time.sleep(1)
            # 输入用户名
            print("正在输入用户名...")
            username_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="fm-login-id"]'))
            )
            username_input.click()
            time.sleep(0.5)
            # 逐个字符输入，模拟真人打字
            for char in self.username:
                username_input.send_keys(char)
                time.sleep(0.1)
            time.sleep(1)
            print("✓ 用户名输入完成")

            # 输入密码
            print("正在输入密码...")
            password_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//input[@name="fm-login-password"]'))
            )
            password_input.click()
            time.sleep(0.5)
            for char in self.password:
                password_input.send_keys(char)
                time.sleep(0.1)
            time.sleep(1)
            print("✓ 输入密码")
            
            # 点击登录按钮
            login_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, '//button[text()="立即登录"]'))
            )
            login_button.click()
            print("✓ 点击登录按钮")
            # 等待登录完成 - 等待URL包含devops
            print("退出 iframe，切换回主页面...")
            self.driver.switch_to.default_content()
            print("正在等待登录完成...")
            try:
                self.wait.until(
                    lambda driver: "devops" in driver.current_url or "account-devops" in driver.current_url
                )
                print("✓ 登录成功")
                time.sleep(2)
                # self._take_screenshot("login_success")
                return True
            except TimeoutException:
                print("✗ 登录超时 - 检查URL变化")
                print(f"   当前URL: {self.driver.current_url}")
                self._take_screenshot("login_timeout")
                # 再等一次，给更多时间
                time.sleep(3)
                if "devops" in self.driver.current_url or "account-devops" in self.driver.current_url:
                    print("✓ 登录成功（延迟确认）")
                    return True
                return False
                
        except TimeoutException:
            print("✗ 登录超时")
            self._take_screenshot("login_timeout")
            return False
        except Exception as e:
            print(f"✗ 登录异常: {str(e)}")
            self._take_screenshot("login_error")
            return False
    
    def navigate_to_bug_section(self, project_name):
        """导航到指定项目的缺陷页面
        
        Args:
            project_name: 项目名称，如 "IOT平台2.0"
        """
        time.sleep(2)
        try:
            print("点击左上角菜单")
            # 使用重试方式点击菜单
            if not self._click_with_retry(By.XPATH, "//span[@class='next-badge']"):
                print("✗ 无法点击菜单")
                return False

            print(f"正在导航到项目缺陷页面: {project_name}...")
            time.sleep(2)
            
            # 等待页面加载，点击菜单（如果需要）
            try:
                if not self._click_with_retry(By.XPATH, '//span[text()="项目协作"]'):
                    print("✓ 项目协作菜单已显示或不需要点击")
                else:
                    print("✓ 已点击项目协作菜单")
                time.sleep(2)
            except Exception as e:
                print(f"⚠ 菜单交互失败: {str(e)}")
            
            # 切换第二个标签页
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[1])
                print("✓ 已切换到新标签页")
                time.sleep(2)
            
            # 等待并点击"我参与的"
            try:
                if self._click_with_retry(By.XPATH, "//span[contains(text(), '我参与的')]"):
                    print("✓ 已点击'我参与的'")
                    time.sleep(2)
                else:
                    print("⚠ 未找到'我参与的'链接")
            except Exception as e:
                print(f"⚠ 未找到'我参与的'链接: {str(e)}")
            
            # 查找并点击指定项目
            project_xpath = f"//span[contains(text(), '{project_name}')]/../../../../.."
            print(f"正在查找项目: {project_name}")
            
            if self._click_with_retry(By.XPATH, project_xpath):
                print(f"✓ 已进入项目: {project_name}")
            else:
                print(f"✗ 无法进入项目: {project_name}")
                return False
            
            time.sleep(3)
            
            # 点击"缺陷"标签
            if self._click_with_retry(By.XPATH, "//div[contains(text(), '缺陷')] | //a[contains(text(), '缺陷')]"):
                print("✓ 已进入缺陷模块")
            else:
                print("✗ 无法进入缺陷模块")
                return False
            
            time.sleep(2)
            # self._take_screenshot("bug_section")
            
            return True
            
        except TimeoutException:
            print("✗ 导航超时")
            self._take_screenshot("navigation_timeout")
            return False
        except Exception as e:
            print(f"✗ 导航异常: {str(e)}")
            self._take_screenshot("navigation_error")
            return False
    
    def create_bug(self, bug_info):
        """创建缺陷
        
        Args:
            bug_info: 缺陷信息字典
                - title: 缺陷标题
                - expected_result: 预期结果
                - actual_result: 实际结果
                - attachment_path: 附件路径（可选）
        """
        try:
            print("正在创建缺陷...")
            
            # 点击新建按钮
            new_bug_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '新建')]"))
            )
            new_bug_button.click()
            print("✓ 已点击新建按钮")
            
            time.sleep(2)
            
            # 等待表单出现
            title_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, '请输入标题')]"))
            )
            
            # 填写标题
            title_input.clear()
            title_input.send_keys(bug_info.get('title', ''))
            print(f"✓ 已填写标题: {bug_info.get('title', '')}")
            
            time.sleep(1)
            
            # 填写预期结果
            try:
                print("正在定位预期结果编辑器包装器...")
                wrapper = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.projex-editor-content-wrapper'))
                )

                # 2. 查找内部真正可编辑的 div
                editable_div = wrapper.find_element(By.CSS_SELECTOR, 'div[data-cangjie-content="true"]')

                # 3. 先点击让光标进入编辑器
                editable_div.click()
                time.sleep(0.5)

                # 4. 使用 document.execCommand 插入文本（最安全，不会破坏图片节点）
                content = bug_info.get('expected_result', '')+"\n"
                script = """
                               var editor = arguments[0];
                               editor.focus();
                               document.execCommand('insertText', false, arguments[1]);
                               """
                self.driver.execute_script(script, editable_div, content)
                print(f"✓ 已通过 execCommand 安全注入预期结果")
                time.sleep(1)

            except Exception as e:
                print(f"⚠ 填写预期结果异常: {str(e)}")
                self._take_screenshot("expected_result_error")
            time.sleep(1)

            # 上传/粘贴多个文件（支持 attachment_path 或 attachment_paths）
            attachment_files = []
            if bug_info.get('attachment_paths'):
                # 新格式：多个文件列表
                attachment_files = bug_info.get('attachment_paths', [])
            elif bug_info.get('attachment_path'):
                # 兼容旧格式：单个文件
                attachment_files = [bug_info.get('attachment_path')]
            
            if attachment_files:
                print(f"\n【上传 {len(attachment_files)} 个文件】")
                for i, file_path in enumerate(attachment_files):
                    # 关键修改：由于预期结果已经填入，后续附件都应该是追加模式 (is_first=False)
                    is_first = False
                    print(f"正在处理文件 {i+1}/{len(attachment_files)}: {file_path}")
                    self._paste_content_to_description(file_path, is_first=is_first)
                    time.sleep(1)
            
            time.sleep(1)
            
            # 点击新建按钮提交
            submit_button = self.driver.find_element(By.XPATH, "//span[contains(text(), '继续新建下一个')]/../../../span/button/span[contains(text(), '新建')]")
            submit_button.click()
            print("✓ 已点击新建按钮提交")
            
            time.sleep(3)
            
            # self._take_screenshot("bug_created")
            
            return True
            
        except TimeoutException:
            print("✗ 创建缺陷超时")
            self._take_screenshot("bug_creation_timeout")
            return False
        except Exception as e:
            print(f"✗ 创建缺陷异常: {str(e)}")
            self._take_screenshot("bug_creation_error")
            return False
    
    def _paste_content_to_description(self, file_path, is_first=True):
        """将文件内容粘贴到描述文本框或上传附件
        
        Args:
            file_path: 文件路径
            is_first: 是否为第一个文件（True时清空现有内容）
        """
        try:
            if not Path(file_path).exists():
                print(f"⚠ 文件不存在: {file_path}")
                return False
            
            file_path_obj = Path(file_path)
            
            # 检查文件类型 - 如果是图片，使用上传方式
            image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
            if file_path_obj.suffix.lower() in image_extensions:
                print(f"ℹ 检测到图片文件，使用上传方式...")
                return self._upload_attachment(file_path)
            
            # 读取文件内容（先尝试 UTF-8，失败则尝试其他编码）
            content = None
            encodings = ['utf-8', 'gbk', 'gb2312', 'latin-1', 'utf-16']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    print(f"✓ 文件使用 {encoding} 编码读取成功")
                    break
                except (UnicodeDecodeError, LookupError):
                    continue
            
            if content is None:
                print(f"⚠ 无法以文本格式读取文件，尝试上传...")
                return self._upload_attachment(file_path)
            
            # 查找描述文本框（根据截图的定位）
            description_xpath = "//textarea[contains(@placeholder, '请输入描述')] | //div[contains(@class, 'editor-content')]//textarea"
            description_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, description_xpath))
            )
            
            # 将光标移动到文本框
            description_input.click()
            time.sleep(0.5)
            
            # 第一个文件时清空现有内容，之后的文件追加
            if is_first:
                description_input.clear()
                description_input.send_keys(content)
                print(f"✓ 已粘贴文件内容到描述框: {file_path}")
            else:
                # 追加内容（在末尾）
                description_input.send_keys("\n\n--- 文件 " + file_path_obj.name + " ---\n" + content)
                print(f"✓ 已追加文件内容: {file_path}")
            
            time.sleep(1)
            return True
            
        except Exception as e:
            print(f"⚠ 处理文件失败: {str(e)}")
            print(f"  尝试上传文件代替...")
            return self._upload_attachment(file_path)
    
    def _upload_attachment(self, file_path):
        """上传附件（图片或其他文件）
        
        点击工具栏的上传图片图标，然后通过PyAutoGUI选择文件
        """
        try:
            if not Path(file_path).exists():
                print(f"⚠ 附件文件不存在: {file_path}")
                return False
            
            # 检查PyAutoGUI是否可用
            if not PYAUTOGUI_AVAILABLE:
                print("✗ PyAutoGUI模块不可用，无法上传文件")
                print("  请运行: pip install pyautogui pyperclip")
                return False
            
            # 获取绝对路径
            abs_file_path = str(Path(file_path).resolve())
            
            # 第一步：点击上传图片图标（通过 aria-label 定位）
            print("正在点击工具栏上传图片图标...")
            picture_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//span[@aria-label='toolbar-picture']"))
            )
            picture_button.click()
            print("✓ 已点击上传图片图标")
            
            # 等待系统文件对话框打开
            print("等待文件对话框打开...")
            time.sleep(1)
            
            # 第二步：使用 PyAutoGUI + 剪贴板方式输入文件路径
            # 这是处理系统对话框最可靠的方法
            try:
                print(f"正在输入文件路径: {abs_file_path}")
                
                # 将文件路径复制到剪贴板
                pyperclip.copy(abs_file_path)
                print("✓ 已将路径复制到剪贴板")
                
                # 等待一下，让对话框完全加载
                time.sleep(0.5)
                
                # 模拟 Ctrl+V 粘贴
                pyautogui.hotkey('ctrl', 'v')
                print("✓ 已粘贴文件路径")
                
                time.sleep(0.5)
                
                # 按 Enter 确认
                pyautogui.press('enter')
                print("✓ 已按Enter确认")
                
                # 等待文件上传完成
                time.sleep(2)
                
                print(f"✓ 已上传文件: {abs_file_path}")
                return True
                
            except Exception as pyautogui_error:
                print(f"⚠ PyAutoGUI操作失败: {str(pyautogui_error)}")
                print("  尝试按Escape关闭对话框...")
                try:
                    pyautogui.press('escape')
                    time.sleep(1)
                except:
                    pass
                return False
            
        except Exception as e:
            print(f"⚠ 上传文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def assign_bug(self, assignee_name_or_email):
        """为缺陷指派负责人
        
        Args:
            assignee_name_or_email: 负责人邮箱或姓名（如 user@example.com 或 测试负责人）
        """
        try:
            print(f"正在为缺陷指派负责人: {assignee_name_or_email}...")
            
            time.sleep(2)
            
            # 查找负责人字段
            assignee_label = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), '负责人')]/../../div[2]"))
            )
            # 点击负责人输入框
            assignee_label.click()
            
            print("✓ 已点击负责人输入框")
            time.sleep(3)
            print("点击请输入关键字输入框")
            search_input = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='请输入关键字']"))
            )
            time.sleep(1)

            # 输入邮箱或姓名
            search_input.send_keys(assignee_name_or_email)
            print(f"✓ 已搜索负责人: {assignee_name_or_email}")
            
            time.sleep(2)
            
            # 等待下拉菜单出现并尝试选择匹配的选项
            try:
                # 使用新的定位表达式 - 查找包含负责人名字的div
                # option_xpath = f"//div[contains(text(), '{assignee_name_or_email}')]"
                # option = self.wait.until(
                #     EC.element_to_be_clickable((By.XPATH, option_xpath)),
                #     timeout=3
                # )
                # option.click()

                option_xpath = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[contains(text(), '{assignee_name_or_email}')]"))
                )
                option_xpath.click()

                print(f"✓ 已选择负责人: {assignee_name_or_email}")
                
                time.sleep(3)
                
                # 点击收起页面按钮
                print("点击收起页面按钮...")
                close_button = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@id='drawerCloseIcon']"))
                )
                close_button.click()
                print("✓ 已关闭BUG抽屉")
            except TimeoutException:
                print(f"⚠ 下拉选项未找到，尝试模糊匹配...")
                # 如果精确定位失败，查找包含该名字的第一个选项
                all_options = self.driver.find_elements(By.XPATH, 
                    "//div[contains(@class, 'ant-select-item-option')]")
                
                selected = False
                for opt in all_options:
                    opt_text = opt.text
                    if assignee_name_or_email.lower() in opt_text.lower():
                        opt.click()
                        print(f"✓ 已选择负责人: {opt_text}")
                        selected = True
                        time.sleep(1)
                        break
                
                if not selected:
                    print(f"⚠ 未找到匹配的负责人，尝试按回车确认...")
                    search_input.send_keys("\n")
                    print(f"✓ 已确认负责人: {assignee_name_or_email}")
            
            time.sleep(5)
            
            self._take_screenshot("bug_assigned")
            
            return True
            
        except TimeoutException:
            print("✗ 指派负责人超时")
            self._take_screenshot("assignment_timeout")
            return False
        except Exception as e:
            print(f"⚠ 指派负责人异常: {str(e)}")
            self._take_screenshot("assignment_error")
            return False
    
    def close_driver(self):
        """关闭浏览器"""
        if self._driver:
            self._driver.quit()
            print("✓ 浏览器已关闭")
    
    def get_current_url(self):
        """获取当前URL"""
        return self.driver.current_url
    
    def get_screenshots_dir(self):
        """获取截图目录"""
        return self.screenshots_dir


def main():
    """测试自动化流程"""
    username = _read_env('CLOUD_EFFECT_USERNAME')
    password = _read_env('CLOUD_EFFECT_PASSWORD')

    if not username or not password:
        print('✗ 缺少环境变量: CLOUD_EFFECT_USERNAME 或 CLOUD_EFFECT_PASSWORD')
        print('  请先设置测试环境登录凭据后再运行。')
        return
    
    automation = AliyunCloudEffectAutomation(username, password)
    
    try:
        # 启动浏览器
        if not automation.start_driver():
            return
        
        # 登录
        if not automation.login():
            print("登录失败，中止操作")
            return
        
        # 导航到缺陷页面
        if not automation.navigate_to_bug_section("IOT平台2.0"):
            print("导航失败，中止操作")
            return
        
        # 创建缺陷
        bug_info = {
            'title': '测试缺陷标题',
            'expected_result': '应该正常显示',
            'actual_result': '显示异常',
        }
        
        if not automation.create_bug(bug_info):
            print("创建缺陷失败")
            return
        
        # 指派负责人
        if not automation.assign_bug('user@example.com'):
            print("指派失败")
            return
        
        print("\n✓ 所有操作完成")
        print(f"✓ 截图已保存到: {automation.get_screenshots_dir()}")
        
    finally:
        automation.close_driver()


if __name__ == "__main__":
    main()
