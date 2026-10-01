# Maxworkinghard/module

用于 Shadowrocket 的个人模块聚合仓库。所有导入链接与 script-path 均指向 **Maxworkinghard/module**，保留原作者署名和上游来源。GitHub Actions 每 6 小时检查一次，只有完整检查通过才发布。

每个模块同时提供内容相同的 .module 与 .sgmodule 文件。文件扩展名不会自动解决客户端或 App 版本差异；HTTPS 重写需要在设备上验证。

## 推荐组合

**只想导入一个地址：使用 [DailyAds · 日用去广告合集](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/DailyAds.module)。**

它由本仓库自动合并以下十个模块：GeneralAds、Adblock、BiliSplash、YouTube、TikTokAds、XianYu、Taobao、JD、Pinduoduo、CaiNiao。

| 范围 | 合集中的处理 | 作者 / 原始来源 |
| :--- | :--- | :--- |
| 通用广告 | AWAvenue Only.Ads 广告域名阻断 | [TG-Twilight/AWAvenue-Ads-Rule](https://github.com/TG-Twilight/AWAvenue-Ads-Rule) |
| 其他 App 开屏 | 当前 startingad 综合开屏规则，过滤专用模块负责的 App | [yfamilys](https://yfamilys.com/module/startingad.module) / ddgksf2013 / deezertidal |
| B 站开屏 | 开屏广告接口返回空 JSON，无需 JS | [splash 接口参考](https://github.com/NADYuk0314/shadowrocket-adblock/blob/main/src/additions/30-bilibili.conf) / 本仓库维护 |
| YouTube | 广告与播放接口处理；字幕翻译关闭，保留 Shorts、上传和选段按钮 | [Maasea/sgmodule](https://github.com/Maasea/sgmodule) |
| TikTok | JSON 信息流显式广告项过滤，保留直播；不修改地区和下载设置 | 本仓库维护；[接口参考 Jard1n](https://github.com/Jard1n/VPN_Tool/blob/master/Scripts/TikTok/TikTok_remove_watermark.js) |
| 闲鱼 | 开屏、首页与搜索广告及部分推荐净化；不处理个人工具栏和频道接口 | [fmz200 原生模块](https://github.com/fmz200/wool_scripts/blob/main/Shadowrocket/module/split/partX/XianYu.srmodule) / [ishowshu](https://github.com/ishowshu/qx/blob/main/script/goofish.js) |
| 淘宝 | 开屏图片、视频、活动弹层和广告域名 | [fmz200](https://github.com/fmz200/wool_scripts/blob/main/Shadowrocket/module/split/partT/Taobao.srmodule) |
| 京东 | 开屏、直播小窗和订单 / 物流页推广 | [fmz200](https://github.com/fmz200/wool_scripts/blob/main/Shadowrocket/module/split/partJ/JD.com.srmodule) |
| 拼多多 | 开屏和物流红包商品广告；保留首页接口 | [fmz200](https://github.com/fmz200/wool_scripts/blob/main/Shadowrocket/module/split/partP/Pinduoduo.srmodule) |
| 菜鸟 | 广告、商品推广和问卷净化；不处理取件、消息和首页导航接口 | [fmz200](https://github.com/fmz200/wool_scripts/blob/main/Shadowrocket/module/split/partC/CaiNiaoGuoGuo.srmodule) |

**启用 DailyAds 后，停用它包含的十个拆分模块、rewrite 及旧 TikTok 模块。也不要同时启用 bilibili 完整模块，它与 BiliSplash 的开屏规则有重叠。** 拆分模块的用途是按 App 选择功能或排查问题，不能与同一合集重复启用。

如果原先依赖 TikTok 的免拔卡换区，在停用旧 TikTok 组合模块后，另启用 [TikTokRegion](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/TikTokRegion.module)。它只处理换区请求，可与 DailyAds / TikTokAds 搭配，默认地区 US；地区选择还需合适的代理节点。

小红书、知乎、微信外链和 Sub-Store 可按需单独启用，DailyAds 不包含它们。cleanup 覆盖更多 App / 小程序界面净化，容易与开屏处理交叉，建议确认需要后再启用。HTTPDNS 可用于有明确分流绕过问题的场景。

已停用 **FuckAppsAD、RevenueCat**，请在客户端删除或关闭。旧订阅地址保留停用提示文件，更新后不再加载旧脚本。

如果只想用拆分模块，通用层选择 **GeneralAds + Adblock**，再添加需要的专用模块；Adblock 与 rewrite 二选一。B 站仅去开屏用 BiliSplash，需要更多广告 / 评论接口处理时可改用 bilibili，二者选一。

## 模块链接

刚发布更新时优先使用 Raw 链接；CDN 链接可能存在缓存。以下模块适配的是脚本覆盖的接口，实际效果取决于 App 与代理客户端版本。

| 模块 | 用途 / 来源 | Raw 导入链接 | CDN 导入链接 |
| :--- | :--- | :--- | :--- |
| **DailyAds（推荐）** | 一个地址，包含上表的通用、开屏、视频和购物模块 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/DailyAds.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/DailyAds.module) |
| **GeneralAds** | AWAvenue Only.Ads；仅域名阻断，无需 HTTPS 解密 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/GeneralAds.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/GeneralAds.module) |
| **BiliSplash** | B 站开屏专用；无需 JS，需要 HTTPS 解密 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/BiliSplash.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/BiliSplash.module) |
| **TikTokAds** | 保守 JSON 信息流广告过滤，无换区 / 水印处理 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/TikTokAds.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/TikTokAds.module) |
| **TikTokRegion（按需）** | Keywos 免拔卡换区，默认 US；可与 DailyAds / TikTokAds 搭配 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/TikTokRegion.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/TikTokRegion.module) |
| **闲鱼** | 开屏、信息流广告及部分推荐净化 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/XianYu.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/XianYu.module) |
| **淘宝** | 开屏图片 / 视频、活动弹层和广告域名 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Taobao.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Taobao.module) |
| **京东** | 开屏、浮窗和订单 / 物流页推广 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/JD.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/JD.module) |
| **拼多多** | 开屏与物流红包商品广告 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Pinduoduo.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Pinduoduo.module) |
| **菜鸟** | 广告、推广和问卷净化 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/CaiNiao.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/CaiNiao.module) |
| **Adblock** | 通用开屏去广告；[yfamilys / deezertidal](https://github.com/deezertidal/shadowrocket-rules)，原脚本署名 ddgksf2013 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Adblock.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Adblock.module) |
| **rewrite** | 通用广告重写；[fmz200](https://github.com/fmz200/wool_scripts)，经 Script-Hub 转换 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/rewrite.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/rewrite.module) |
| **cleanup** | App 与小程序界面净化；[fmz200](https://github.com/fmz200/wool_scripts)，经 Script-Hub 转换 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/cleanup.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/cleanup.module) |
| **bilibili** | B 站广告接口处理；[fmz200 原生模块](https://github.com/fmz200/wool_scripts/blob/main/Shadowrocket/module/split/partB/bilibili.srmodule) / [kokoryh Sparkle](https://github.com/kokoryh/Sparkle)，固定 JSON 参数 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/bilibili.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/bilibili.module) |
| **小红书** | 广告过滤与图片 / 视频水印处理；[fmz200](https://github.com/fmz200/wool_scripts) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/XiaoHongShu.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/XiaoHongShu.module) |
| **知乎** | 信息流及回答等页面净化；[blackmatrix7](https://github.com/blackmatrix7/ios_rule_script) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Zhihu.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Zhihu.module) |
| **YouTube** | 当前 YouTube Enhance 广告与播放接口处理；[Maasea](https://github.com/Maasea/sgmodule) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/YouTube.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/YouTube.module) |
| **TikTok（可选替代）** | 旧换区与水印处理方案，默认地区 US；[Keywos](https://github.com/Keywos/rule) / [lodepuly](https://github.com/Jard1n/VPN_Tool)，不要与 DailyAds / TikTokAds 同时启用 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/TikTok.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/TikTok.module) |
| **Twitter_Instagram** | 部分广告域名与统计请求阻断；不处理原生信息流响应 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Twitter_Instagram.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Twitter_Instagram.module) |
| **彩云天气** | 天气接口广告与功能处理；[chxm1023](https://github.com/chxm1023/Rewrite) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/CaiYun.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/CaiYun.module) |
| **扫描全能王** | 扫描全能王功能接口处理；[chxm1023](https://github.com/chxm1023/Rewrite) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/CamScanner.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/CamScanner.module) |
| **HTTPDNS** | 部分私有 HTTPDNS / DoH 请求阻断；本仓库维护 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/HTTPDNS.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/HTTPDNS.module) |
| **weixin110** | 微信外链提示页重定向 | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/weixin110.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/weixin110.module) |
| **BoxJs** | 脚本设置管理面板；[ChavyLeung](https://github.com/chavyleung/scripts) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/BoxJs.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/BoxJs.module) |
| **Sub-Store** | 订阅管理；[sub-store-org](https://github.com/sub-store-org/Sub-Store) | [导入](https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Sub-Store.module) | [CDN](https://fastly.jsdelivr.net/gh/Maxworkinghard/module@main/modules/Sub-Store.module) |

YouTube 上游明确以 Surge 为测试环境，不保证其他客户端兼容。本仓库同步当前模块和脚本并固定 JSON 参数，下载检查不等同于 iPhone 上的广告过滤、后台播放或画中画实测。TikTokAds 只处理能被 HTTPS 解密的 JSON 信息流；若 App 使用其他接口、二进制响应或证书绑定，该规则不会覆盖。

B 站模块保留最常访问列表，关闭赞助片段跳过；过滤上游的账户会员字段修改及整套导航重建。广告接口可能随 App 更新而变化，仍需在设备上验证。

## 安装与迁移

1. 在 Shadowrocket 的配置 / 模块页面，添加所需模块的导入链接并启用。
2. 对带 [MITM] 的 HTTPS 重写模块，开启 HTTPS 解密，安装 CA 证书并在 iOS 证书信任设置中完全信任。仅域名阻断的模块不要求 HTTPS 解密。
3. 推荐添加 DailyAds 并启用，关闭 Adblock、GeneralAds、BiliSplash、YouTube、TikTokAds、闲鱼、淘宝、京东、拼多多、菜鸟的拆分模块，以及 rewrite、旧 TikTok 和 bilibili 完整模块。停用已退役的 FuckAppsAD、RevenueCat。
4. 若使用的是其他仓库的旧 AdBlock.module、startingad.module 或 YouTubeAd.sgmodule，关闭旧模块并改用本仓库链接。GitHub 仓库首页不能作为模块导入地址，使用上表的 Raw 文件链接。
5. 更新后重新连接代理，重新打开目标 App。若广告仍在，检查模块是否更新成功、证书是否信任及该 App 的请求是否命中模块。

BoxJs 启用后可通过 Safari 访问 [http://boxjs.com](http://boxjs.com) 或 [http://boxjs.net](http://boxjs.net) 管理脚本参数。

## 2026-10-01 聚合更新

- 新增 DailyAds，合并十个功能模块，合并 MITM 域名、去除完全重复的规则并生成独立脚本名称。
- 综合开屏来源中省略中间占位符的 reject 行，统一补为 Shadowrocket 的 `URL - reject` 三字段格式。
- 新增 AWAvenue 通用广告域名、B 站开屏专用、TikTok 广告专用及五个购物 / 物流专用模块。
- 单独提供 TikTokRegion，保留需要免拔卡换区的用户的可选方案，可与日用广告合集搭配。
- YouTube 改为同步当前 YouTube Enhance 模块与脚本，关闭翻译并保留操作按钮。
- 闲鱼过滤个人工具栏和频道接口的裁剪；拼多多移除整段首页接口阻断；菜鸟过滤取件、消息、首页导航及 AMDC 处理；京东过滤私有 DNS 阻断。
- 所有 script-path 均改为本仓库 Raw 链接，镜像脚本保留内容与作者注释，来源和 SHA-256 记录在 [scripts/upstream.json](scripts/upstream.json)。镜像每轮从作者地址更新，失效来源会使整轮发布失败。
- 保留 AWAvenue 的 GPL-3.0 许可证：[licenses/AWAvenue-GPL-3.0.txt](licenses/AWAvenue-GPL-3.0.txt)。GeneralAds 和含这些规则的 DailyAds 保留此许可，其他作者内容遵循各自的许可与声明。

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

同步先下载到内存并处理过滤，再镜像脚本、生成合集并检查所有 .sgmodule 文件中的脚本引用。第三方脚本实际下载检查 HTTP 结果、文件内容及 JavaScript 语法；本仓库链接检查待发布文件。未配置刷新来源的现有模块，其镜像脚本也会根据来源记录继续更新。全部检查通过后，才写入模块、脚本、来源清单及内容一致的 .module 文件。任何来源失败都不发布该轮变更，工作流会保留错误日志。

开发验证：

~~~sh
python -m unittest discover -s scripts -p 'test_*.py'
node scripts/test_tiktok_ads.js
python scripts/sync.py
~~~

完整同步需要 PyYAML 与 Node.js，并在 127.0.0.1:9100 启动 [Script-Hub](https://github.com/Script-Hub-Org/Script-Hub) 转换服务。工作流会自动启动服务；使用 node --check 检查语法，不执行第三方广告脚本。这不能验证 Shadowrocket 的脚本 API 或 iPhone 上的实际运行行为。
