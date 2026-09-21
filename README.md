# YouTube Reviewed

Shadowrocket 去广告模块，版本 1.0.1。仓库已公开，无需 GitHub 令牌。使用自己在小火箭中生成的 MITM 证书。

## 安装

1. 复制模块地址，到小火箭「配置 → 模块 → ＋」添加并启用：

   https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/YouTube-Reviewed.sgmodule

2. 停用原来的 YouTube 模块，避免重复改写。如果装过本项目的 Private 版本，也停用并换成此链接。
3. 在当前配置中启用 HTTPS 解密，使用小火箭自己生成的证书；在 iOS 安装描述文件后，到「设置 → 通用 → 关于本机 → 证书信任设置」开启该证书的完全信任。已经完成且证书有效则不用重装。不要使用别人给的证书或私钥。
4. 全局路由设为「配置」，连接小火箭；必要时手动更新一次外部脚本资源，再重启 YouTube 测试普通视频、Shorts、搜索及 YouTube Music。

不需要填写模块参数、GitHub 令牌或下载本地脚本。如果已生成仅供本模块使用的 GitHub 令牌，可在 GitHub 设置中撤销；没生成则无需处理。

## 更新与限制

脚本从本仓库 main/scripts/youtube.response.js 下载，模块设置 script-update-interval=86400（一天）。实际刷新仍受小火箭版本、缓存、联网及更新设置影响，不能保证每 24 小时必定执行。模块规则本身改变时也需刷新远程模块；维护任务会在需要操作时通知。

Codex 每日检查上游，审查并测试后才发布正常兼容更新；发现可疑变化保留旧版。任务依赖本机 Codex 可运行与联网，不是 GitHub 云端全天候审计。公开可读不代表任何人可修改，写入仍受仓库权限控制；审查也不保证零漏洞。

本版保留原响应脚本的广告过滤算法和原模块 oad 拦截，排除新上游向第三方 Worker 转发播放请求的逻辑，以及播放密钥采集、字幕翻译、后台播放/画中画和导航/设置修改。可能弱于最新版完整上游的去广告效果。15 项合成测试通过，但手机实际广告效果和自动刷新尚未验证。

解密主机仅 youtubei.googleapis.com 和 *.googlevideo.com，不再解密 GitHub 下载主机或注入鉴权头。响应超过 4 MiB 时不处理，解析异常时保留原响应。只保留本地广告分类缓存，当前响应入口不主动联网。

如出现不能播放或异常，先关闭模块确认是否恢复。彻底停用且证书无其他用途时，可关闭 HTTPS 解密并移除证书。

## 来源和审查

- 来源：https://github.com/Maasea/sgmodule/tree/65075cdb388fc5e3094afd7e7314c67b243f3525
- 审查：REVIEW.md；维护约束：MAINTENANCE.md；哈希：review-state.json。
- 旧文件名 YouTube-Reviewed-Private.sgmodule 仅为兼容入口，内容也已改为无令牌公开版。
- Apache-2.0，见 LICENSE 和 NOTICE。不是 YouTube、Google、Shadowrocket 或 Maasea 官方发行版。

仓库只含代码、来源、测试和说明，不应提交令牌、证书、Cookie、代理节点、订阅或个人观看数据。
