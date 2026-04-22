#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IOT 2.0 平台 UI 自动化测试脚本
测试用例来源：excel/设备统计_测试用例.xlsx
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import openpyxl
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# ─── 路径配置 ───────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parents[2]
EXCEL_PATH = ROOT_DIR / "excel" / "设备统计_测试用例.xlsx"
OUT_DIR = Path(__file__).resolve().parent
HTML_DIR = OUT_DIR / "html"   # HTML 快照保存目录
LOG_DIR  = OUT_DIR / "log"   # 日志文件保存目录

# ─── 系统配置 ───────────────────────────────────────────────
LOGIN_URL = "https://iot.csmart-test.com/#/login"
USERNAME = "raolekang"
PASSWORD = "Aa123456."


@dataclass
class TestCase:
    case_id: str
    title: str
    precondition: str
    steps: str
    expected: str
    priority: str


class IOTDeviceStatsAutomation:
    def __init__(self, headless: bool = False) -> None:
        self._driver: Optional[WebDriver] = None
        self._wait: Optional[WebDriverWait] = None
        self.headless = headless
        # 确保输出目录存在
        HTML_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = LOG_DIR / f"test_log_{ts}.txt"
        self.cases: List[TestCase] = []
        self.results: dict = {}

    # ─── 驱动属性访问器 ────────────────────────────────────────
    @property
    def driver(self) -> WebDriver:
        assert self._driver is not None, "Driver not initialized"
        return self._driver

    @property
    def wait(self) -> WebDriverWait:
        assert self._wait is not None, "Wait not initialized"
        return self._wait

    # ─── 日志 ────────────────────────────────────────────────
    def log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    # ─── 浏览器初始化 ────────────────────────────────────────
    def setup(self) -> None:
        self.log("=== 初始化浏览器 ===")
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        # 保持浏览器置顶，方便输入验证码
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        service = Service(ChromeDriverManager().install())
        self._driver = webdriver.Chrome(service=service, options=options)
        self._wait = WebDriverWait(self._driver, 20)
        self.log("✓ 浏览器已就绪")

    def teardown(self) -> None:
        if self._driver:
            self.log("关闭浏览器...")
            try:
                self._driver.quit()
            except Exception:
                pass
            self._driver = None
            self._wait = None

    # ─── 工具方法 ─────────────────────────────────────────────
    def save_html(self, tag: str) -> None:
        """保存页面源码用于调试"""
        path = HTML_DIR / f"{tag}_{datetime.now().strftime('%H%M%S')}.html"
        path.write_text(self.driver.page_source, encoding="utf-8")
        self.log(f"  页面已保存：html/{path.name}")

    def _try_find(self, by: str, value: str, timeout: float = 5) -> Optional[WebElement]:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
        except Exception:
            return None

    def _try_click(self, by: str, value: str, label: str = "", timeout: float = 8) -> bool:
        try:
            el = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((by, value))
            )
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            try:
                el.click()
            except Exception:
                ActionChains(self.driver).move_to_element(el).click().perform()
            self.log(f"  ✓ 点击：{label or value}")
            return True
        except Exception as e:
            self.log(f"  ✗ 未找到可点击元素：{label or value}  ({e})")
            return False

    def _click_echarts_bar(self, series_name: str) -> bool:
        """通过 JS 获取 ECharts 实例，找到指定名称的柱并触发 click 事件"""
        script = """
(function(name) {
    // 收集所有挂有 echarts 实例的 DOM
    var instances = [];
    var doms = document.querySelectorAll('[_echarts_instance_]');
    for (var i = 0; i < doms.length; i++) {
        try {
            var inst = echarts.getInstanceByDom(doms[i]);
            if (inst) instances.push({dom: doms[i], inst: inst});
        } catch(e) {}
    }
    if (instances.length === 0) return 'NO_INSTANCE';

    for (var ii = 0; ii < instances.length; ii++) {
        var inst = instances[ii].inst;
        var option = inst.getOption();
        // 在 xAxis categories 中找 name
        var xAxes = option.xAxis || [];
        if (!Array.isArray(xAxes)) xAxes = [xAxes];
        for (var xi = 0; xi < xAxes.length; xi++) {
            var cats = xAxes[xi].data || [];
            for (var di = 0; di < cats.length; di++) {
                var cat = (typeof cats[di] === 'object') ? cats[di].value : cats[di];
                if (cat && cat.indexOf(name) !== -1) {
                    inst.dispatchAction({type: 'click', seriesIndex: 0, dataIndex: di});
                    return 'CLICKED:' + cat + '@dataIndex=' + di;
                }
            }
        }
        // 也尝试 series name
        var series = option.series || [];
        for (var si = 0; si < series.length; si++) {
            if (series[si].name && series[si].name.indexOf(name) !== -1) {
                inst.dispatchAction({type: 'click', seriesIndex: si, dataIndex: 0});
                return 'CLICKED_SERIES:' + series[si].name;
            }
        }
    }
    return 'NOT_FOUND';
})(arguments[0]);
        """
        try:
            result = self.driver.execute_script(script, series_name)
            self.log(f"  ECharts JS 触发结果：{result}")
            return result is not None and result.startswith("CLICKED")
        except Exception as exc:
            self.log(f"  ECharts JS 执行失败：{exc}")
            return False

    def _analyze_elements(self, xpath: str, limit: int = 5) -> str:
        """抓取页面真实 HTML 片段辅助调试"""
        els = self.driver.find_elements(By.XPATH, xpath)
        snippets = []
        for el in els[:limit]:
            try:
                snippets.append(el.get_attribute("outerHTML")[:200])
            except Exception:
                pass
        return "\n".join(snippets) if snippets else "(无匹配元素)"

    # ─── 加载测试用例 ────────────────────────────────────────
    def load_testcases(self) -> None:
        self.log(f"=== 加载测试用例：{EXCEL_PATH} ===")
        wb = openpyxl.load_workbook(EXCEL_PATH)
        ws = wb.active
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not row[0]:
                continue
            self.cases.append(TestCase(
                case_id=str(row[0]),
                title=str(row[1] or ""),
                precondition=str(row[2] or ""),
                steps=str(row[3] or ""),
                expected=str(row[4] or ""),
                priority=str(row[5] or ""),
            ))
        self.log(f"✓ 共加载 {len(self.cases)} 条用例")
        for c in self.cases:
            self.log(f"   {c.case_id} | {c.title} | 优先级:{c.priority}")

    # ═══════════════════════════════════════════════════════════
    # TC_DS_001  登录
    # ═══════════════════════════════════════════════════════════
    def test_tc_ds_001_login(self) -> bool:
        self.log("\n" + "=" * 60)
        self.log("TC_DS_001  已登录 IOT 平台")
        self.log("=" * 60)

        try:
            # ① 打开登录页
            self.log("步骤1：打开登录页")
            self.driver.get(LOGIN_URL)
            time.sleep(3)
            self.save_html("login_page")

            # ② 分析输入框（先抓 HTML 结构）
            self.log("分析页面输入框...")
            self.log(self._analyze_elements("//input"))

            # ③ 输入账号
            self.log("步骤2：输入账号密码")
            username_locators = [
                (By.XPATH, "//input[@name='username']"),
                (By.XPATH, "//input[contains(@placeholder,'账号') or contains(@placeholder,'用户名')]"),
                (By.XPATH, "(//input[@type='text'])[1]"),
            ]
            username_el = None
            for by, val in username_locators:
                username_el = self._try_find(by, val, timeout=3)
                if username_el:
                    break
            if not username_el:
                self.log("  ✗ 未找到账号输入框")
                return False
            username_el.clear()
            username_el.send_keys(USERNAME)
            self.log(f"  ✓ 账号输入完成：{USERNAME}")

            # ④ 输入密码
            password_locators = [
                (By.XPATH, "//input[@name='password']"),
                (By.XPATH, "//input[@type='password']"),
            ]
            password_el = None
            for by, val in password_locators:
                password_el = self._try_find(by, val, timeout=3)
                if password_el:
                    break
            if not password_el:
                self.log("  ✗ 未找到密码输入框")
                return False
            password_el.clear()
            password_el.send_keys(PASSWORD)
            self.log("  ✓ 密码输入完成")

            # ⑤ 等待用户在浏览器中手动输入验证码（最多等待 15 秒）
            self.log("步骤3：等待验证码输入（最多 15 秒）...")
            captcha_el = self._try_find(By.XPATH, "//input[@id='form_item_verifyCode']", timeout=3)
            if not captcha_el:
                captcha_el = self._try_find(By.XPATH, "//input[contains(@placeholder,'验证码')]", timeout=3)
            if captcha_el:
                for i in range(15):
                    val = (captcha_el.get_attribute("value") or "").strip()
                    if len(val) >= 4:
                        self.log(f"  ✓ 检测到验证码已输入（{i+1}秒）")
                        break
                    time.sleep(1)
                else:
                    self.log("  ⚠ 15 秒内未检测到验证码，尝试继续登录")
            else:
                self.log("  ⚠ 未找到验证码输入框，跳过等待")

            # ⑥ 勾选"记住我"
            self.log("步骤3：勾选记住我")
            # 先抓取复选框相关 HTML
            self.log("  分析记住我相关元素：")
            self.log(self._analyze_elements("//*[contains(@class,'remember') or contains(text(),'记住')]"))
            self.log(self._analyze_elements("//input[@type='checkbox']"))

            remember_locators = [
                (By.XPATH, "//input[@type='checkbox']"),
                (By.XPATH, "//*[contains(text(),'记住我')]"),
                (By.XPATH, "//label[contains(.,'记住')]"),
            ]
            for by, val in remember_locators:
                try:
                    el = self.driver.find_element(by, val)
                    if el.is_displayed():
                        if el.tag_name == "input" and not el.is_selected():
                            el.click()
                        elif el.tag_name != "input":
                            el.click()
                        self.log("  ✓ 已勾选记住我")
                        break
                except Exception:
                    continue
            else:
                self.log("  ⚠ 未找到记住我复选框，跳过")

            # ⑦ 点击登录按钮
            self.log("步骤4：点击登录按钮")
            # 先抓按钮 HTML
            self.log("  分析按钮元素：")
            self.log(self._analyze_elements("//button"))

            login_clicked = False
            login_locators = [
                (By.XPATH, "//button[.//span[normalize-space()='登 录']]"),
                (By.XPATH, "//button[normalize-space()='登录' or normalize-space()='登 录']"),
                (By.XPATH, "//span[normalize-space()='登 录' or normalize-space()='登录']"),
                (By.XPATH, "//button[@type='submit']"),
                (By.XPATH, "(//button)[last()]"),
            ]
            for by, val in login_locators:
                if self._try_click(by, val, label="登录按钮"):
                    login_clicked = True
                    break
            if not login_clicked:
                self.log("  ✗ 未能点击登录按钮")
                self.save_html("login_btn_failed")
                return False

            # ⑧ 等待跳转
            self.log("等待登录跳转...")
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda d: "login" not in d.current_url
                )
                self.log(f"✓ 登录成功，当前 URL：{self.driver.current_url}")
                return True
            except TimeoutException:
                # 可能验证码错误，保存页面
                self.save_html("login_failed")
                error_msgs = self.driver.find_elements(
                    By.XPATH, "//*[contains(@class,'error') or contains(@class,'msg')]"
                )
                for em in error_msgs[:3]:
                    if em.text:
                        self.log(f"  页面提示：{em.text}")
                self.log("✗ 登录失败（可能验证码错误）")
                return False

        except Exception as exc:
            import traceback
            self.log(f"✗ 登录异常：{exc}")
            self.log(traceback.format_exc())
            self.save_html("login_exception")
            return False

    # ═══════════════════════════════════════════════════════════
    # TC_DS_002  全局筛选 - 系统切换
    # ═══════════════════════════════════════════════════════════
    def test_tc_ds_002_system_filter(self) -> bool:
        self.log("\n" + "=" * 60)
        self.log("TC_DS_002  全局筛选-系统切换展示正确")
        self.log("=" * 60)

        try:
            time.sleep(2)
            self.save_html("before_filter")

            # 步骤1：确认默认显示 C-Smart内部盘
            self.log("步骤1：验证筛选框默认值")
            self.log("  分析顶部筛选相关 span 元素：")
            self.log(self._analyze_elements("//span[contains(text(),'C-Smart') or contains(text(),'内部盘') or contains(text(),'市场')]"))

            default_locators = [
                (By.XPATH, "//span[normalize-space()='C-Smart内部盘']"),
                (By.XPATH, "//*[normalize-space()='C-Smart内部盘']"),
                (By.XPATH, "//*[contains(normalize-space(),'内部盘')]"),
            ]
            default_el = None
            for by, val in default_locators:
                default_el = self._try_find(by, val, timeout=5)
                if default_el:
                    self.log(f"  ✓ 默认选中：{default_el.text}")
                    break
            if not default_el:
                self.log("  ✗ 未找到默认筛选框 'C-Smart内部盘'")
                return False

            # 步骤2：点击筛选下拉
            self.log("步骤2：点击系统下拉框")
            # 尝试点击 span 本身或其父容器
            clicked = False
            for by, val in [
                (By.XPATH, "//span[normalize-space()='C-Smart内部盘']"),
                (By.XPATH, "//span[normalize-space()='C-Smart内部盘']/.."),
                (By.XPATH, "//*[contains(normalize-space(),'内部盘')]"),
            ]:
                if self._try_click(by, val, label="系统下拉框"):
                    clicked = True
                    break
            if not clicked:
                self.log("  ✗ 无法打开下拉框")
                return False
            time.sleep(1)

            # 步骤3：选择市场化盘
            self.log("步骤3：选择【市场化盘】")
            self.log("  分析下拉选项：")
            self.log(self._analyze_elements("//*[contains(text(),'市场')]"))

            if not self._try_click(By.XPATH, "//*[normalize-space()='市场化盘']", label="市场化盘"):
                self.log("  ✗ 未找到【市场化盘】选项")
                self.save_html("no_market_option")
                return False
            time.sleep(1)

            # 步骤4：点击查询
            self.log("步骤4：点击查询按钮")
            self.log("  分析查询按钮：")
            self.log(self._analyze_elements("//button[contains(.,'查询')]"))

            query_clicked = False
            for by, val in [
                (By.XPATH, "//button[contains(normalize-space(),'查') and contains(normalize-space(),'询')]"),
                (By.XPATH, "//span[contains(normalize-space(),'查') and contains(normalize-space(),'询')]/ancestor::button[1]"),
                (By.XPATH, "//*[contains(normalize-space(),'查') and contains(normalize-space(),'询')]"),
            ]:
                if self._try_click(by, val, label="查询按钮"):
                    query_clicked = True
                    break
            if not query_clicked:
                self.log("  ✗ 未找到查询按钮")
                return False
            time.sleep(2)

            # 步骤5：验证结果
            self.log("步骤5：验证结果")
            if "暂无数据" in self.driver.page_source:
                self.log("✓ 页面显示【暂无数据】，用例通过")
                return True
            else:
                self.save_html("filter_result")
                self.log("⚠ 页面未出现【暂无数据】，请人工确认结果")
                return False

        except Exception as exc:
            import traceback
            self.log(f"✗ TC_DS_002 异常：{exc}")
            self.log(traceback.format_exc())
            self.save_html("filter_exception")
            return False

    # ═══════════════════════════════════════════════════════════
    # TC_DS_003  导出 PDF
    # ═══════════════════════════════════════════════════════════
    def test_tc_ds_003_export_pdf(self) -> bool:
        self.log("\n" + "=" * 60)
        self.log("TC_DS_003  导出 PDF 文件")
        self.log("=" * 60)

        try:
            # 先抓导出相关按钮 HTML
            self.log("  分析导出按钮：")
            self.log(self._analyze_elements("//*[contains(text(),'导出')]"))

            # 点击导出
            if not self._try_click(
                By.XPATH,
                "//*[normalize-space()='导出' or normalize-space()='导 出']",
                label="导出按钮"
            ):
                self.log("  ✗ 未找到导出按钮")
                return False
            time.sleep(1)

            # 选 PDF
            self.log("  分析 PDF 选项：")
            self.log(self._analyze_elements("//*[contains(text(),'PDF') or contains(text(),'pdf')]"))

            if not self._try_click(By.XPATH, "//*[contains(normalize-space(),'PDF')]", label="PDF选项"):
                self.log("  ✗ 未找到 PDF 选项")
                self.save_html("no_pdf_option")
                return False
            time.sleep(0.5)

            # 点击确定
            confirmed = False
            for by, val in [
                (By.XPATH, "//button[contains(normalize-space(),'确') and contains(normalize-space(),'定')]"),
                (By.XPATH, "//button[contains(normalize-space(),'确') and contains(normalize-space(),'认')]"),
                (By.XPATH, "//*[contains(normalize-space(),'确') and (contains(normalize-space(),'定') or contains(normalize-space(),'认'))]"),
            ]:
                if self._try_click(by, val, label="确定按钮"):
                    confirmed = True
                    break
            if not confirmed:
                self.log("  ✗ 未找到确定按钮")
                return False

            time.sleep(3)
            self.log("✓ 导出操作完成")
            return True

        except Exception as exc:
            import traceback
            self.log(f"✗ TC_DS_003 异常：{exc}")
            self.log(traceback.format_exc())
            self.save_html("export_exception")
            return False

    # ═══════════════════════════════════════════════════════════
    # TC_DS_004  设备状态分布柱状图
    # ═══════════════════════════════════════════════════════════
    def test_tc_ds_004_device_distribution(self) -> bool:
        self.log("\n" + "=" * 60)
        self.log("TC_DS_004  设备状态分布")
        self.log("=" * 60)

        try:
            time.sleep(2)
            self.save_html("before_device_dist")

            # 分析 4G手表 相关元素
            self.log("步骤1：分析柱状图中的 4G手表 元素")
            self.log(self._analyze_elements("//*[contains(text(),'4G') or contains(text(),'手表')]"))
            self.log(self._analyze_elements("//canvas"))
            self.log(self._analyze_elements("//div[contains(@class,'chart') or contains(@class,'echarts')]"))

            # 点击 4G手表 柱 —— 优先尝试文字定位，失败则用 JS 触发 ECharts 点击
            clicked = False
            for by, val in [
                (By.XPATH, "//*[normalize-space()='4G手表']"),
                (By.XPATH, "//*[contains(normalize-space(),'4G手表')]"),
                (By.XPATH, "//*[contains(text(),'4G') and contains(text(),'手表')]"),
            ]:
                if self._try_click(by, val, label="4G手表柱状图", timeout=5):
                    clicked = True
                    break

            if not clicked:
                self.log("  ⚠ 未找到文字元素，尝试通过 JS 触发 ECharts 点击 4G手表")
                self.save_html("no_4g_watch_element")
                clicked = self._click_echarts_bar("4G手表")
                time.sleep(2)

            # 步骤2：等待弹窗并抓取其 HTML 结构
            time.sleep(1)
            self.log("步骤2：分析点击后出现的弹窗")
            self.log(self._analyze_elements("//*[contains(text(),'查看详情')]"))
            self.log(self._analyze_elements("//*[contains(@class,'popup') or contains(@class,'modal') or contains(@class,'dialog')]"))

            # 点击查看详情
            self.log("步骤3：点击查看详情")
            # 先抓取其真实 HTML 以确定标签类型
            detail_els = self.driver.find_elements(By.XPATH, "//*[normalize-space()='查看详情']")
            for el in detail_els[:3]:
                self.log(f"  查看详情候选 tag={el.tag_name} html={el.get_attribute('outerHTML')[:200]}")

            detail_clicked = False
            for by, val in [
                (By.XPATH, "//*[normalize-space()='查看详情']"),
                (By.XPATH, "//*[contains(normalize-space(),'查看详情')]"),
            ]:
                if self._try_click(by, val, label="查看详情", timeout=8):
                    detail_clicked = True
                    break

            if not detail_clicked:
                self.log("  ✗ 未找到查看详情按钮")
                self.save_html("no_detail_btn")
                return False

            # 步骤4：验证设备详情窗口
            time.sleep(2)
            self.save_html("after_detail_click")
            if "设备详情" in self.driver.page_source:
                self.log("✓ 设备详情窗口已打开")
                return True
            else:
                self.log("⚠ 未检测到【设备详情】字样，请人工确认")
                return False

        except Exception as exc:
            import traceback
            self.log(f"✗ TC_DS_004 异常：{exc}")
            self.log(traceback.format_exc())
            self.save_html("device_dist_exception")
            return False

    # ─── 主流程 ───────────────────────────────────────────────
    def run(self) -> dict:
        self.setup()
        self.load_testcases()

        try:
            self.results["TC_DS_001"] = self.test_tc_ds_001_login()
            if not self.results["TC_DS_001"]:
                self.log("⚠ 登录失败，停止后续用例")
                return self.results

            time.sleep(2)
            self.results["TC_DS_002"] = self.test_tc_ds_002_system_filter()
            time.sleep(2)
            self.results["TC_DS_003"] = self.test_tc_ds_003_export_pdf()
            time.sleep(2)
            self.results["TC_DS_004"] = self.test_tc_ds_004_device_distribution()

        except Exception as exc:
            import traceback
            self.log(f"✗ 总体异常：{exc}")
            self.log(traceback.format_exc())
        finally:
            self.teardown()
            self._print_summary()

        return self.results

    def _print_summary(self) -> None:
        self.log("\n" + "=" * 60)
        self.log("测试结果汇总")
        self.log("=" * 60)
        name_map = {
            "TC_DS_001": "已登录IOT平台",
            "TC_DS_002": "全局筛选-系统切换",
            "TC_DS_003": "导出PDF文件",
            "TC_DS_004": "设备状态分布",
        }
        passed = 0
        for cid, title in name_map.items():
            if cid in self.results:
                flag = "✓ 通过" if self.results[cid] else "✗ 失败"
                self.log(f"  {cid} [{title}]: {flag}")
                if self.results[cid]:
                    passed += 1
            else:
                self.log(f"  {cid} [{title}]: - 未执行")
        total = len(self.results)
        self.log(f"\n  通过率：{passed}/{total}")
        self.log(f"  日志文件：{self.log_file}")


def main() -> int:
    runner = IOTDeviceStatsAutomation(headless=False)
    results = runner.run()
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    return 0 if total > 0 and passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
