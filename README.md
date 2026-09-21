# YouTube Reviewed Private

供 bark-jie 自用的 Shadowrocket 模块。仓库保持私有。当前版本 1.0.0，2026-09-21。

采用 Maasea 原响应脚本的广告过滤算法，保留原模块的 `oad` 拦截；移除后台播放/画中画、翻译、导航/设置修改及播放密钥采集入口。不包含最新上游的第三方播放转发脚本。它不是完整最新版上游的等效替代；去广告效果、私库下载及自动刷新仍待 iPhone/iPad 实测。

## 首次安装

1. 在 GitHub 登录 bark-jie，创建 **Fine-grained personal access token**。Resource owner 选 bark-jie；Repository access 选 **Only select repositories → youtube-reviewed**；Repository permissions 仅 **Contents → Read-only**，Metadata 的必要只读权限保留。不要选择所有私库或写权限。
   - 创建入口：https://github.com/settings/personal-access-tokens/new?name=YouTube-ReadOnly&target_name=bark-jie&contents=read&expires_in=366
   - 默认示例为 366 天，届时需更换。若更重视减少维护，可自行选 No expiration（若账户允许）；泄露后将持续有效，直到撤销。令牌不要发给 Codex、不要放进仓库/下载网址或截图。
2. 从本次交付文件，或登录 GitHub 后下载本仓库的 `YouTube-Reviewed-Private.sgmodule`，导入 Shadowrocket 模块。首次导入私库不能依赖匿名链接，所以用本地文件。无需另装鉴权模块。
3. 在这个模块的「编辑参数」里填写 `GitHub只读令牌`。不要把令牌填在脚本参数、主配置正文或分享链接里。
4. 在小火箭中生成自己的 HTTPS 解密证书，安装到系统并在「证书信任设置」中开启完全信任；开启当前配置的 HTTPS 解密及此模块。不要使用别人提供的证书或私钥。全局路由使用「配置」。停用旧 YouTube 模块以免重复改写。
5. 连接小火箭后，在外部资源/脚本管理中手动刷新一次脚本。确认下载成功后再打开 YouTube。初次下载可能早于鉴权规则生效而失败，需要在连接后再次刷新；不同版本菜单名称可能不同。若仍显示 404/401，不要把失败当成安装成功，也不要改用带写权限的令牌。
6. 检查首页、普通视频、Shorts、搜索及 YouTube Music，确认能播放、广告减少。若卡顿或不能播放，先关闭本模块验证恢复。

## 后续更新

脚本来自本私库 `main/scripts/youtube.response.js`。模块设置 `script-update-interval=86400`（一天），实际刷新还受小火箭版本、缓存、联网与资源更新设置影响，并非保证每 24 小时必定执行。私库认证采用精确到本仓库的 Authorization 请求头规则；需要保持模块、证书和连接可用。此方法参考作者实际发布的私库助手，但尚未在你的手机验证。

首次本地导入的模块本身**不会因此自动追踪仓库里的模块文件**。日常兼容更新优先只更新同一脚本地址；若必须更改匹配范围、模块规则或证书范围，维护任务会通知你替换模块。不能承诺永远无需操作。

Codex 定时任务检查上游并审查差异，只有通过审查和测试的版本才发布到本仓库；发现第三方转发、账户/播放密钥外传、远程执行、不明混淆或无法核实的变化时保留旧版并通知。定时任务在本机运行，需要电脑开机且 Codex 可运行；不是 GitHub 云端全天候人工审计。客户端刷新与审查任务是两个独立环节。

## 权限与边界

- 解密主机为 `youtubei.googleapis.com`、`*.googlevideo.com`、`raw.githubusercontent.com`。raw 主机用于私库鉴权，实际解密范围是整个主机；只有本仓库 URL 匹配才注入令牌。不同模块也可能接触同一解密流量，应仅保留信任的模块。
- 令牌留在手机参数中；若开启小火箭 iCloud 同步，参数可能同步到你的 iCloud。丢失或分享配置时需撤销令牌。
- 发布的响应脚本不主动联网，只保留广告分类缓存。第三方工具函数虽仍在上游打包代码中，但当前入口没有调用网络函数。审查不是形式化安全证明，不能保证没有遗漏、上游账户不会被入侵、或广告永远可去除。
- 超过 4 MiB 的响应不交给脚本处理；解析异常时保留原响应。可能有漏广告，避免无限制处理大型响应。
- 本仓库只放代码和审查记录，不放代理订阅、节点、证书私钥、Cookie、令牌或个人观看数据。

## 停用与回退

关闭该模块可立即停止它的解密/改写规则。若彻底停用且没有其他用途，可关闭 HTTPS 解密并移除本机证书；GitHub 设置中撤销此只读令牌。回退脚本需把先前审核通过的内容以新提交恢复，不能强制改写历史。

## 来源与验证

- 上游：https://github.com/Maasea/sgmodule/tree/65075cdb388fc5e3094afd7e7314c67b243f3525
- 私库鉴权语法参考：https://github.com/LOWERTOP/Shadowrocket-First/blob/main/Private.module
- 令牌权限说明：https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
- 审查详情：`REVIEW.md`；版本哈希：`review-state.json`；测试：`test-results.json`。

许可 Apache-2.0，见 LICENSE 和 NOTICE。不是 YouTube、Google、Shadowrocket 或 Maasea 官方发行版。
