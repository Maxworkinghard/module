# Maxworkinghard/module

基于上游优秀开源脚本与模块自动同步的 Shadowrocket / Surge 模块仓库，由 GitHub Actions 每 6 小时自动同步更新。

> **提示**：内容版权归各原作者所有，本仓库负责统一维护、Shadowrocket 语法规范化兼容、自建 CDN 加速分发与自动化定时同步。

---

## 模块列表

国内网络推荐优先使用 **Fastly CDN 镜像链接**；境外或已开启全局代理可直接使用 **GitHub Raw 链接**。所有模块均同时提供 `.module`（Shadowrocket 专属）与 `.sgmodule`（Surge / Shadowrocket 通用）双版本。

### 1. 会员解锁与实用生产力

| 模块 | 说明 | 原作者 / 上游 | CDN 订阅链接 (推荐) | GitHub Raw 链接 |
| :--- | :--- | :--- | :--- | :--- |
| **RevenueCat** | 通用内购/订阅解锁，支持数十款集成 RevenueCat SDK 的热门 App（如 HabitKit、Pillow、Structured、Vision 等） | [Yu9191](https://github.com/Yu9191) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/RevenueCat.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/RevenueCat.module) |
| **扫描全能王** | 扫描全能王高级会员特权解锁、高清扫描导出、自动去除水印 | [chxm1023](https://github.com/chxm1023) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/CamScanner.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/CamScanner.module) |
| **彩云天气** | 彩云天气免广告、解锁 SVIP 权益、开启 48 小时逐小时精准降水预报与高质量卫星云图 | [chxm1023](https://github.com/chxm1023) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/CaiYun.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/CaiYun.module) |

### 2. 热门社交与影音增强

| 模块 | 说明 | 原作者 / 上游 | CDN 订阅链接 (推荐) | GitHub Raw 链接 |
| :--- | :--- | :--- | :--- | :--- |
| **YouTube** | YouTube / YouTube Music 去视频与信息流广告、解锁画中画 (PiP)、支持后台/锁屏持续播放 | [Maasea](https://github.com/Maasea/sgmodule) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/YouTube.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/YouTube.module) |
| **TikTok** | TikTok 免拔卡换区、解锁全球区域 (默认美区 US，可自定义)、视频下载去水印与广告过滤 | [Keywos & lodepuly](https://github.com/Keywos/rule) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/TikTok.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/TikTok.module) |
| **小红书** | 小红书开屏/信息流去广告、无水印保存 4K 原图/视频、无水印保存 LivePhoto 实况动图 | [奶思 (fmz200)](https://github.com/fmz200/wool_scripts) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/XiaoHongShu.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/XiaoHongShu.module) |
| **知乎** | 哲也同学知乎净化：去除信息流/回答/热榜广告、屏蔽盐选付费故事营销引导、折叠垃圾推广 | [blackmatrix7](https://github.com/blackmatrix7/ios_rule_script) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Zhihu.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Zhihu.module) |
| **Twitter_Instagram** | Twitter (X) 与 Instagram 商业广告拦截、数据上报与分析追踪屏蔽 | [fmz200 & blackmatrix7](https://github.com/fmz200/wool_scripts) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Twitter_Instagram.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Twitter_Instagram.module) |
| **bilibili** | B站去广告兼容版：开屏/首页推荐流/视频页/动态/底层Tab净化（原生 json+proto 处理，Shadowrocket 深度调优） | 本仓库自维护 | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/bilibili.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/bilibili.module) |

### 3. 黑科技与网络实用工具

| 模块 | 说明 | 原作者 / 上游 | CDN 订阅链接 (推荐) | GitHub Raw 链接 |
| :--- | :--- | :--- | :--- | :--- |
| **Sub-Store** | 高级订阅与节点管理神器：多机场/自建节点聚合清洗、去除死节点、国旗 Emoji 重命名、测速排序 | [Peng-YM / sub-store-org](https://github.com/sub-store-org/Sub-Store) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Sub-Store.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Sub-Store.module) |
| **BoxJs** | 本地 Web 管理控制台：管理所有脚本的设置、授权 Cookie、环境变量与订阅配置 | [ChavyLeung](https://github.com/chavyleung/scripts) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/BoxJs.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/BoxJs.module) |
| **wloc** | 苹果 WLOC 网络定位修改：欺骗系统 Wi-Fi 定位接口，支持网页交互选点与快捷指令无缝切换 | [Yu9191](https://github.com/Yu9191/wloc) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/wloc.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/wloc.module) |
| **weixin110** | 微信外链解锁：自动跳过拦截提示，直接 302 重定向到原始网页链接 | [ddgksf2013](https://github.com/ddgksf2013) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/weixin110.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/weixin110.module) |
| **HTTPDNS** | HTTPDNS / 私有 DoH 拦截：阻断腾讯、阿里、微博等私有 DNS 探测，强制走代理软件 DNS 规则 | 本仓库自维护 | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/HTTPDNS.module) | [Raw 链接](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/HTTPDNS.module) |


### 4. 规则合集模块

| 模块 | 说明 | 上游 | 订阅链接 |
| :--- | :--- | :--- | :--- |
| **rewrite** | 广告拦截合集-重写（约 730 款 APP，已过滤 Bilibili 冲突规则） | [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/rewrite.module) |
| **cleanup** | App & 小程序净化合集（约 88 款，已过滤 Bilibili 冲突规则） | [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/cleanup.module) |
| **Adblock** | 综合去广告集合（已过滤 Bilibili 冲突规则） | [bai1zi](https://github.com/bai1zi/shadowrocket-surge-loon-qx) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Adblock.module) |
| **FuckAppsAD** | 多应用去广告（已过滤 Bilibili 冲突规则） | [uxudjs](https://github.com/uxudjs/Shadowrocket) | [导入链接](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/FuckAppsAD.module) |

---

## 安装与配置

1. **Shadowrocket 导入**：
   - 打开 Shadowrocket -> 点击下方 **配置** -> 进入 **模块**。
   - 点击右上角 **`+`**，粘贴上方模块的 CDN 订阅链接。
   - 勾选启用该模块。
2. **前提条件（必须开启 HTTPS 解密）**：
   - 必须开启 **HTTPS 解密 (MITM)** 并生成并信任 CA 证书（iOS 系统设置 -> 通用 -> 关于本机 -> 证书信任设置 -> 打开完全信任）。
   - 去广告、去水印、会员修改、BoxJs 以及定位修改均依赖 MITM 注入。

---

## 重点模块详细使用说明

### 1. BoxJs（脚本管理利器）
* **原理**：BoxJs 是运行在手机代理内核中的本地 Web 服务。启用模块后，它会在本地拦截 `boxjs.com` 和 `boxjs.net` 的 HTTP 请求，直接将管理面板渲染在浏览器中。**完全不需要远程服务器，零网络延迟，数据安全保存在本地**。
* **访问方法**：
  1. 开启包含 BoxJs 模块的 VPN 连接。
  2. 使用 Safari 浏览器直接打开 [http://boxjs.com](http://boxjs.com) 或 [http://boxjs.net](http://boxjs.net)。
* **主要用途**：
  - **应用订阅配置**：在面板中可添加大佬们维护的订阅链接（如签到脚本、Cookie获取等）。
  - **应用参数修改**：针对支持 BoxJs 的脚本，可通过可视化开关直接调整选项，不用手动改代码。
  - **数据备份与迁移**：导入/导出备份所有脚本的环境变量与授权 Token。

### 2. wloc（苹果网络定位修改）
* **定位修改方式**：
  - 网页可视化选点：浏览器访问 `http://wloc.net` 选择地图上的目标坐标。
  - 快捷指令联动：运行预设快捷指令直接更新坐标。
* 详细说明与快捷指令安装请参考模块内注释。

---

## 定时同步机制

- 仓库内集成了 GitHub Actions 自动化工作流（`.github/workflows/sync.yml`），**每 6 小时自动触发一次** (`0 */6 * * *`)。
- 自动化同步引擎（`scripts/sync.py`）会自动执行：
  1. 从 upstream 拉取并更新所有依赖的独立 JavaScript 脚本。
  2. 同步通用去广告合集并自动过滤冲突域名规则。
  3. 规范化模块语法为 Shadowrocket 完美兼容格式（去除多余空格，修正参数格式）。
  4. 自动生成与更新 `.module` 与 `.sgmodule` 双版本文件并提交推送。