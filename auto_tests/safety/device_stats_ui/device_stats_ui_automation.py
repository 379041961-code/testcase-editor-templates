#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
IOT 2.0 平台 UI 自动化测试脚本
测试用例来源：excel/设备统计_测试用例.xlsx

安全说明：
1. 登录账号、密码必须从环境变量读取（IOT_TEST_USERNAME / IOT_TEST_PASSWORD）。
2. 仅执行正常 UI 测试流程，不包含高危系统操作。
"""

from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

import openpyxl
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

OUT_DIR = Path(__file__).resolve().parent
ROOT_DIR = OUT_DIR.parents[2]
EXCEL_PATH = ROOT_DIR / "excel" / "设备统计_测试用例.xlsx"
HTML_DIR = OUT_DIR / "html"
LOG_DIR = OUT_DIR / "log"

LOGIN_URL = "https://iot.csmart-test.com/#/login"
USERNAME_ENV = "IOT_TEST_USERNAME"
PASSWORD_ENV = "IOT_TEST_PASSWORD"


def _read_env(name: str) -> str:
    return os.getenv(name, "").strip().strip('"').strip("'")


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

        HTML_DIR.mkdir(parents=True, exist_ok=True)
        LOG_DIR.mkdir(parents=True, exist_ok=True)

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = LOG_DIR / f"test_log_{ts}.txt"
        self.cases: List[TestCase] = []
        self.results: dict[str, bool] = {}

        self.username = _read_env(USERNAME_ENV)
        self.password = _read_env(PASSWORD_ENV)

    @property
    def driver(self) -> WebDriver:
        assert self._driver is not None, "Driver not initialized"
        return self._driver

    @property
    def wait(self) -> WebDriverWait:
        assert self._wait is not None, "Wait not initialized"
        return self._wait

    def log(self, msg: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}"
        print(line)
        with self.log_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def setup(self) -> None:
        self.log("=== 初始化浏览器 ===")
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
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

    def save_html(self, tag: str) -> None:
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
            self.log(f"  ✗ 未找到可点击元素：{label or value} ({e})")
            return False

    def _analyze_elements(self, xpath: str, limit: int = 5) -> str:
        els = self.driver.find_elements(By.XPATH, xpath)
        snippets = []
        for el in els[:limit]:
            try:
                outer_html = el.get_attribute("outerHTML") or ""
                snippets.append(outer_html[:200])
            except Exception:
                pass
        return "\n".join(snippets) if snippets else "(无匹配元素)"

    def _click_echarts_bar(self, series_name: str) -> bool:
        script = """
(function(name) {
    var doms = document.querySelectorAll('[_echarts_instance_]');
    if (!doms || doms.length === 0) return 'NO_INSTANCE';

    for (var i = 0; i < doms.length; i++) {
        try {
            var inst = echarts.getInstanceByDom(doms[i]);
            if (!inst) continue;

            var option = inst.getOption();
            var xAxes = option.xAxis || [];
            if (!Array.isArray(xAxes)) xAxes = [xAxes];

            for (var xi = 0; xi < xAxes.length; xi++) {
                var cats = xAxes[xi].data || [];
                for (var di = 0; di < cats.length; di++) {
                    var cat = (typeof cats[di] === 'object') ? cats[di].value : cats[di];
                    if (cat && cat.indexOf(name) !== -1) {
                        inst.dispatchAction({type: 'click', seriesIndex: 0, dataIndex: di});
                        return 'CLICKED:' + cat;
                    }
                }
            }
        } catch (e) {}
    }

    return 'NOT_FOUND';
})(arguments[0]);
        """
        try:
            result = self.driver.execute_script(script, series_name)
            self.log(f"  ECharts JS 触发结果：{result}")
            return bool(result) and str(result).startswith("CLICKED")
        except Exception as exc:
            self.log(f"  ECharts JS 执行失败：{exc}")
            return False

    def _validate_credentials(self) -> bool:
        self.username = _read_env(USERNAME_ENV)
        self.password = _read_env(PASSWORD_ENV)
        if not self.username or not self.password:
            self.log("✗ 未检测到登录凭据，请先设置环境变量：")
            self.log(f"  set {USERNAME_ENV}=你的账号")
            self.log(f"  set {PASSWORD_ENV}=你的密码")
            return False
        return True

    def load_testcases(self) -> None:
        self.log(f"=== 加载测试用例：{EXCEL_PATH} ===")
        wb = openpyxl.load_workbook(EXCEL_PATH)
        ws = wb.active
        if ws is None:
            raise ValueError(f"未找到可用工作表：{EXCEL_PATH}")
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
        for case in self.cases:
            self.log(f"   {case.case_id} | {case.title} | 优先级:{case.priority}")

    def test_tc_ds_001_login(self) -> bool:
        self.log("\n" + "=" * 60)
        self.log("TC_DS_001 已登录 IOT 平台")
        self.log("=" * 60)

        if not self._validate_credentials():
            return False

        try:
            self.log("步骤1：打开登录页")
            self.driver.get(LOGIN_URL)
            time.sleep(3)
            self.save_html("login_page")

            self.log("步骤2：输入账号密码")
            username_el = None
            for by, val in [
                (By.XPATH, "//input[@name='username']"),
                (By.XPATH, "//input[contains(@placeholder,'账号') or contains(@placeholder,'用户名')]"),
                (By.XPATH, "(//input[@type='text'])[1]"),
            ]:
                username_el = self._try_find(by, val, timeout=3)
                if username_el:
                    break
            if not username_el:
                self.log("  ✗ 未找到账号输入框")
                return False
            username_el.clear()
            username_el.send_keys(self.username)
            self.log("  ✓ 账号输入完成")

            password_el = None
            for by, val in [
                (By.XPATH, "//input[@name='password']"),
                (By.XPATH, "//input[@type='password']"),
            ]:
                password_el = self._try_find(by, val, timeout=3)
                if password_el:
                    break
            if not password_el:
                self.log("  ✗ 未找到密码输入框")
                return False
            password_el.clear()
            password_el.send_keys(self.password)
            self.log("  ✓ 密码输入完成")

            self.log("步骤3：等待验证码输入（最多15秒）")
            captcha_el = self._try_find(By.XPATH, "//input[@id='form_item_verifyCode']", timeout=3)
            if not captcha_el:
                captcha_el = self._try_find(By.XPATH, "//input[contains(@placeholder,'验证码')]", timeout=3)
            if captcha_el:
                for i in range(15):
                    val = (captcha_el.get_attribute("value") or "").strip()
                    if len(val) >= 4:
                        self.log(f"  ✓ 检测到验证码已输入（{i + 1}秒）")
                        break
                    time.sleep(1)
                else:
                    self.log("  ⚠ 15秒内未检测到验证码，尝试继续登录")
            else:
                self.log("  ⚠ 未找到验证码输入框，跳过等待")

            self.log("步骤4：勾选记住我")
            for by, val in [
                (By.XPATH, "//input[@type='checkbox']"),
                (By.XPATH, "//*[contains(text(),'记住我')]"),
                (By.XPATH, "//label[contains(.,'记住')]"),
            ]:
                try:
                    el = self.driver.find_element(by, val)
                    if not el.is_displayed():
                        continue
                    if el.tag_name == "input" and not el.is_selected():
                        el.click()
                    elif el.tag_name != "input":
                        el.click()
                    self.log("  ✓ 已勾选记住我")
                    break
                except Exception:
                    continue

            self.log("步骤5：点击登录")
            login_clicked = False
            for by, val in [
                (By.XPATH, "//button[.//span[normalize-space()='登 录']]"),
                (By.XPATH, "//button[normalize-space()='登录' or normalize-space()='登 录']"),
                (By.XPATH, "//span[normalize-space()='登 录' or normalize-space()='登录']"),
                (By.XPATH, "//button[@type='submit']"),
            ]:
                if self._try_click(by, val, label="登录按钮"):
                    login_clicked = True
                    break
            if not login_clicked:
                self.log("  ✗ 未能点击登录按钮")
                self.save_html("login_btn_failed")
                return False

            self.log("等待登录跳转")
            try:
                WebDriverWait(self.driver, 15).until(lambda d: "login" not in d.current_url)
                self.log(f"✓ 登录成功，当前URL：{self.driver.current_url}")
                return True
            except TimeoutException:
                self.save_html("login_failed")
                self.log("✗ 登录失败（可能验证码错误）")
                return False

        except Exception as exc:
            self.log(f"✗ 登录异常：{exc}")
            self.save_html("login_exception")
            return False

    def test_tc_ds_002_system_filter(self) -> bool:
        self.log("\n" + "=" * 60)
        self.log("TC_DS_002 全局筛选-系统切换展示正确")
        self.log("=" * 60)

        try:
            time.sleep(2)
            self.save_html("before_filter")

            default_el = None
            for by, val in [
                (By.XPATH, "//span[normalize-space()='C-Smart内部盘']"),
                (By.XPATH, "//*[normalize-space()='C-Smart内部盘']"),
                (By.XPATH, "//*[contains(normalize-space(),'内部盘')]"),
            ]:
                default_el = self._try_find(by, val, timeout=5)
                if default_el:
                    self.log(f"  ✓ 默认选中：{default_el.text}")
                    break
            if not default_el:
                self.log("  ✗ 未找到默认筛选框")
                return False

            opened = False
            for by, val in [
                (By.XPATH, "//span[normalize-space()='C-Smart内部盘']"),
                (By.XPATH, "//span[normalize-space()='C-Smart内部盘']/.."),
            ]:
                if self._try_click(by, val, label="系统下拉框"):
                    opened = True
                    break
            if not opened:
                self.log("  ✗ 无法打开系统下拉框")
                return False

            time.sleep(1)
            if not self._try_click(By.XPATH, "//*[normalize-space()='市场化盘']", label="市场化盘"):
                self.log("  ✗ 未找到市场化盘")
                self.save_html("no_market_option")
                return False

            time.sleep(1)
            query_clicked = False
            for by, val in [
                (By.XPATH, "//button[contains(normalize-space(),'查') and contains(normalize-space(),'询')]"),
                (By.XPATH, "//span[contains(normalize-space(),'查') and contains(normalize-space(),'询')]/ancestor::button[1]"),
            ]:
                if self._try_click(by, val, label="查询按钮"):
                    query_clicked = True
                    break
            if not query_clicked:
                self.log("  ✗ 未找到查询按钮")
                return False

            time.sleep(2)
            if "暂无数据" in self.driver.page_source:
                self.log("✓ 页面显示暂无数据，用例通过")
                return True

            self.save_html("filter_result")
            self.log("⚠ 页面未出现暂无数据，请人工确认")
            return False

        except Exception as exc:
            self.log(f"✗ TC_DS_002 异常：{exc}")
            self.save_html("filter_exception")
            return False

    def test_tc_ds_003_export_pdf(self) -> bool:
        self.log("\n" + "=" * 60)
        self.log("TC_DS_003 导出PDF文件")
        self.log("=" * 60)

        try:
            if not self._try_click(By.XPATH, "//*[normalize-space()='导出' or normalize-space()='导 出']", label="导出按钮"):
                self.log("  ✗ 未找到导出按钮")
                return False

            time.sleep(1)
            if not self._try_click(By.XPATH, "//*[contains(normalize-space(),'PDF')]", label="PDF选项"):
                self.log("  ✗ 未找到PDF选项")
                self.save_html("no_pdf_option")
                return False

            confirmed = False
            for by, val in [
                (By.XPATH, "//button[contains(normalize-space(),'确') and contains(normalize-space(),'定')]"),
                (By.XPATH, "//button[contains(normalize-space(),'确') and contains(normalize-space(),'认')]"),
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
            self.log(f"✗ TC_DS_003 异常：{exc}")
            self.save_html("export_exception")
            return False

    def test_tc_ds_004_device_distribution(self) -> bool:
        self.log("\n" + "=" * 60)
        self.log("TC_DS_004 设备状态分布")
        self.log("=" * 60)

        try:
            time.sleep(2)
            self.save_html("before_device_dist")

            clicked = False
            for by, val in [
                (By.XPATH, "//*[normalize-space()='4G手表']"),
                (By.XPATH, "//*[contains(normalize-space(),'4G手表')]"),
            ]:
                if self._try_click(by, val, label="4G手表柱状图", timeout=5):
                    clicked = True
                    break

            if not clicked:
                self.log("  ⚠ 未找到4G手表元素，尝试ECharts JS触发")
                clicked = self._click_echarts_bar("4G手表")
                time.sleep(2)

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

            time.sleep(2)
            self.save_html("after_detail_click")
            if "设备详情" in self.driver.page_source:
                self.log("✓ 设备详情窗口已打开")
                return True

            self.log("⚠ 未检测到设备详情字样，请人工确认")
            return False

        except Exception as exc:
            self.log(f"✗ TC_DS_004 异常：{exc}")
            self.save_html("device_dist_exception")
            return False

    def run(self) -> dict[str, bool]:
        if not EXCEL_PATH.exists():
            self.log(f"✗ 未找到测试用例文件：{EXCEL_PATH}")
            return {}

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

            return self.results
        finally:
            self.teardown()
            self.print_summary()

    def print_summary(self) -> None:
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
        for case_id, title in name_map.items():
            if case_id in self.results:
                flag = "✓ 通过" if self.results[case_id] else "✗ 失败"
                self.log(f"  {case_id} [{title}]: {flag}")
                if self.results[case_id]:
                    passed += 1
            else:
                self.log(f"  {case_id} [{title}]: - 未执行")

        total = len(self.results)
        self.log(f"\n  通过率：{passed}/{total}")
        self.log(f"  日志文件：{self.log_file}")


def main() -> int:
    runner = IOTDeviceStatsAutomation(headless=False)
    results = runner.run()
    passed = sum(1 for item in results.values() if item)
    total = len(results)
    return 0 if total > 0 and passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
