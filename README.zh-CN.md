# Virtual TCU v12.0 — Forza Horizon 6

**简体中文 | [English](README.md)**

> 本项目由 **Insightful** 维护，面向 [**Forza Mods**](https://discord.gg/forzamods) Discord 社区用户。

面向《极限竞速：地平线 6》的外部自适应变速箱控制器。通过 UDP 读取游戏遥测，根据驾驶风格、油门、转速、车速与刹车等信号自动换挡，并向游戏注入键盘按键（**E** 升档、**Q** 降档）。

启动后在浏览器打开 **http://127.0.0.1:8765** 查看实时仪表盘与设置（支持 English / 简体中文界面）。

---

## 快速选择

| 需求 | 说明 |
|------|------|
| 只想玩，不装 Python / Node | [下载与使用（Release）](#下载与使用release) |
| 从仓库源码运行 / 开发 | [从源码运行](#从源码运行) |
| 改 Vue 前端 | [web-ui/README.md](web-ui/README.md) |

**平台：** 仅 **Windows 10 / 11**。请**以管理员身份运行**（全局按键注入需要）。

---

## 下载与使用（Release）

### 1. 下载

打开 **[GitHub Releases](https://github.com/Quirrel-zh/fh6-virtual_tcu/releases)**，下载最新的 `VirtualTCU-*-win64.zip`。

### 2. 解压

**完整解压**到任意目录（如 `C:\Games\VirtualTCU\`），不要在压缩包预览里直接双击 exe。

```
VirtualTCU-12.0.x-win64/
├── Launch VirtualTCU.bat    ← 可选启动器（推荐）
└── VirtualTCU/
    ├── VirtualTCU.exe
    └── _internal/           ← 必需，勿单独移动 exe
```

### 3. 启动

右键 **`Launch VirtualTCU.bat`** 或 **`VirtualTCU\VirtualTCU.exe`** → **以管理员身份运行**。

会出现黑色命令行窗口；浏览器可能自动打开 **http://127.0.0.1:8765**，否则手动打开。

### 4. 进游戏

按下方 [游戏内设置](#forza-horizon-6-游戏内设置首次配置) 配置 FH6，开始比赛后仪表盘会从离线变为在线。

### 5. 退出

切到**命令行窗口**，按 **`Ctrl + C`**，再关窗口。  
（**不要**按 **Q** — 那是游戏内降档键。）

### Release 版数据存放位置

Release 的所有用户数据在 **`%APPDATA%\VirtualTCU\`**，**不在** exe 旁边。

| 内容 | 路径 |
|------|------|
| 设置 | `%APPDATA%\VirtualTCU\tcu_config.json` |
| 每车档案 | `%APPDATA%\VirtualTCU\tcu_profiles.json` |
| 遥测录制日志 | `%APPDATA%\VirtualTCU\logs\` |
| 启动崩溃日志 | `%APPDATA%\VirtualTCU\crash.log` |

快速打开日志目录：`Win + R` → 输入 `%APPDATA%\VirtualTCU\logs`

### 遥测录制（侧边栏）

1. 在 Web 界面侧边栏点 **开始记录（事件）** 或 **开始记录（全部）**。
2. 在 FH6 比赛中驾驶（需开启 Data Out）。
3. 完成后点 **停止** — 文件在停止时才会完整写入。

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
| Node.js | 18+ | 仅构建 / 修改 Web UI 时需要 |

### 首次配置

**管理员**命令提示符或 PowerShell：

```bash
cd path\to\virtualTCU
pip install -r requirements.txt
```

```bash
cd web-ui
npm install
npm run build
cd ..
```

`npm run build` 会生成 `virtual_tcu/web/dist/`。未构建时访问 `:8765` 只会看到 HTTP **503** 提示页。

### 启动后端

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
cd web-ui && npm run build && cd ..
pip install pyinstaller
pyinstaller virtual_tcu.spec --noconfirm
```

产物在 `dist/VirtualTCU/`，与 GitHub Release 结构相同。推送 `v*` 标签可触发 CI 自动发布。

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

**F9** 循环切换模式，**F8** 切换日志录制（全局热键，Forza 在前台时同样有效）。可在 Web 设置中修改。

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

---

## Web 仪表盘

- **档位 / 车速 / 转速**、**油门 / 刹车**、**TCU 状态**
- **涡轮 / 发动机**、**统计与换挡历史**
- **设置**（实时调参、每车配置导入导出）
- **日志录制**（侧边栏开始/停止）

页头可切换 English / 简体中文。

---

## 项目结构（简要）

```
virtualTCU/
├── virtual_tcu.py          # 入口
├── virtual_tcu/            # Python 核心包
├── web-ui/                 # Vue 3 + Tailwind v4 前端
├── packaging/              # Launch VirtualTCU.bat（打入 Release zip）
├── virtual_tcu.spec        # PyInstaller 配置
└── .github/workflows/      # Release CI
```

---

## 故障排除

### Release exe 闪退

- 完整解压，保留 `_internal/`。
- 关闭其它 TCU 实例（含 `python -m virtual_tcu`）。
- cmd 中运行 exe 查看报错；查 **`%APPDATA%\VirtualTCU\crash.log`**。

### 点了录制但找不到文件

- Release 日志在 **`%APPDATA%\VirtualTCU\logs\`**，不在 exe 目录。
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

---

## 说明

- 任意 FH6 车辆可用，换挡点从遥测自动校准。
- **倒档保护**、**低速保护**（约 12 km/h 以下不自动换挡）。
- 仅发送 **E/Q** 键盘事件。

---

## 测试环境

- Windows 11 · Steam 版 FH6 · Xbox Elite Series 2

遥测基于 FH6 **324 字节 Car Dash** 数据包（实车诊断验证）。
