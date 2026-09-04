# Maxworkinghard/module

基于上游模块自动同步的 Shadowrocket 模块仓库，由 GitHub Actions 自动同步更新。

> 内容版权归原作者所有，本仓库仅做同步与分发。

## 模块列表

| 模块 | 说明 | 上游 | 订阅链接 |
| --- | --- | --- | --- |
| rewrite | 广告拦截合集-重写（约730款APP，经 Script-Hub 转换为 Shadowrocket 模块） | [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts) | https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/rewrite.sgmodule |
| cleanup | App&小程序净化合集（约88款，经 Script-Hub 转换） | [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts) | https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/cleanup.sgmodule |
| Adblock | 去广告集合 | [bai1zi/shadowrocket-surge-loon-qx](https://github.com/bai1zi/shadowrocket-surge-loon-qx) | https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Adblock.sgmodule |
| FuckAppsAD | 多应用去广告（墨迹天气/联通/淘票票/知乎/小红书等） | [uxudjs/Shadowrocket](https://github.com/uxudjs/Shadowrocket) | https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/FuckAppsAD.sgmodule |
| bilibili | B站去广告（Shadowrocket 兼容版：开屏/推荐流/视频页/动态/tab，json+proto 脚本） | 本仓库自维护 | https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/bilibili.sgmodule |
| HTTPDNS | HTTPDNS/私有 DNS 拦截（防止 App 绕过 Shadowrocket 的 DNS 框架） | 本仓库自维护 | https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/HTTPDNS.sgmodule |
| Enhanced | BiliUniverse B站界面增强 | [BiliUniverse/Enhanced](https://github.com/BiliUniverse/Enhanced) | https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Enhanced.sgmodule |
| Global | BiliUniverse B站地区解锁/线路切换 | [BiliUniverse/Global](https://github.com/BiliUniverse/Global) | https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Global.sgmodule |
| Redirect | BiliUniverse B站CDN重定向 | [BiliUniverse/Redirect](https://github.com/BiliUniverse/Redirect) | https://raw.githubusercontent.com/Maxworkinghard/module/main/modules/Redirect.sgmodule |

## 安装

Shadowrocket - 配置 - 模块 - 右上角 `+` - 粘贴上方订阅链接 - 启用模块

需开启 HTTPS 解密(MITM) 并信任证书，广告/净化模块才能生效。

## 使用说明

- `modules/` 大部分由同步自动生成；`bilibili.sgmodule`、`HTTPDNS.sgmodule` 及 `scripts/bilibili-*.js` 为本仓库自维护
- 新增/修改上游请在 `config/upstream.yml` 中配置
- 可手动触发同步：仓库 Actions - Sync Upstream Modules - Run workflow
- BiliUniverse 模块（Enhanced/Global/Redirect）官方不支持 Shadowrocket，同步时已剥离脚本，仅保留静态规则

### 关于 B 站

通用去广告模块（rewrite/cleanup/Adblock/FuckAppsAD）在同步时会自动剔除 bilibili 相关规则
（`filters.bilibili`，可自行修改），避免多个模块同时 MITM 同一批 B 站域名导致
评论 / 相关推荐 / 历史记录 / 搜索接口打不开。B 站去广告由 `bilibili.sgmodule` 单独负责。

原 BiliUniverse ADBlock 已退役：官方不支持 Shadowrocket，剥离脚本后仅剩静态规则、功能不全，
且与 bilibili.sgmodule 的 MITM 域名和接口重叠，二者不要同时启用。

## 上游

- [fmz200/wool_scripts](https://github.com/fmz200/wool_scripts) - 奶思的模块 (通过 [Script-Hub](https://script.hub) 转换)
- [bai1zi/shadowrocket-surge-loon-qx](https://github.com/bai1zi/shadowrocket-surge-loon-qx) - 去广告集合
- [uxudjs/Shadowrocket](https://github.com/uxudjs/Shadowrocket) - FuckAppsAD
- [BiliUniverse](https://github.com/BiliUniverse) - 哔哩万象 B站增强系列 (Enhanced/Global/Redirect，ADBlock 已由本仓库自维护 bilibili.sgmodule 替代)