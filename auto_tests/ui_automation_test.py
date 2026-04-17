import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import sys

class IOTAutoTest:
    def __init__(self):
        self.driver = None
        self.wait = None
        self.test_cases = []
        
    def setup(self):
        """初始化Chrome浏览器"""
        chrome_options = Options()
        # chrome_options.add_argument('--headless')  # 取消注释可后台运行
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)
        
    def load_testcases(self):
        """从Excel加载测试用例"""
        wb = openpyxl.load_workbook('../excel/设备统计_测试用例.xlsx')
        ws = wb.active
        
        for row in ws.iter_rows(min_row=2, max_row=100, values_only=True):
            if row[0] is None:  # 用例ID为空，则停止
                break
            case = {
                'id': row[0],
                'title': row[1],
                'precondition': row[2],
                'steps': row[3],
                'expected': row[4],
                'priority': row[5]
            }
            self.test_cases.append(case)
        print(f"✓ 加载了 {len(self.test_cases)} 个测试用例")
        
    def analyze_page_structure(self):
        """分析页面HTML结构"""
        print("\n" + "="*80)
        print("分析页面结构...")
        print("="*80)
        
        # 等待页面加载
        time.sleep(2)
        
        # 获取当前URL和标题
        print(f"当前URL: {self.driver.current_url}")
        print(f"页面标题: {self.driver.title}")
        
        # 获取页面的某些关键元素信息
        try:
            # 检查系统筛选下拉框
            filter_elements = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'C-Smart内部盘')]")
            print(f"\n找到系统筛选元素数量: {len(filter_elements)}")
            for elem in filter_elements[:3]:  # 打印前3个
                print(f"  - 元素: {elem.tag_name}, 文本: {elem.text}")
                print(f"    HTML: {elem.get_attribute('outerHTML')[:150]}")
                
        except Exception as e:
            print(f"分析筛选框失败: {e}")
        
    def test_login(self):
        """TC_DS_001: 登录测试"""
        print("\n" + "="*80)
        print("执行 TC_DS_001: 已登录IOT平台")
        print("="*80)
        
        try:
            self.driver.get('https://iot.csmart-test.com/#/login')
            
            # 等待登录表单加载
            self.wait.until(EC.presence_of_element_located((By.NAME, 'username')))
            
            # 输入账号
            username_field = self.driver.find_element(By.NAME, 'username')
            username_field.clear()
            username_field.send_keys('raolekang')
            print("✓ 输入账号: raolekang")
            
            # 输入密码
            password_field = self.driver.find_element(By.NAME, 'password')
            password_field.clear()
            password_field.send_keys('Aa123456.')
            print("✓ 输入密码")
            
            # 等待用户输入验证码（最多15秒）
            print("\n⏳ 等待用户输入验证码（最多15秒）...")
            time.sleep(2)
            
            # 检查并勾选"记住我"
            try:
                remember_me = self.driver.find_element(By.XPATH, "//input[@type='checkbox' and @name='remember']")
                if not remember_me.is_selected():
                    remember_me.click()
                    print("✓ 已勾选'记住我'")
            except:
                print("⚠ 未找到'记住我'复选框")
            
            # 点击登录按钮
            login_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), '登录')]")))
            login_btn.click()
            print("✓ 点击登录按钮")
            
            # 等待登录成功（重定向到首页）
            self.wait.until(EC.url_changes(self.driver.current_url))
            time.sleep(3)
            
            current_url = self.driver.current_url
            if 'login' not in current_url:
                print(f"✓ 登录成功，已跳转到: {current_url}")
                return True
            else:
                print("✗ 登录失败，仍在登录页面")
                return False
                
        except Exception as e:
            print(f"✗ 登录测试失败: {e}")
            return False
    
    def test_system_filter(self):
        """TC_DS_002: 系统筛选-系统切换"""
        print("\n" + "="*80)
        print("执行 TC_DS_002: 全局筛选-系统切换展示正确")
        print("="*80)
        
        try:
            # 等待首页加载
            time.sleep(2)
            
            # 查找系统筛选下拉框
            print("查找系统筛选下拉框...")
            
            # 先尝试找到下拉框的容器
            try:
                filter_wrapper = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[contains(@class, 'system-filter') or contains(@class, 'select')]")))
                print(f"✓ 找到筛选框容器")
            except:
                print("⚠ 未找到特定class的筛选框，尝试其他定位方式")
            
            # 查找当前显示的系统（应该是C-Smart内部盘）
            current_system = self.driver.find_elements(By.XPATH, "//span[contains(text(), 'C-Smart') or contains(text(), '内部盘')]")
            print(f"找到相关元素: {len(current_system)} 个")
            
            if current_system:
                elem = current_system[0]
                print(f"✓ 当前系统显示: {elem.text}")
                print(f"  元素标签: {elem.tag_name}")
                print(f"  元素HTML: {elem.get_attribute('outerHTML')[:200]}")
                
                # 获取父元素信息（可能是可点击的)
                parent = elem.find_element(By.XPATH, "..")
                print(f"  父元素: {parent.tag_name}, class: {parent.get_attribute('class')}")
                
                # 尝试点击下拉框打开选项
                try:
                    parent.click()
                    print("✓ 已点击筛选框，打开选项")
                    time.sleep(1)
                    
                    # 查找市场化盘选项
                    market_option = self.wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "//span[text()='市场化盘' or contains(text(), '市场化')]")))
                    print(f"✓ 找到'市场化盘'选项")
                    market_option.click()
                    print("✓ 已切换到'市场化盘'")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"⚠ 切换系统失败: {e}")
                    return False
            
            # 点击查询按钮
            try:
                query_btn = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), '查询')]")))
                query_btn.click()
                print("✓ 已点击查询按钮")
                time.sleep(2)
                
                # 检查结果
                page_html = self.driver.page_source
                if '暂无数据' in page_html:
                    print("✓ 显示'暂无数据'，符合预期")
                    return True
                else:
                    print("⚠ 未显示'暂无数据'")
                    return False
                    
            except Exception as e:
                print(f"⚠ 点击查询按钮失败: {e}")
                return False
                
        except Exception as e:
            print(f"✗ 系统筛选测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_export_pdf(self):
        """TC_DS_003: 导出PDF文件"""
        print("\n" + "="*80)
        print("执行 TC_DS_003: 导出PDF文件")
        print("="*80)
        
        try:
            # 查找导出按钮
            export_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), '导出')]")))
            export_btn.click()
            print("✓ 已点击导出按钮")
            time.sleep(1)
            
            # 查找PDF选项
            pdf_option = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//span[text()='PDF' or contains(text(), 'PDF')]")))
            pdf_option.click()
            print("✓ 已选择PDF格式")
            time.sleep(1)
            
            # 查找确定按钮
            confirm_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(text(), '确定') or contains(text(), '确认')]")))
            confirm_btn.click()
            print("✓ 已点击确定按钮")
            
            # 等待文件下载
            time.sleep(3)
            print("✓ 导出PDF成功")
            return True
            
        except Exception as e:
            print(f"✗ 导出PDF测试失败: {e}")
            return False
    
    def test_device_statistics(self):
        """TC_DS_004: 设备状态分布图表交互"""
        print("\n" + "="*80)
        print("执行 TC_DS_004: 设备状态分布")
        print("="*80)
        
        try:
            time.sleep(2)
            
            # 查找4G手表柱状图并点击
            print("查找'4G手表'柱状图...")
            
            # 首先分析图表的HTML结构
            chart_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '4G') or contains(text(), '手表')]")
            print(f"找到相关元素: {len(chart_elements)} 个")
            
            if chart_elements:
                # 打印HTML结构
                for i, elem in enumerate(chart_elements[:3]):
                    print(f"\n元素 {i+1}:")
                    print(f"  标签: {elem.tag_name}")
                    print(f"  文本: {elem.text}")
                    print(f"  HTML: {elem.get_attribute('outerHTML')[:300]}")
                    
                    # 尝试点击第一个元素
                    if i == 0:
                        try:
                            elem.click()
                            print("✓ 已点击'4G手表'元素")
                            time.sleep(1)
                        except:
                            print("⚠ 点击失败，尝试其他方式")
            
            # 等待弹窗出现
            try:
                detail_btn = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), '查看详情')]")), timeout=5)
                print(f"✓ 找到'查看详情'按钮（标签: {detail_btn.tag_name}）")
                print(f"  HTML: {detail_btn.get_attribute('outerHTML')[:200]}")
                
                # 点击查看详情
                detail_btn.click()
                print("✓ 已点击'查看详情'")
                time.sleep(2)
                
                # 检查是否打开设备详情窗口
                detail_window = self.wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), '设备详情') or contains(@class, 'detail')]")), timeout=5)
                print("✓ 设备详情窗口已打开")
                return True
                
            except Exception as e:
                print(f"⚠ 未找到或打开详情窗口: {e}")
                # 继续，不中断测试
                return False
                
        except Exception as e:
            print(f"✗ 设备统计测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run_all_tests(self):
        """执行所有测试"""
        print("\n" + "="*80)
        print("IOT平台自动化测试开始")
        print("="*80)
        
        results = {}
        
        try:
            self.setup()
            self.load_testcases()
            
            # TC_DS_001: 登录
            results['TC_DS_001'] = self.test_login()
            
            # TC_DS_002: 系统筛选
            if results['TC_DS_001']:
                results['TC_DS_002'] = self.test_system_filter()
            
            # TC_DS_003: 导出PDF
            if results['TC_DS_002']:
                results['TC_DS_003'] = self.test_export_pdf()
            
            # TC_DS_004: 设备统计
            if results['TC_DS_003']:
                results['TC_DS_004'] = self.test_device_statistics()
            
        except Exception as e:
            print(f"\n✗ 测试执行异常: {e}")
            import traceback
            traceback.print_exc()
        finally:
            self.teardown()
        
        # 打印总结
        self.print_summary(results)
    
    def print_summary(self, results):
        """打印测试总结"""
        print("\n" + "="*80)
        print("测试结果总结")
        print("="*80)
        for case_id, result in results.items():
            status = "✓ 通过" if result else "✗ 失败"
            print(f"{case_id}: {status}")
        
        pass_count = sum(1 for r in results.values() if r)
        total_count = len(results)
        print(f"\n总体: {pass_count}/{total_count} 通过")
    
    def teardown(self):
        """清理资源"""
        if self.driver:
            print("\n关闭浏览器...")
            self.driver.quit()

if __name__ == '__main__':
    tester = IOTAutoTest()
    tester.run_all_tests()
