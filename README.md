# 韩山师范学院校园网自动登录工具 (HSTC Campus Network Auto Login)

针对韩山师范学院（HSTC）校园网（城市热点 Dr.COM 网关 + 智慧韩园统一身份认证 CAS）开发的自动化免密登录与掉线保活工具。

## ✨ 特性

- **即开即用**：自动从 Dr.COM 网关提取当前设备 IP 并重定向至 CAS 统一身份认证。
- **完全静默运行**：无控制台黑框、无浏览器界面，系统开机或连上 Wi-Fi 后在底层数秒内完成认证。
- **掉线自动重连**：后台守护进程周期性检测网络（默认 30 秒一次），一旦断开自动发起重新认证。
- **防误判检测机制**：采用微软官方专用连通性接口与 HTTPS 严格握手探测，避免网关拦截页面造成的“假联网”误判。
- **一键自启管理**：提供开机自启动与取消开机自启的快速管理脚本。

## 📦 文件说明

| 文件 | 说明 |
| :--- | :--- |
| `config.example.ini` | 配置文件模板（复制为 `config.ini` 后填入学号和密码） |
| `hstc_campus_login.py` | 核心登录逻辑与网络守护脚本 |
| `silent_login.vbs` | 后台无窗口静默启动器 |
| `一键登录.bat` | 带有控制台日志输出的手动启动脚本（适合调试） |
| `添加开机自启.bat` | 一键将本工具添加至 Windows 开机自启文件夹 |
| `取消开机自启.bat` | 一键从 Windows 开机自启中移除本工具 |

## 🚀 快速上手

### 1. 安装环境依赖
本项目基于 Python 与 Playwright 驱动，在终端中执行：

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. 填写配置
将项目中的 `config.example.ini` 重命名或复制为 `config.ini`，使用文本编辑器填入你的账号信息：

```ini
[account]
username = 你的学号
password = 你的密码

[settings]
headless = True
check_interval = 30
```

### 3. 运行与测试
- **调试测试**：双击 `一键登录.bat`，控制台会输出登录状态并开始守护。
- **后台静默运行**：双击 `silent_login.vbs`，直接在后台静默运行，结果会写入 `login.log`。
- **设置开机自启**：双击 `添加开机自启.bat` 即可。

## ⚠️ 免责声明与安全提示
- 请勿将包含真实学号和密码的 `config.ini` 提交至公开代码仓库（项目默认的 `.gitignore` 已屏蔽该文件）。
- 本项目仅供学习交流与校园网络便利使用，请遵守学校网络管理规范。
