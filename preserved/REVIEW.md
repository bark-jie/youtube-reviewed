# 原功能保留版审查 — 2026-09-21

以用户本次提供的 `YouTube_Music_Enhance_Screenshot_Reconstructed.sgmodule` 为边界。结论：未发现该模块实际引用的响应脚本存在重大安全问题，候选脚本逐字节保留，不沿用旧版本对功能的删减。静态审查与合成测试不构成绝对安全或手机效果保证。

- 固定上游：Maasea/sgmodule，提交 `65075cdb388fc5e3094afd7e7314c67b243f3525`，路径 `Script/Youtube/youtube.response.js`。
- Git blob：`becad8eaa6094c189ea8db6d644de68ac2d66f61`。
- SHA-256：`f98483d5f5017514f82502253c0db5ce2d4ffb7839887aa2cadc22666f5a7f12`。
- 模块仅将一个 `script-path` URL 换为本仓库 `main/scripts/youtube.original.response.js`。参数、名称、匹配、max-size、规则和 MITM 均不改。未添加未经确认的刷新间隔字段。

检查了入口 Ki/ii 与实际分派、广告过滤 Ni/Ir/Di、后台与画中画 Si、字幕 Pi、导航 $i、设置 ji、持久化以及网络适配器。大部分打包内容为 protobuf 类型与编解码实现。未发现 eval/new Function/外部 require 或下载后执行；通用 fetch 适配器存在，但当前业务调用链没有调用。唯一 HTTP 字符串是 protobuf 文档地址；字幕选项对原有字幕 URL 添加 tlang，不新增第三方域名。

脚本会读取本地 YouTubeAdvertiseInfo 和 YouTubeConfig；广告分类改变时保存分类缓存及已有配置。config/log_event 分派包含本地播放密钥提取代码，但用户模块不匹配这些入口；合法匹配路径先命中自身分派，查询字符串不会使其跳入 config/log_event。没有发现 Cookie/Authorization 读取或主动外发调用。不把“包含密钥相关类型”误报为本模块实际收集或上传。

新上游完整模块中的请求中转不是用户提供模块的依赖，不引入 `youtube.request.js`、Worker 中转或额外匹配。保持原有功能也保留上游的一般兼容性限制：缺少 playabilityStatus、异常缓存或异常 protobuf 可能导致回退原响应；max-size=-1 保持原样。未因这些普通问题擅自修订脚本。

15 个合成行为用例通过，覆盖 YouTube/Music player 广告删除与画中画/后台保留、get_watch、Shorts、空列表、设置修改、畸形输入回退及查询字符串入口边界。检测到的网络调用为 0。模块与原文件比较仅有 URL 替换。另验证 24 小时门槛的提前一毫秒、恰好到期、未来时间、非法时间。未进行 iOS 实机测试。

本次先存候选。以 GitHub 实际候选提交时间为起点，满 24 小时后才在单一提交中开放正式脚本和模块；首次版本同样等待。候选入库不代表正式发布。旧模块入口在等待期保持原状。
