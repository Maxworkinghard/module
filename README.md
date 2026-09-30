# Maxworkinghard/module

用于 Shadowrocket 的模块与脚本仓库。保留原作者署名，按当前可用上游同步；GitHub Actions 每 6 小时检查一次，只有完整检查通过才发布。

每个模块同时提供内容相同的 .module 与 .sgmodule 文件。文件扩展名不会自动解决客户端或 App 版本差异；HTTPS 重写需要在设备上验证。

## 推荐组合

- 通用开屏去广告使用 **Adblock**。它已替换为 [yfamilys 当前维护的 startingad.module](https://yfamilys.com/module/startingad.module)，保留本仓库原来的 Adblock 订阅地址。
- **Adblock 与 rewrite 二选一**，避免叠加两套综合去广告规则。rewrite 保留 [fmz200 的当前重写合集](https://github.com/fmz200/wool_scripts/tree/main/QuantumultX/rewrite)。
- B 站、小红书、知乎、YouTube、彩云天气及微信外链按需要启用对应专用模块。通用合集已过滤这些 App 的规则及 MITM 域名，包括 api\.(bilibili|biliapi) 这种组合写法。
- cleanup 是额外的 App / 小程序界面净化，按需要单独启用；遇到某个 App 加载异常时，可先停用它排查。
- 已停用 **FuckAppsAD、RevenueCat**，请在客户端删除或关闭。旧订阅地址保留停用提示文件，更新后不再加载旧脚本。

## 模块链接

刚发布更新时优先使用 Raw 链接；CDN 链接可能存在缓存。以下模块适配的是脚本覆盖的接口，实际效果取决于 App 与代理客户端版本。

| 模块 | 用途 / 来源 | Raw 导入链接 | CDN 导入链接 |
| :--- | :--- | :--- | :--- |
| **Adblock** | 通用开屏去广告；[yfamilys / deezertidal](https://github.com/deezertidal/shadowrocket-rules)，原脚本署名 ddgksf2013 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Adblock.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Adblock.module) |
| **rewrite** | 通用广告重写；[fmz200](https://github.com/fmz200/wool_scripts)，经 Script-Hub 转换 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/rewrite.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/rewrite.module) |
| **cleanup** | App 与小程序界面净化；[fmz200](https://github.com/fmz200/wool_scripts)，经 Script-Hub 转换 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/cleanup.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/cleanup.module) |
| **bilibili** | B 站广告接口处理；[fmz200 原生模块](https://github.com/fmz200/wool_scripts/blob/main/Shadowrocket/module/split/partB/bilibili.srmodule) / [kokoryh Sparkle](https://github.com/kokoryh/Sparkle)，固定 JSON 参数 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/bilibili.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/bilibili.module) |
| **小红书** | 广告过滤与图片 / 视频水印处理；[fmz200](https://github.com/fmz200/wool_scripts) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/XiaoHongShu.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/XiaoHongShu.module) |
| **知乎** | 信息流及回答等页面净化；[blackmatrix7](https://github.com/blackmatrix7/ios_rule_script) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Zhihu.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Zhihu.module) |
| **YouTube** | YouTube 接口广告处理与播放功能调整；[Maasea](https://github.com/Maasea/sgmodule) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/YouTube.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/YouTube.module) |
| **TikTok** | 换区与水印 / 广告处理；[Keywos](https://github.com/Keywos/rule) / [lodepuly](https://github.com/Jard1n/VPN_Tool) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/TikTok.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/TikTok.module) |
| **Twitter_Instagram** | 部分广告域名与统计请求阻断；不处理原生信息流响应 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Twitter_Instagram.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Twitter_Instagram.module) |
| **彩云天气** | 天气接口广告与功能处理；[chxm1023](https://github.com/chxm1023/Rewrite) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/CaiYun.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/CaiYun.module) |
| **扫描全能王** | 扫描全能王功能接口处理；[chxm1023](https://github.com/chxm1023/Rewrite) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/CamScanner.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/CamScanner.module) |
| **HTTPDNS** | 部分私有 HTTPDNS / DoH 请求阻断；本仓库维护 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/HTTPDNS.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/HTTPDNS.module) |
| **weixin110** | 微信外链提示页重定向 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/weixin110.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/weixin110.module) |
| **BoxJs** | 脚本设置管理面板；[ChavyLeung](https://github.com/chavyleung/scripts) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/BoxJs.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/BoxJs.module) |
| **Sub-Store** | 订阅管理；[sub-store-org](https://github.com/sub-store-org/Sub-Store) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Sub-Store.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Sub-Store.module) |

YouTube 上游明确以 Surge 为测试环境，不保证其他客户端兼容。本仓库使用已展开参数的模块和当前脚本，下载检查不等同于 iPhone 上的广告过滤、后台播放或画中画实测。

B 站模块保留最常访问列表，关闭赞助片段跳过；过滤上游的账户会员字段修改及整套导航重建。广告接口可能随 App 更新而变化，仍需在设备上验证。

## 安装与迁移

1. 在 Shadowrocket 的配置 / 模块页面，添加所需模块的导入链接并启用。
2. 对带 [MITM] 的 HTTPS 重写模块，开启 HTTPS 解密，安装 CA 证书并在 iOS 证书信任设置中完全信任。仅域名阻断的模块不要求 HTTPS 解密。
3. 已导入本仓库 Adblock 的用户，更新这个模块即可；停用 FuckAppsAD 后启用 Adblock。不要同时启用 Adblock 与 rewrite。
4. 若使用的是其他仓库的旧 AdBlock.module、startingad.module 或 YouTubeAd.sgmodule，删除旧模块并改用上表相应链接。更新本仓库无法更新其他作者的旧订阅地址。
5. 更新后重新连接代理，重新打开目标 App。若广告仍在，检查模块是否更新成功、证书是否信任及该 App 的请求是否命中模块。

BoxJs 启用后可通过 Safari 访问 [http://boxjs.com](http://boxjs.com) 或 [http://boxjs.net](http://boxjs.net) 管理脚本参数。

## 2026-09-30 清理记录

| 内容 | 处理 |
| :--- | :--- |
| Adblock 的旧 bai1zi 快照 | 改用作者网站当前维护的开屏去广告模块，保留本仓库 Adblock 地址及原作者信息 |
| FuckAppsAD | 移除旧规则与全部脚本引用，提供停用提示；旧合集含失效的滴滴、小红书等脚本，以及返回网页的百度网盘 / 知乎脚本 |
| RevenueCat | 原独立脚本地址返回 404，移除缓存脚本和同步配置，模块地址提供停用提示 |
| bilibili | 移除有乱码语法错误的 JSON 脚本与旧 Protobuf 缓存，改用 fmz200 原生模块和 kokoryh 当前脚本；修正 JSON 参数格式 |
| rewrite / cleanup | 从 fmz200 当前上游重新转换；统一过滤专用 App 规则 |
| 自动同步 | 检查脚本引用及 JavaScript 语法、拒绝空文件 / HTML / 未展开参数；失败时保留旧版本并让工作流失败 |

源码日期本身不作为删除依据；仍可获取、被现有模块使用的脚本继续保留。功能是否仍适配 App 新版本，需要设备上的实际验证。

## 同步维护

配置入口为 [config/upstream.yml](config/upstream.yml)，同步实现为 [scripts/sync.py](scripts/sync.py)。

同步先下载到内存并处理过滤，再检查所有 .sgmodule 文件中的脚本引用。本仓库脚本链接检查待发布文件；第三方脚本链接实际下载检查 HTTP 结果、文件内容及 JavaScript 语法。全部检查通过后，才写入模块、脚本并生成内容一致的 .module 文件。任何来源失败都不发布该轮变更，工作流会保留错误日志。

开发验证：

~~~sh
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/sync.py
~~~

完整同步需要 PyYAML 与 Node.js，并在 127.0.0.1:9100 启动 [Script-Hub](https://github.com/Script-Hub-Org/Script-Hub) 转换服务。工作流会自动启动服务；使用 node --check 检查语法，不执行第三方广告脚本。这不能验证 Shadowrocket 的脚本 API 或 iPhone 上的实际运行行为。
