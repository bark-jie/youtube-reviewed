# 交接：Shadowrocket 规则集（Sensitive / AI / Honor-of-Kings）

用中文和用户沟通。用户在 iPhone/iPad 上使用 Shadowrocket，不是程序员；给用户的操作步骤要把注意事项写进对应的那一步，不要集中放到最后。

## 现状
规则已经放在公开仓库 `bark-jie/youtube-reviewed` 的 `main` 分支（用户同意公开，并同意清空仓库原来的 YouTube 模块内容，旧内容只在 Git 历史里）。之前打算用私密 Gist，但云端会话的 GitHub 权限建不了 Gist，所以改用仓库。用户不想自己改文件，以后由 Claude 直接改仓库并推送。

- 配置链接（用户导入用）：`https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/Shadowrocket_RuleSet.conf`
- 无分组版配置链接：`https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/Shadowrocket_RuleSet_NoGroup.conf`
- 规则集链接：`https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/ruleset/<文件名>`
- 网址里用分支名 `main`，不要用 commit hash，否则改了文件后 Shadowrocket 拉到的还是旧版本。

## 文件
| 路径 | 说明 |
|---|---|
| `ruleset/Sensitive.list` | 敏感信息组规则（126 条） |
| `ruleset/AI.list` | AI 组规则（151 条） |
| `ruleset/HonorOfKings.list` | 王者荣耀国际服组规则（60 条） |
| `template/Shadowrocket_RuleSet.conf` | 配置模板，三行 `RULE-SET` 的网址里有占位符 `https://gist.githubusercontent.com/USERNAME/GIST_ID/raw`（占位符原样保留，脚本靠它定位） |
| `Shadowrocket_RuleSet.conf` | 由脚本生成的已填网址的配置，用户导入的就是它。不要手改，改模板后重新生成 |
| `Shadowrocket_RuleSet_NoGroup.conf` | 无分组版，也由脚本生成：同样的规则，去掉 `[Proxy Group]`，自定义规则全部改成 `PROXY`，也就是走主页选中的节点。用户要求保留这个版本，两个版本共用 `ruleset/` 里的规则集 |
| `ruleset/clash/*.yaml`、`stash/RuleSet.stoverride`、`clash-party/RuleSet.override.yaml` | 给 Stash / Clash Party 用的规则集副本和覆写，由脚本生成，见下面「Stash / Clash Party 分流覆写」 |
| `backup/Shadowrocket_Sensitive_AI_HoK.conf` | 同样规则全部写在配置里的完整版（备用，也是校验基准） |
| `tools/fill_and_verify.py` | 填网址并校验：检查列表格式、规则与备用版一致；加 `--online` 时逐个下载 raw 地址并和本地文件比对。不带网址参数时默认用本仓库 main 分支的 `ruleset/` |

## 每次改动的流程
1. 改 `ruleset/` 里的 `.list` 文件（只有改配置结构时才动 `template/`）。
2. 运行 `python3 tools/fill_and_verify.py`，格式检查必须全部是 `[OK]`、exit 0。
3. 提交并推送到 `main`（用户已允许直接推 main，不必走 PR）。如果会话指定了别的工作分支，先推到工作分支，再快进合并到 `main`。
4. 运行 `python3 tools/fill_and_verify.py --online`，三项都要 `[OK]`。GitHub raw 有约 5 分钟缓存，失败就等几分钟再跑。
5. 提醒用户去「规则集 URL」里更新。

## 用户在手机上要做的（交付时原样转述）
1. **导入配置。** Shadowrocket → 配置 → 右上角 + → 粘贴配置链接 `https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/Shadowrocket_RuleSet.conf` → 下载 → 点这个配置并选「使用配置」。这一步之后，旧配置里的证书就不在了。
2. **重装证书（最后一次）。** 在新配置里打开「HTTPS 解密」，生成新的 CA 证书 → 安装证书 → 到 iOS 设置 → 通用 → 关于本机 → 证书信任设置，打开对它的完全信任。漏了最后这个开关，解密不会生效。
3. **选节点。** 配置 → 代理分组，三个组分别在「服务器节点」里选机场，再在「策略」里勾选节点。HoK 组要选支持 UDP 的节点，最好是香港的 TUIC 或 Hysteria2 节点，否则开局可能掉线。
4. **确认规则集已加载。** 配置 → 规则集 URL，三个规则集都应该显示规则数量（约 126 / 151 / 60）。显示 0 的话，在 Shadowrocket 开着的状态下点一次更新。
5. **以后只更新规则集，不要「更新配置」。** 更新配置会用仓库里的版本覆盖掉本地配置，证书设置也会跟着丢。

## 以后维护规则（给以后的 Claude）
- **只改 `ruleset/` 里的 `.list` 文件**，按上面「每次改动的流程」推送到 `main`，配置不用动。改完提醒用户去「规则集 URL」里更新。
- **列表文件格式：** 每行写成 `类型,值`，**不要写策略名**，策略由配置里的 `RULE-SET` 行决定。IP 类规则（`IP-CIDR`、`IP-ASN`）**必须带 `,no-resolve`**，否则所有请求都会先做一次 DNS 解析。列表里只用 `DOMAIN`、`DOMAIN-SUFFIX`、`DOMAIN-KEYWORD`、`IP-CIDR`、`IP-ASN` 这几种。
- **`DOMAIN-WILDCARD`、`DEST-PORT`、`AND` 这几类规则只写在配置里**（目前只有 3 条，都属于 HoK）。不确定 Shadowrocket 的规则集文件是否支持它们。
- **配置里 `# ==================== Original default rules` 以下是用户原版 default，一字不改。** 所有新规则都靠放在它前面来覆盖原规则。配置里不写 MITM 段。
- 每次改完都跑一次 `tools/fill_and_verify.py`。规则改动以后，和备用版不一致属于正常，会显示 `[INFO]`；格式检查必须全部是 `[OK]`。

### 已经和用户确定的决定
- **三个组都是 `select` 手动选择**，在「服务器节点」里选机场，再选节点，不加正则筛选。
- **AI 组**：只放 AI 服务本身，加上需要和 AI 节点用同一个 IP 的主机，也就是登录、人机验证、付款、功能开关这类。具体包括：
  - OpenAI、Anthropic、Gemini 官方允许清单里的这类主机，Perplexity、Grok、Copilot、GitHub Copilot、Cursor、JetBrains AI、Groq、Together、Azure AI、Meta AI、Mistral、Poe，以及 Apple Intelligence relay。
  - 用户要求额外放进来的：Intercom、Datadog、Sanity、Fathom、SendGrid。
  - 用户明确要求**不放**的：`www.google.com`、GitHub、npm、brew、`storage.googleapis.com`、JS 库 CDN、YouTube/字体/地图等普通 Google 服务。这些继续走原规则的 PROXY。
- **HoK 组**：包含 `IP-ASN,132203` 和 `IP-ASN,139341`（腾讯的两个海外网络，对局服务器每局 IP 都不同），这会覆盖 default 里的 `IP-ASN,132203,DIRECT`。用户用的是大陆版微信，日志确认微信没有受影响。用户明确要求**不放** Facebook、Google、Firebase 的 SDK 地址。
- **Sensitive 组**：旧配置的新闻和人权类站点，加上网页存档、翻墙工具官网、Proton、Signal。

### 分析用户发来的 Shadowrocket 日志（.db）
日志是 SQLite 数据库（FTS3），表 `logging_content` 的列是 `c0url`（目标主机:端口）、`c1ua`、`c2result`（命中的规则，后面跟 `# 节点名`）、`c3type`（PROXY/DIRECT）、`c4created`（时间）。查询：`select c0url,c1ua,c2result,c3type,c4created from logging_content order by docid`。如果导出的文件只有 4KB、里面没有表，说明是在记录还没结束时导出的，请用户停止记录后重新导出。分析方法：先找出没命中目标组的连接，再按时间和 HoK 的连接对照，判断它是不是游戏发起的。

## Stash / Clash Party 分流覆写（`stash/`、`clash-party/`）
用户在 Stash（iPhone）和 Clash Party（Windows）里用的是**机场的托管订阅配置**（第一行 `#SUBSCRIBED`，Stash 每 12 小时整份替换）。所以分组和规则**只能做成覆写**，绝不能改机场配置本身。

- Stash 覆写：`https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/stash/RuleSet.stoverride`
- Clash Party 覆写：`clash-party/RuleSet.override.yaml`（模板，用户在本地副本里填订阅链接）
- 两个文件和 `ruleset/clash/*.yaml` 都由 `tools/fill_and_verify.py` 生成，**不要手改**。规则只改 `ruleset/*.list`，再跑脚本。
- 结构（用户已确认）：
  - 机场作为 proxy-provider 引入（目前 SinX、G94cloud，在脚本的 `AIRPORTS` 里加减）。
  - 三个组 Sensitive / AI / Honor-of-Kings，每个组先选「组名-机场」小组，再在小组里选该机场的节点。组和组之间互不影响。不加正则筛选，不写死节点名。
  - 我们的规则用前插的方式放在机场规则前面；没命中的流量交给机场原配置的规则（用户同意，所以 Stash 和 Shadowrocket 的其他分流不完全一致）。
- **订阅链接是机密，绝不能进仓库。** Stash 用覆写参数（`arguments`），值只存在手机上，覆写远程更新时会保留。Clash Party 的 YAML 覆写没有参数功能，用户自己在本地副本里把 `PASTE_..._HERE` 换成链接。
- 订阅链接为空或失效时，对应小组没有节点，会被当成直连（Stash 文档写明，mihomo 同理）。所以参数设为必填；某个机场暂时没有链接时，先填另一个机场的链接。
- 自动延迟测试已按用户要求关闭：Stash 的 9 个组都是 `interval: -1`，Clash Party 两个订阅的 `health-check.enable: false`。组都是手动选择，测速不会切换节点，只影响 App 里显示的延迟数字；用户需要时在 App 里手动测。
- `ruleset/clash/*.yaml` 是 `.list` 去掉注释后的 classical YAML 副本，因为不确定 Stash 的 text 格式是否接受 `#` 注释行。
- Shadowrocket 的 `DEST-PORT` 在 Stash/mihomo 里写作 `DST-PORT`；脚本会检查 `INLINE` 和模板里的 inline 规则保持一致。
- 2026-11 用户发来的 SinX 配置里，SinX 自带：`ads` 拦截、按服务分组（Claude/ChatGPT/Google 等）、`.mrs` 规则集。我们的规则在它们前面，不冲突。用户的机场配置里有订阅 token 和节点密码，**不要存进仓库，也不要转述**。

## YouTube 去广告模块（`youtube/`）
用户选了「本地运行、固定版本」的方案：模块是用户截图里的旧版 Maasea「Youtube (Music) Enhance」，唯一改动是 `script-path` 指向本仓库的 `youtube/youtube.response.js`（Maasea 原文件的原样副本，Apache 2.0，见 `youtube/NOTICE`）。

- 模块导入链接：`https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/youtube/YouTube-Enhance.sgmodule`
- Stash 覆写链接：`https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/youtube/YouTube-Enhance.stoverride`（和 sgmodule 同样的规则和脚本，`script-providers` 指向本仓库同一份 `youtube.response.js`，所以采用新脚本时两边同时更新。改 sgmodule 的匹配规则时，要同步改 stoverride。Stash 没有参数界面，参数直接写死在 `argument` 里。写法参照 Script-Hub 转换出的 Stash 覆写，因为 stash.wiki 在云端会话里访问不了，没有对照官方文档；`PROTOCOL,UDP` 规则如果 Stash 报错，可以改成 `NETWORK,UDP` 试试）
- **绝不引入作者的 `youtube.request.js`，也不要用作者新版模块的写法。** 新版会把视频加载请求连同解密密钥转发到作者的 Cloudflare Worker（`init-stream.maasea.workers.dev`），按 YouTube 的设计，里面很可能带账号登录凭证。用户明确不接受。
- `youtube.response.js` 本身目前没有任何外发网络请求，`fetch` 只是工具函数的定义，没有被调用。它会把一些密钥存到手机本地（persistentStore），但不会发出去。
- 「歌词翻译语言」参数在新脚本里已经不起作用，保留只是为了和用户原版一致。

### 每周检查作者更新
1. 运行 `python3 youtube/check_update.py <临时目录>`，看第一行 `STATUS`：
   - `NO_CHANGE`：没有更新，什么都不用做，也不用通知用户。
   - `TOO_NEW`：作者改了，但改动还不满 `min_age_days`（3 天），下次再看。用于防范作者账号被盗后推送的恶意版本。
   - `NEEDS_REVIEW`：扫描发现新增风险项（网络请求、新域名、eval、重定向等）。要人工看新旧脚本的差异，并搞清楚每个新增项的用途。只要有一项会把数据发到 YouTube/Google 以外的地方，就**不采用**，并告诉用户原因。
   - `CANDIDATE_OK`：没有新增风险项，但仍要看一眼报告里的提交说明和差异。
2. 确认没问题后，运行 `python3 youtube/check_update.py <临时目录> --adopt`（扫描标记过的版本，人工确认后可以手动复制，并更新 `state.json`）。然后提交并推送到 `main`，再提醒用户：Shadowrocket → 配置 → 模块，在这个模块上左滑点「更新」（或者下拉刷新），这样新脚本才会生效。如果用户也在用 Stash，一并提醒：Stash → 覆写，更新这个覆写（脚本本身也会每天自动拉取一次）。
3. 同时检查作者的 `YouTube.Enhance.sgmodule` 里匹配规则有没有变化，有用的改动（比如新的广告接口）可以手动合并进本仓库的模块，但不要合并 `youtube.request.js` 相关的部分。
