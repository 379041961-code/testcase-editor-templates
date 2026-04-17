#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IOT平台UI自动化测试脚本
根据测试用例生成的自动化脚本
"""

import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import sys
import json
from datetime import datetime

class IOTAutoTest:
    def __init__(self, headless=False, save_session=False):
        self.driver = None
        self.wait = None
        self.test_cases = []
        self.headless = headless
        self.save_session = save_session
        self.log_file = f"test_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.log(f"自动化测试开始 - {datetime.now()}")
        
    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_msg + '\n')
    
    def setup(self):
        """初始化Chrome浏览器"""
        self.log("=== 初始化浏览器 ===")
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # 禁用GPU加速（可提高稳定性）
        chrome_options.add_argument('--disable-gpu')
        # 设置窗口大小
        chrome_options.add_argument('--window-size=1920,1080')
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        self.log("✓ 浏览器初始化完成")
        
    def load_testcases(self):
        """从Excel加载测试用例"""
        self.log("=== 加载测试用例 ===")
        wb = openpyxl.load_workbook('../excel/设备统计_测试用例.xlsx')
        ws = wb.active
        
        for row in ws.iter_rows(min_row=2, max_row=100, values_only=True):
            if row[0] is None:
                break
            case = {
                'id': row[0],
                'title': row[1],
                'precondition': row[2],
                'steps': row[3],
                'expected': row[4],
                'priority': row[5] if len(row) > 5 else '中'
            }
            self.test_cases.append(case)
            self.log(f"  └─ {case['id']}: {case['title']}")
        
        self.log(f"✓ 加载了 {len(self.test_cases)} 个测试用例")
    
    def find_element_safe(self, by, value, timeout=10):
        """安全地查找元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except:
            return None
    
    def find_clickable_element_safe(self, by, value, timeout=10):
        """安全地查找可点击的元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            return element
        except:
            return None
    
    def analyze_page_elements(self, xpath_patterns):
        """分析页面中匹配特定模式的元素"""
        results = {}
        for name, xpath in xpath_patterns.items():
            try:
                elements = self.driver.find_elements(By.XPATH, xpath)
                results[name] = {
                    'count': len(elements),
                    'elements': []
                }
                for i, elem in enumerate(elements[:3]):  # 只保存前3个
                    results[name]['elements'].append({
                        'tag': elem.tag_name,
                        'text': elem.text[:50] if elem.text else '',
                        'class': elem.get_attribute('class'),
                        'id': elem.get_attribute('id'),
                        'html': elem.get_attribute('outerHTML')[:150]
                    })
            except Exception as e:
                results[name] = {'error': str(e)}
        return results
    
    def save_page_source(self, filename=None):
        """保存页面源代码用于分析"""
        if filename is None:
            filename = f"page_source_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(self.driver.page_source)
        self.log(f"✓ 页面源代码已保存: {filename}")
        return filename
    
    def test_login(self):
        """TC_DS_001: 用户登录"""
        self.log("\n" + "="*80)
        self.log("执行用例: TC_DS_001 - 已登录IOT平台")
        self.log("="*80)
        
        try:
            self.log("步骤1: 打开登录页面")
            self.driver.get('https://iot.csmart-test.com/#/login')
            self.log(f"  当前URL: {self.driver.current_url}")
            time.sleep(3)
            
            # 分析登录页面元素
            self.log("分析登录页面元素...")
            login_elements = self.analyze_page_elements({
                '用户名输入框': "//input[@name='username' or @type='text' or contains(@placeholder, '用户')]",
                '密码输入框': "//input[@name='password' or @type='password']",
                '登录按钮': "//button[contains(text(), '登录')]",
                '验证码输入': "//input[contains(@placeholder, '验证码') or @name='captcha']"
            })
            
            self.log("步骤2: 输入账号和密码")
            username = self.find_element_safe(By.NAME, 'username', timeout=10)
            if not username:
                username = self.find_element_safe(By.XPATH, "//input[@type='text'][1]", timeout=10)
            
            if username:
                username.clear()
                username.send_keys('raolekang')
                self.log("  ✓ 输入账号: raolekang")
            else:
                self.log("  ✗ 未找到用户名输入框")
                return False
            
            password = self.find_element_safe(By.NAME, 'password', timeout=10)
            if not password:
                password = self.find_element_safe(By.XPATH, "//input[@type='password']", timeout=10)
            
            if password:
                password.clear()
                password.send_keys('Aa123456.')
                self.log("  ✓ 输入密码")
            else:
                self.log("  ✗ 未找到密码输入框")
                return False
            
            self.log("步骤3: 输入验证码（请在浏览器中手动输入，超时时间: 15秒）")
            captcha_input = self.find_element_safe(
                By.XPATH, "//input[contains(@placeholder, '验证码') or contains(@class, 'captcha')]", 
                timeout=2
            )
            
            if captcha_input:
                self.log("\n⏳ 等待验证码输入 (最多15秒)...")
                # 等待用户输入验证码（检查验证码字段是否被填充）
                for i in range(15):
                    captcha_text = captcha_input.get_attribute('value')
                    if captcha_text and len(captcha_text) >= 4:
                        self.log(f"  ✓ 检测到验证码输入: {'*' * len(captcha_text)}")
                        break
                    time.sleep(1)
                    if i % 5 == 0:
                        self.log(f"  继续等待... ({15-i}秒)")
                else:
                    self.log("  ⚠ 验证码输入超时")
            else:
                self.log("  ⚠ 未找到验证码输入框")
            
            self.log("步骤4: 勾选'记住我'并点击登录")
            # 尝试勾选'记住我'
            try:
                remember_checkbox = self.driver.find_element(
                    By.XPATH, "//input[@type='checkbox']"
                )
                if not remember_checkbox.is_selected():
                    remember_checkbox.click()
                    self.log("  ✓ 已勾选'记住我'")
            except:
                self.log("  ⚠ 未找到'记住我'复选框")
            
            # 点击登录按钮
            login_btn = self.find_clickable_element_safe(
                By.XPATH, "//span[contains(text(), '登 录')]",
                timeout=5
            )
            if login_btn:
                login_btn.click()
                self.log("  ✓ 已点击登录按钮")
            else:
                self.log("  ✗ 未找到登录按钮")
                return False
            
            # 等待登录成功
            self.log("等待登录成功...")
            try:
                WebDriverWait(self.driver, 10).until(
                    lambda driver: 'login' not in driver.current_url
                )
                time.sleep(2)
                self.log(f"✓ 登录成功，已跳转到: {self.driver.current_url}")
                return True
            except:
                self.log(f"✗ 登录超时或失败，当前URL: {self.driver.current_url}")
                self.save_page_source(f"login_failed_{datetime.now().strftime('%H%M%S')}.html")
                return False
                
        except Exception as e:
            self.log(f"✗ 登录测试异常: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def test_system_filter(self):
        """TC_DS_002: 全局筛选-系统切换"""
        self.log("\n" + "="*80)
        self.log("执行用例: TC_DS_002 - 全局筛选-系统切换展示正确")
        self.log("="*80)
        
        try:
            time.sleep(2)
            
            self.log("步骤1: 进入首页并分析筛选框")
            self.save_page_source(f"page_before_filter_{datetime.now().strftime('%H%M%S')}.html")
            
            # 分析筛选框相关元素
            filter_elements = self.analyze_page_elements({
                '系统筛选框': "//span[contains(text(), 'C-Smart') or contains(text(), '盘')]",
                '下拉框选项': "//div[contains(@class, 'dropdown') or contains(@class, 'select')]",
                '市场化盘': "//span[contains(text(), '市场化')]",
                '查询按钮': "//button[contains(text(), '查询')]"
            })
            
            self.log(f"找到的筛选相关元素: {json.dumps(filter_elements, ensure_ascii=False, indent=2)}")
            
            self.log("步骤2: 定位并点击系统筛选下拉框")
            filter_span = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'C-Smart') or contains(text(), '内部盘')]")
            
            if filter_span:
                elem = filter_span[0]
                self.log(f"  找到筛选框元素: {elem.tag_name}, 文本: {elem.text}")
                
                # 获取父元素（可能是可点击的)
                parent = elem.find_element(By.XPATH, "..")
                parent.click()
                self.log(f"  ✓ 已点击筛选框")
                time.sleep(1)
            else:
                self.log("  ✗ 未找到系统筛选框")
                return False
            
            self.log("步骤3: 选择'市场化盘'选项")
            market_options = self.driver.find_elements(By.XPATH, "//*[contains(text(), '市场化')]")
            if market_options:
                market_options[0].click()
                self.log("  ✓ 已选择'市场化盘'")
                time.sleep(1)
            else:
                self.log("  ✗ 未找到'市场化盘'选项")
                self.save_page_source(f"no_market_option_{datetime.now().strftime('%H%M%S')}.html")
            
            self.log("步骤4: 点击查询按钮")
            query_btn = self.find_clickable_element_safe(
                By.XPATH, "//button[contains(text(), '查询')]",
                timeout=5
            )
            if query_btn:
                query_btn.click()
                self.log("  ✓ 已点击查询按钮")
                time.sleep(2)
            else:
                self.log("  ✗ 未找到查询按钮")
                return False
            
            self.log("步骤5: 验证查询结果")
            page_html = self.driver.page_source
            if '暂无数据' in page_html:
                self.log("✓ 查询结果正确 - 显示'暂无数据'")
                return True
            else:
                self.log("⚠ 未显示'暂无数据'")
                self.save_page_source(f"query_result_{datetime.now().strftime('%H%M%S')}.html")
                return False
                
        except Exception as e:
            self.log(f"✗ 系统筛选测试异常: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def test_export_pdf(self):
        """TC_DS_003: 导出PDF文件"""
        self.log("\n" + "="*80)
        self.log("执行用例: TC_DS_003 - 导出PDF文件")
        self.log("="*80)
        
        try:
            self.log("步骤1: 查找导出按钮")
            export_btn = self.find_clickable_element_safe(
                By.XPATH, "//button[contains(text(), '导出')]",
                timeout=5
            )
            if export_btn:
                export_btn.click()
                self.log("  ✓ 已点击导出按钮")
                time.sleep(1)
            else:
                self.log("  ✗ 未找到导出按钮")
                return False
            
            self.log("步骤2: 选择PDF格式")
            pdf_options = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'PDF')]")
            if pdf_options:
                pdf_options[0].click()
                self.log("  ✓ 已选择PDF格式")
                time.sleep(1)
            else:
                self.log("  ✗ 未找到PDF选项")
                return False
            
            self.log("步骤3: 点击确定按钮")
            confirm_btn = self.find_clickable_element_safe(
                By.XPATH, "//button[contains(text(), '确定') or contains(text(), '确认')]",
                timeout=5
            )
            if confirm_btn:
                confirm_btn.click()
                self.log("  ✓ 已点击确定按钮")
                time.sleep(3)
                self.log("✓ 导出PDF成功")
                return True
            else:
                self.log("  ✗ 未找到确定按钮")
                return False
                
        except Exception as e:
            self.log(f"✗ 导出PDF测试异常: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def test_device_statistics(self):
        """TC_DS_004: 设备状态分布"""
        self.log("\n" + "="*80)
        self.log("执行用例: TC_DS_004 - 设备状态分布")
        self.log("="*80)
        
        try:
            time.sleep(2)
            self.save_page_source(f"page_before_chart_{datetime.now().strftime('%H%M%S')}.html")
            
            self.log("步骤1: 分析页面中的图表元素")
            chart_elements = self.analyze_page_elements({
                '4G手表相关': "//*[contains(text(), '4G') or contains(text(), '手表')]",
                '图表容器': "//div[contains(@class, 'chart') or contains(@class, 'graph')]",
                '查看详情按钮': "//*[contains(text(), '查看详情')]"
            })
            self.log(f"分析结果:\n{json.dumps(chart_elements, ensure_ascii=False, indent=2)}")
            
            self.log("步骤2: 查找并点击'4G手表'柱状图")
            
            # 首先查找与4G手表相关的元素
            watch_elements = self.driver.find_elements(
                By.XPATH, "//*[contains(text(), '4G') or contains(text(), '手表')]"
            )
            
            if not watch_elements:
                watch_elements = self.driver.find_elements(
                    By.XPATH, "//span[contains(., '4') or contains(., '手')]"
                )
            
            if watch_elements:
                self.log(f"  找到相关元素 {len(watch_elements)} 个")
                elem = watch_elements[0]
                self.log(f"  元素: {elem.tag_name}, 文本: {elem.text}, 类: {elem.get_attribute('class')}")
                
                # 尝试点击
                try:
                    elem.click()
                    self.log(f"  ✓ 已点击元素")
                    time.sleep(1)
                except:
                    # 如果直接点击失败，尝试用ActionChains
                    ActionChains(self.driver).move_to_element(elem).click().perform()
                    self.log(f"  ✓ 已通过ActionChains点击元素")
                    time.sleep(1)
            else:
                self.log("  ✗ 未找到'4G手表'相关元素")
                self.save_page_source(f"no_watch_element_{datetime.now().strftime('%H%M%S')}.html")
            
            self.log("步骤3: 等待并查找'查看详情'按钮")
            try:
                detail_btn = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "//*[contains(text(), '查看详情')]"))
                )
                self.log(f"  ✓ 找到'查看详情'按钮 (标签: {detail_btn.tag_name})")
                self.log(f"    HTML: {detail_btn.get_attribute('outerHTML')[:200]}")
                
                # 点击查看详情
                detail_btn.click()
                self.log("  ✓ 已点击'查看详情'")
                time.sleep(2)
                
                self.log("步骤4: 验证设备详情窗口已打开")
                detail_window = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[contains(text(), '设备详情') or contains(@class, 'detail')]"))
                )
                self.log("✓ 设备详情窗口已打开")
                self.save_page_source(f"device_detail_{datetime.now().strftime('%H%M%S')}.html")
                return True
                
            except Exception as e:
                self.log(f"  ⚠ 未能打开详情窗口: {e}")
                self.save_page_source(f"no_detail_window_{datetime.now().strftime('%H%M%S')}.html")
                return False
                
        except Exception as e:
            self.log(f"✗ 设备统计测试异常: {e}")
            import traceback
            self.log(traceback.format_exc())
            return False
    
    def run_all_tests(self):
        """执行所有测试"""
        results = {}
        
        try:
            self.setup()
            self.load_testcases()
            
            # 执行TC_DS_001: 登录
            results['TC_DS_001'] = self.test_login()
            
            # 如果登录成功，继续其他测试
            if results['TC_DS_001']:
                time.sleep(2)
                results['TC_DS_002'] = self.test_system_filter()
                
                if results['TC_DS_002']:
                    time.sleep(2)
                    results['TC_DS_003'] = self.test_export_pdf()
                
                if results['TC_DS_003']:
                    time.sleep(2)
                    results['TC_DS_004'] = self.test_device_statistics()
            else:
                self.log("\n⚠ 登录失败，跳过后续测试")
            
        except Exception as e:
            self.log(f"\n✗ 测试执行出现异常: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.teardown()
        
        self.print_summary(results)
        return results
    
    def print_summary(self, results):
        """打印测试总结"""
        self.log("\n" + "="*80)
        self.log("测试结果总结")
        self.log("="*80)
        
        for test_id in ['TC_DS_001', 'TC_DS_002', 'TC_DS_003', 'TC_DS_004']:
            if test_id in results:
                status = "✓ 通过" if results[test_id] else "✗ 失败"
                self.log(f"{test_id}: {status}")
            else:
                self.log(f"{test_id}: - (未执行)")
        
        pass_count = sum(1 for r in results.values() if r)
        total_count = len(results)
        self.log(f"\n总计: {pass_count}/{total_count} 测试通过")
        self.log(f"测试日志已保存: {self.log_file}")
    
    def teardown(self):
        """清理资源"""
        if self.driver:
            self.log("\n关闭浏览器...")
            try:
                self.driver.quit()
                self.log("✓ 浏览器已关闭")
            except:
                pass

if __name__ == '__main__':
    # 创建测试实例并运行
    # headless=True 可以在后台直接运行（不显示浏览器）
    # headless=False 会显示浏览器窗口
    tester = IOTAutoTest(headless=False, save_session=True)
    results = tester.run_all_tests()
