# Virtual TCU v12.0 — Forza Horizon 6

**简体中文 | [English](README.md)**

> 本项目由 **Insightful** 维护，面向 [**Forza Mods**](https://discord.gg/forzamods) Discord 社区用户。

面向《极限竞速：地平线 6》的外部自适应变速箱控制器。通过 UDP 读取游戏遥测，根据驾驶风格、油门、转速、车速与刹车等信号自动换挡，并向游戏注入键盘按键（**E** 升档、**Q** 降档）。

启动后在浏览器打开 **http://127.0.0.1:8765** 查看实时仪表盘与设置（支持 English / 简体中文界面）。

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

**F9**（全局热键，Forza 在前台时同样有效）循环切换模式。热键可在 Web 设置中修改。

---

## 系统要求

| 项目 | 要求 |
|------|------|
| 操作系统 | **Windows 10 / 11**（仅支持 Windows） |

### 方式 A — 下载 Release（无需 Python / Node）

1. 打开 **[GitHub Releases](https://github.com/Quirrel-zh/fh6-virtual_tcu/releases)**，下载最新的 `VirtualTCU-*-win64.zip`。
2. 解压到任意目录（例如 `C:\Games\VirtualTCU\`）。
3. 以**管理员**身份运行 **`VirtualTCU.exe`**（全局按键注入需要管理员权限）。
4. 在浏览器打开 **http://127.0.0.1:8765**。

配置、档案与日志保存在 **`%APPDATA%\VirtualTCU\`**（`tcu_config.json`、`tcu_profiles.json`、`logs\`）。

### 方式 B — 从源码运行（开发者）

| 项目 | 要求 |
|------|------|
| Python | **3.10+** — [下载](https://www.python.org/downloads/)，安装时勾选 **Add Python to PATH** |
| Node.js | 仅在前端开发或重新构建 Web UI 时需要（建议 18+） |

### 安装 Python 依赖

在**管理员**命令提示符中执行（`keyboard` 需要管理员权限才能全局注入按键）：

```bash
pip install -r requirements.txt
```

- `keyboard` — 必需，全局热键与虚拟按键注入
- `aiohttp` — 可选；无则无法启动 Web UI（核心 TCU 可 headless 运行）
- `pypresence` — 可选，Discord 富状态

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

> 手柄/方向盘的换挡键可与上述键盘绑定**同时生效**。TCU 仅通过键盘注入 **E** / **Q**，不会占用油门、转向或其它轴输入。

### 3. 遥测数据输出（Data Out）

**设置 → HUD 与游戏 → Data Out**：

| 选项 | 值 |
|------|-----|
| Data Out | **开** |
| IP 地址 | `127.0.0.1` |
| 端口 | `5555` |
| 数据包格式 | **Car Dash**（324 字节） |

---

## 运行

### Release 版本（玩家推荐）

见上方 [系统要求](#系统要求) 中的**方式 A**。无需安装依赖，解压后以管理员运行 `VirtualTCU.exe` 即可。

### 从源码运行（开发者）

1. 以**管理员**身份打开命令提示符（推荐，确保换挡注入可靠）。
2. 进入项目目录并启动：

   ```bash
   cd path\to\virtualTCU
   python -m virtual_tcu
   ```

   也可使用兼容入口：`python virtual_tcu.py`

3. 在浏览器打开 **http://127.0.0.1:8765**。
4. 启动 FH6 并开始比赛；收到遥测后仪表盘会自动上线。
5. 在终端按 **Q** 退出程序。

### 首次使用或更新前端后

运行前先构建 Web UI（或使用已包含 `dist/` 的 GitHub Release 压缩包）：

```bash
cd web-ui
npm install
npm run build
```

构建产物输出到 `virtual_tcu/web/dist/`。未构建时，后端在 `/` 返回 HTTP **503** 提示页，而非仪表盘。

前端开发说明见 [web-ui/README.md](web-ui/README.md)。

---

## Web 仪表盘

连接成功后可在浏览器中查看：

- **档位 / 车速 / 转速** — 转速条按区间变色（绿 → 黄 → 橙 → 红）
- **油门 / 刹车** — 踏板百分比
- **TCU 状态** — 巡航、Kickdown、发动机制动等
- **涡轮 / 发动机** — 增压（Bar）、功率（kW）、扭矩（Nm）
- **统计与换挡历史** — 会话数据、学习进度
- **设置** — 实时调参并写入 `tcu_config.json`；支持导出/导入每车配置

界面语言可在页头切换（English / 简体中文）。

---

## 项目结构（简要）

```
virtualTCU/
├── virtual_tcu.py          # 入口（转发至 virtual_tcu.app）
├── virtual_tcu/            # Python 核心包
│   ├── logic/tcu.py        # 换挡逻辑与各驾驶模式
│   ├── telemetry/          # FH6 UDP 遥测解析
│   ├── web/                # Web 服务与 dist 静态资源
│   └── ...
├── web-ui/                 # Vue 3 + Tailwind v4 前端
├── tcu_config.json         # 运行时可调参数（开发：项目目录；Release：%APPDATA%\VirtualTCU）
├── tcu_profiles.json       # 每车配置存档（与 config 同路径规则）
└── logs/                   # 遥测回放日志（开发目录 / Release 为 APPDATA）
```

---

## 故障排除

### 仪表盘显示离线 / 等待 Forza

- 确认游戏内 **Data Out** 已开启，端口为 **5555**。
- 必须在**比赛中**（菜单内无遥测流）。
- 修改 Data Out 后建议重启游戏。

### TCU 不换挡 / 游戏内无反应

- 确认 Forza 键盘绑定：**E** 升档、**Q** 降档。
- 以**管理员**运行 CMD 后再启动 `python -m virtual_tcu`。

### F9 无法切换模式

- 关闭可能占用 F9 的软件（Discord 覆盖层、MSI Afterburner 等）。

### 档位或车速异常

- 本程序针对 **FH6 Car Dash（324 字节）** 数据包校准，不适用于 FH5 或 Forza Motorsport。

---

## 说明

- 适配 FH6 任意车辆 — 从遥测读取最大转速，换挡点按车自动校准。
- **倒档保护** — 倒档时不会自动换挡。
- **低速保护** — 约 12 km/h 以下不自动换挡，减少停车抖动。
- 仅发送 **E** / **Q** 键盘事件，不修改手柄或其它输入设备。

---

## 测试环境

- Windows 11
- Steam 版 Forza Horizon 6
- Xbox Elite Series 2 手柄

遥测结构基于 FH6 **324 字节 Car Dash** 数据包（实车诊断验证）。
