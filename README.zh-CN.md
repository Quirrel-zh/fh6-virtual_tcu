# Virtual TCU v13.0 — Forza Horizon 6

**简体中文 | [English](README.md)**

> 本项目由 **Insightful** 维护，面向 [**Forza Mods**](https://discord.gg/forzamods) Discord 社区用户。

面向《极限竞速：地平线 6》的外部自适应变速箱控制器。通过 UDP 读取游戏遥测，根据驾驶风格、油门、转速、车速与刹车等信号自动换挡，并向游戏注入键盘按键（**E** 升档、**Q** 降档）。

**v13** 提供 Windows 托盘桌面应用（Electron），含浮动 HUD 与自动更新；实时遥测仪表盘在浏览器 **http://127.0.0.1:8765** 打开（支持 English / 简体中文）。仍提供纯 Python 便携版，适合不需要 Electron 的用户。

---

## 快速选择

| 需求 | 说明 |
|------|------|
| 只想玩 — 托盘应用、HUD、自动更新 | [下载 Electron 安装包](#下载与使用electron-安装包) |
| 只想玩 — 纯 Python 后端、无 Electron | [下载 backend-only 压缩包](#下载与使用backend-only-压缩包) |
| 从仓库源码运行 / 开发 | [从源码运行](#从源码运行) |
| 改 Vue 前端 | [web-ui/README.md](web-ui/README.md) |

**平台：** 仅 **Windows 10 / 11**。请**以管理员身份运行**（全局按键注入需要）。

---

## 下载与使用（Electron 安装包）

推荐给大多数用户。单个安装包整合 Python 后端，提供 **设置窗口** 用于配置、**浏览器只读仪表盘** 查看实时遥测、可选 **HUD 悬浮窗** 与 **自动更新**。

### 1. 下载

打开 **[GitHub Releases](https://github.com/Quirrel-zh/fh6-virtual_tcu/releases)**，下载最新的 `VirtualTCU-*-win64.exe`。

### 2. 安装与启动

运行安装程序（启动时会请求管理员权限）。首次启动后会创建**系统托盘图标**，并注册开始菜单 / 桌面快捷方式。

启动后应用会：

1. 在后台启动内置 Python 后端；
2. 打开 **设置窗口**（驾驶模式、调参、网络、统计、更新器等）；
3. 关闭设置窗口后仍在托盘中运行。

**托盘菜单：**

| 项目 | 作用 |
|------|------|
| **Settings（设置）** | 打开 / 聚焦设置窗口 |
| **Open Dashboard in Browser（在浏览器中打开仪表盘）** | 打开实时遥测页（`http://127.0.0.1:8765`） |
| **Toggle HUD（切换 HUD）** | 显示 / 隐藏悬浮窗（档位 / 模式 / RPM / 车速） |
| **Restart Backend（重启后端）** | 不退出应用的情况下重启 Python 后端 |
| **Quit（退出）** | 完全退出 |

左键单击托盘图标也会打开**设置窗口**。

**自动更新**在启动后稍晚检查 GitHub Releases，并在后台下载新版本。Electron 与 Python 后端作为整体一起更新（可在设置窗口 **关于** 标签页查看状态）。

### 3. 进游戏

按下方 [游戏内设置](#forza-horizon-6-游戏内设置首次配置) 配置 FH6，然后：

1. 打开 **设置** → 选择驾驶模式并按需调整；
2. 托盘 → **在浏览器中打开仪表盘**（或设置 **概览** 标签页中的按钮）查看实时数据；
3. 可选：托盘 → **切换 HUD** 显示游戏内悬浮窗；
4. 开始比赛 — 收到遥测后仪表盘与 HUD 变为**在线**。

### 4. 退出

托盘图标 → **Quit（退出）**。

### Electron 版数据存放位置

内置后端将配置、档案、日志保存在安装目录 `resources/backend/` 下的 `VirtualTCU.exe` 同目录（便携模式）。若该目录不可写（例如 `C:\Program Files\`），则回退到 **`%APPDATA%\VirtualTCU\`**。

| 内容 | 默认位置（Electron） |
|------|----------------------|
| 设置 | `resources\backend\tcu_config.json` 或 `%APPDATA%\VirtualTCU\tcu_config.json` |
| 每车档案 | 同上目录 / `tcu_profiles.json` |
| 遥测录制 | 同上目录 / `logs\` |
| 崩溃日志 | 同上目录 / `crash.log` |

---

## 下载与使用（backend-only 压缩包）

适合需要原版便携布局、不需要 Electron / HUD / 自动更新的用户。仪表盘在默认浏览器中打开，且包含完整设置（非只读）。

### 1. 下载

从 **[GitHub Releases](https://github.com/Quirrel-zh/fh6-virtual_tcu/releases)** 下载 `VirtualTCU-Backend-*-win64.zip`。

### 2. 解压

**完整解压**到任意目录（如 `C:\Games\VirtualTCU\`），不要在压缩包预览里直接双击 exe。

```
VirtualTCU-Backend-13.0.x-win64/
├── Launch VirtualTCU.bat    ← 可选启动器（推荐）
└── VirtualTCU/
    ├── VirtualTCU.exe
    └── _internal/           ← 必需，勿单独移动 exe
```

### 3. 启动

右键 **`Launch VirtualTCU.bat`** 或 **`VirtualTCU\VirtualTCU.exe`** → **以管理员身份运行**。

会出现黑色命令行窗口；浏览器可能自动打开 **http://127.0.0.1:8765**，否则手动打开。

### 4. 退出

切到**命令行窗口**，按 **`Ctrl + C`**，再关窗口。  
（**不要**按 **Q** — 那是游戏内降档键。）

### backend-only 版数据存放位置

Release 的配置、档案、日志默认保存在 **`VirtualTCU.exe` 同目录**（便携模式）：

```
VirtualTCU/
├── VirtualTCU.exe
├── _internal/
├── tcu_config.json
├── tcu_profiles.json
├── logs/
│   └── tcu_replay_*.bin.gz
└── .tcu_last_run
```

若安装目录不可写（例如装在 `C:\Program Files\`），会自动回退到 **`%APPDATA%\VirtualTCU\`**。启动时黑窗口会打印实际使用的路径。

| 内容 | 默认位置（Release） |
|------|---------------------|
| 设置 | `VirtualTCU\tcu_config.json` |
| 每车档案 | `VirtualTCU\tcu_profiles.json` |
| 遥测录制 | `VirtualTCU\logs\` |
| 崩溃日志 | 同上目录下的 `crash.log` |

### 遥测录制

**Electron 用户：** 在 **设置窗口** 中开始 / 停止录制（概览或侧边栏控件）。

**backend-only 用户：** 在 Web 界面侧边栏点 **开始记录（事件）** 或 **开始记录（全部）**，在 FH6 比赛中驾驶，完成后点 **停止**。

| 模式 | 说明 |
|------|------|
| **事件** | 主要记录换挡瞬间及前后缓冲（约 0.5 MB） |
| **全部** | 录制期间所有遥测包（最大 10 MB 自动停止） |

文件名为 `tcu_replay_YYYYMMDD_HHMMSS.bin.gz`（gzip 二进制回放，不是普通 `.log`）。

---

## 从源码运行

适用于 git clone 后的开发或自测。

### 环境要求

| 工具 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | [下载](https://www.python.org/downloads/)，勾选 **Add Python to PATH** |
| Node.js | 18+ | 构建 Vue 仪表盘与 Electron 壳时需要 |

### 首次配置

**管理员**命令提示符或 PowerShell：

```bash
cd path\to\virtualTCU
pip install -r requirements.txt

cd web-ui
npm install
npm run build
cd ..
```

`npm run build` 会生成 `virtual_tcu/web/dist/`。未构建时访问 `:8765` 只会看到 HTTP **503** 提示页。

### 方式 A — Electron 壳（推荐）

```bash
cd electron
npm install
npm run dev
```

或在仓库根目录运行：`packaging\dev-electron.bat`

会自动启动 `python -m virtual_tcu --backend-only`。若存在 `dist/VirtualTCU/` 下的 PyInstaller 产物会优先使用（开发时可设 `TCU_USE_FROZEN_BACKEND=1` 强制使用）。

### 方式 B — 仅 Python 后端（浏览器 UI）

```bash
cd path\to\virtualTCU
python -m virtual_tcu
```

（`python virtual_tcu.py` 亦可。）

浏览器打开 **http://127.0.0.1:8765**，进 FH6 比赛。终端里 **`Ctrl + C`** 退出。

### 源码运行的数据位置

配置、档案、日志写在**项目目录**（当前工作目录）：

```
virtualTCU/
├── tcu_config.json
├── tcu_profiles.json
└── logs/
    └── tcu_replay_*.bin.gz
```

### 前端开发（可选）

终端 1 — 后端：

```bash
python -m virtual_tcu
```

终端 2 — Vite 热更新：

```bash
cd web-ui
npm run dev
```

浏览器打开 **http://127.0.0.1:5173**（WebSocket 代理到 8765）。详见 [web-ui/README.md](web-ui/README.md)。

### 本地打包 Release（维护者）

```bash
# 1. Vue 仪表盘
cd web-ui && npm ci && npm run build && cd ..

# 2. Python 后端（PyInstaller onedir → dist/VirtualTCU/）
pip install pyinstaller
pyinstaller virtual_tcu.spec --noconfirm

# 3. Electron 安装包（NSIS → electron/release/VirtualTCU-*-win64.exe）
cd electron && npm ci && npm run package
```

推送 `v*` 标签可触发 CI，产出 Electron 安装包（`VirtualTCU-*-win64.exe` + `latest.yml`）与 backend-only 压缩包（`VirtualTCU-Backend-*-win64.zip`）。

---

## 驾驶模式

| 模式 | 说明 |
|------|------|
| **COMFORT** | 省油取向，较早升档，巡航时保持稳定转速 |
| **DYNAMIC** | 奥迪式逻辑：较高转速保持、降档严格匹配转速 |
| **RACE** | 赛道取向：接近红线升档、积极发动机制动 |
| **DRIFT** | 维持动力区间转速，减少漂移中意外降档 |
| **OFFROAD** | 越野取向：适应低抓地与起伏路况的换挡策略 |
| **MANUAL** | 关闭 TCU 自动换挡，由玩家手动控制 |

**F9** 循环切换模式，**F8** 切换日志录制（全局热键，Forza 在前台时同样有效）。可在设置窗口 / Web UI 中修改。

---

## Forza Horizon 6 游戏内设置（首次配置）

### 1. 变速箱

**设置 → 难度 → 变速箱 → 手动（无离合器）**

### 2. 键盘换挡绑定

**设置 → 控制 → 键盘**：

| 动作 | 按键 |
|------|------|
| 升档 | **E** |
| 降档 | **Q** |

> 手柄/方向盘的换挡键可与上述键盘绑定**同时生效**。TCU 仅注入 **E** / **Q**。

### 3. 遥测 Data Out

**设置 → HUD 与游戏 → Data Out**：

| 选项 | 值 |
|------|-----|
| Data Out | **开** |
| IP 地址 | `127.0.0.1` |
| 端口 | `5555` |
| 数据包格式 | **Car Dash**（324 字节） |

> 若在 Virtual TCU 网络设置中修改 UDP 端口，请同步修改 FH6 中的端口。

---

## 桌面应用（Electron）

| 窗口 | 用途 |
|------|------|
| **设置** | 完整配置 — 驾驶模式、滑块、热键、网络、统计、换挡历史、配置导入导出、自动更新 |
| **浏览器仪表盘** | 只读实时视图 — 档位、RPM 曲线、G 值球、会话统计（通过托盘或设置窗口打开） |
| **HUD 悬浮窗** | 极简置顶 overlay — 档位、模式、RPM 条、车速、换档提示；支持点击穿透 |

关闭设置窗口只是隐藏，应用在托盘中继续运行，直到选择 **退出**。

---

## Web 仪表盘

连接成功后，浏览器仪表盘显示：

- **档位 / 车速 / 转速** — 大号档位读数、20 段 RPM LED 条
- **实时曲线** — RPM、油门、刹车、车速随时间变化，换档时刻标记
- **G 值球** — 横向 / 纵向 G 值与抓地力使用率
- **踏板与输入** — 油门、刹车、离合百分比
- **TCU 状态** — 巡航、Kickdown、发动机制动、腾空 / 横摆锁定等
- **涡轮 / 发动机** — 增压（bar）、功率（kW）、扭矩（Nm）
- **统计与换挡历史** — 会话计数、峰值、最近换档记录（右侧面板）
- **学习侧栏** — 运动指数、功率曲线 / 齿比校准状态

**Electron 版**中浏览器页面为**只读**（页脚提示请在桌面设置应用中修改配置与录制）。**backend-only 版**在 Web UI 中提供完整设置。

页头可切换 English / 简体中文。

---

## 网络设置

可在 Electron **设置窗口**与 backend-only Web UI 中配置：

| 设置项 | 默认值 | 说明 |
|--------|--------|------|
| Web 绑定地址 | `127.0.0.1` | 设为 `0.0.0.0` 可允许局域网内其他设备访问 |
| Web 端口 | `8765` | 仪表盘 HTTP / WebSocket 端口 |
| UDP 端口 | `5555` | 须与 FH6 Data Out 端口一致 |

点击 **Apply（应用）** 保存。后端会热重载绑定；若 Web 端口变更，请按设置窗口显示的新 URL 重新打开仪表盘。

---

## 项目结构（简要）

```
virtualTCU/
├── virtual_tcu.py          # 入口
├── virtual_tcu/            # Python 后端包
├── web-ui/                 # Vue 3 + Tailwind v4 仪表盘（:8765 提供）
├── electron/               # Electron 壳（托盘、设置、HUD、自动更新）
│   ├── src/main/index.ts   # 启动后端、生命周期、托盘、IPC、autoUpdater
│   ├── src/settings-renderer/  # 设置窗口（Naive UI）
│   ├── src/hud-renderer/   # 无边框透明 HUD 悬浮窗
│   ├── src/preload/        # main + hud 预加载脚本
│   └── electron-builder.yml
├── packaging/              # Launch VirtualTCU.bat、dev-electron.bat
├── virtual_tcu.spec        # PyInstaller 配置
└── .github/workflows/      # Release CI
```

---

## 故障排除

### Electron 已启动但打不开仪表盘

- 托盘 → **在浏览器中打开仪表盘**，或设置 → **概览** → 打开仪表盘。
- 确认后端已就绪（设置中显示 **在线** / **待机**，而非 **未连接**）。
- 若后端崩溃，托盘 → **重启后端**。

### Release exe 闪退（backend-only 压缩包）

- 完整解压，保留 `_internal/`。
- 关闭其它 TCU 实例（含 `python -m virtual_tcu`）；**5555** / **8765** 端口同一时刻只能被一个实例占用。
- 在 cmd 中运行 exe 查看报错；查启动时打印的数据目录下的 **`crash.log`**。

### 端口已被占用

- 同时只应运行一个后端。退出其他 Virtual TCU 实例，或在网络设置中更换端口。

### 点了录制但找不到文件

- 日志在后端数据目录的 `logs\`（exe 同目录或 `%APPDATA%\VirtualTCU\logs\`）。
- 必须先点 **停止**。
- **全部**模式 + 比赛中 + Data Out 开启；**事件**模式主要在换挡时才有内容。
- 文件名是 `tcu_replay_*.bin.gz`。

### 仪表盘离线

- Data Out 开、端口 **5555**、**Car Dash** 格式；必须在**比赛中**。

### 不换挡

- Forza 键盘 **E/Q**；**管理员**运行。

### 热键无效

- 关闭可能占用 F9/F8 的 overlay 软件。

### 档位/车速异常

- 仅支持 FH6 **324 字节 Car Dash** 包。

### 自动更新无反应

- 自动更新仅在**打包后的** Electron 安装版中生效，`npm run dev` 不会检查更新。
- 在设置窗口 **关于** 标签页查看更新状态。

---

## 说明

- 任意 FH6 车辆可用，换挡点从遥测自动校准。
- **倒档保护**、**低速保护**（约 12 km/h 以下不自动换挡）。
- 仅发送 **E/Q** 键盘事件。

---

## 测试环境

- Windows 11 · Steam 版 FH6 · Xbox Elite Series 2

遥测基于 FH6 **324 字节 Car Dash** 数据包（实车诊断验证）。
