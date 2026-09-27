# -*- coding: utf-8 -*-
"""
韩山师范学院 (HSTC) 校园网自动登录脚本 (Playwright 静默后台版)
适用于：城市热点 Dr.COM + 智慧韩园统一身份认证 (CAS)
"""

import os
import sys
import time
import ssl
import configparser
import urllib.request
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.ini")
LOG_FILE = os.path.join(BASE_DIR, "login.log")

def log(msg: str):
    """同时输出到控制台与本地日志文件"""
    line = f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line, flush=True)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def load_config():
    """读取 config.ini 配置文件"""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        log(f"[错误] 未找到配置文件: {CONFIG_FILE}")
        sys.exit(1)
    config.read(CONFIG_FILE, encoding="utf-8")
    username = config.get("account", "username", fallback="202416057214").strip()
    password = config.get("account", "password", fallback="").strip()
    headless = config.getboolean("settings", "headless", fallback=True)
    check_interval = config.getint("settings", "check_interval", fallback=5)
    return username, password, headless, check_interval

class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """禁止自动重定向，以便准确获取网关返回的真实 302 拦截码"""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

_opener = urllib.request.build_opener(_NoRedirect)

def _probe_internet() -> bool:
    """探测国内高速 204 接口与微软接口，防拦截且延迟极低"""
    # 1. 华为与小米国内高速 204 接口（响应约数十毫秒，被劫持时会返回 302 或 200，只有真正联网才是 204）
    fast_endpoints = [
        "http://connectivitycheck.platform.hicloud.com/generate_204",
        "http://connect.rom.miui.com/generate_204",
    ]
    for url in fast_endpoints:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with _opener.open(req, timeout=2.5) as resp:
                if resp.getcode() == 204:
                    return True
        except Exception:
            pass

    # 2. 微软官方连通性校验备用（被拦截返回 HTML，真实联网返回纯文本）
    try:
        req = urllib.request.Request("http://www.msftconnecttest.com/connecttest.txt", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            if resp.read().decode("utf-8", errors="ignore").strip() == "Microsoft Connect Test":
                return True
    except Exception:
        pass

    # 3. 百度 HTTPS 兜底
    try:
        ctx = ssl.create_default_context()
        req = urllib.request.Request("https://www.baidu.com", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3, context=ctx) as resp:
            if resp.getcode() == 200:
                return True
    except Exception:
        pass

    return False

def is_online() -> bool:
    """带防抖重试的连通性判定，防止单次 Wi-Fi 波动丢包引起误报重连"""
    if _probe_internet():
        return True
    time.sleep(1)
    return _probe_internet()

def get_auth_url() -> str:
    """从 Dr.COM 网关接口获取携带当次设备 IP 的精准 CAS 认证地址"""
    try:
        url = "http://rz.hstc.edu.cn:801/eportal/portal/cas/create?callback=dr1003&login_method=1"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as resp:
            raw = resp.read().decode("utf-8", errors="ignore")
            idx = raw.find("authorize_uri")
            if idx != -1:
                part = raw[idx:]
                start = part.find("http")
                end = part.find('"', start)
                if end != -1:
                    auth_url = part[start:end].replace("\\/", "/")
                    log("成功获取到网关专用认证链接")
                    return auth_url
    except Exception as e:
        log(f"探测网关接口提示: {e}")

    return "https://hscas.hstc.edu.cn/cas/login"

def do_login(username, password, headless):
    """使用 Playwright 执行后台静默登录"""
    if not password:
        log("[提示] 配置文件 config.ini 中的 password 尚未填写，请先填入密码！")
        return False

    auth_url = get_auth_url()
    log(f"正在启动后台登录引擎 (学号: {username}, headless={headless})...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            log("正在打开统一身份认证页面...")
            page.goto(auth_url, wait_until="commit", timeout=15000)

            # 等待菜单渲染
            page.wait_for_selector(".el-menu-item, #fm1, .sw-login-menu", timeout=15000)
            time.sleep(0.5)

            # 1. 切换到“账号登录”选项卡
            menu_items = page.locator(".el-menu-item").all()
            if menu_items:
                clicked = False
                for item in menu_items:
                    text = item.inner_text().strip()
                    if "账号" in text or "学号" in text:
                        item.click()
                        clicked = True
                        break
                if not clicked:
                    menu_items[0].click()

            # 2. 等待表单可见
            page.wait_for_selector("#fm1", state="visible", timeout=6000)

            # 3. 自动填入学号与密码
            u_input = page.locator("#fm1 #username")
            p_input = page.locator("#fm1 #password")
            
            u_input.fill(username)
            p_input.fill(password)
            time.sleep(0.3)

            # 4. 检查是否出现图形验证码
            captcha_input = page.locator("#fm1 #captcha")
            if captcha_input.is_visible():
                log("[注意] 检测到页面触发了图片验证码，需人工处理。")
                return False

            # 5. 点击登录按钮
            login_btn = page.locator(
                '#fm1 input[value="LOGIN"], #fm1 input[name="button"], #fm1 input[type="button"], #fm1 button'
            ).first
            login_btn.click()
            log("已点击登录，等待网关放行...")

            # 6. 等待并检测网络状态
            for i in range(8):
                time.sleep(1)
                err_el = page.locator(".el-message--error, .error, #msg, .sw-login-error")
                if err_el.count() > 0 and err_el.first.is_visible():
                    err_msg = err_el.first.inner_text().strip()
                    log(f"登录失败，系统提示: {err_msg}")
                    return False

                if is_online():
                    log("登录成功！网络已正常连通。")
                    return True

            if is_online():
                log("登录成功！")
                return True
            else:
                log(f"认证请求已完成，但网络尚未放行。当前地址: {page.url}")
                return False

        except Exception as e:
            log(f"登录过程异常: {e}")
            return False
        finally:
            try:
                time.sleep(0.5)
                browser.close()
            except Exception:
                pass

def main():
    username, password, headless, check_interval = load_config()

    log("==================================================")
    log("      韩山师范学院校园网自动登录服务已就绪       ")
    log(f" 当前学号: {username}")
    log(f" 运行模式: {'后台完全静默' if headless else '显示浏览器窗口'}")
    log("==================================================")

    if not is_online():
        log("检测到当前未联网，开始执行后台登录...")
        do_login(username, password, headless)
    else:
        log("当前网络已连通，保持在线守护中...")

    try:
        while True:
            time.sleep(check_interval)
            if not is_online():
                log("检测到网络掉线，正在重新登录...")
                do_login(username, password, headless)
    except KeyboardInterrupt:
        log("守护进程退出。")

if __name__ == "__main__":
    main()

