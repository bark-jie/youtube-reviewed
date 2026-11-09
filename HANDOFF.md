# 交接：Shadowrocket 规则集（Sensitive / AI / Honor-of-Kings）

用中文和用户沟通。用户在 iPhone/iPad 上使用 Shadowrocket，不是程序员；给用户的操作步骤要把注意事项写进对应的那一步，不要集中放到最后。

## 现状
规则已经放在公开仓库 `bark-jie/youtube-reviewed` 的 `main` 分支（用户同意公开，并同意清空仓库原来的 YouTube 模块内容，旧内容只在 Git 历史里）。之前打算用私密 Gist，但云端会话的 GitHub 权限建不了 Gist，所以改用仓库。用户不想自己改文件，以后由 Claude 直接改仓库并推送。

- 配置链接（用户导入用）：`https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/Shadowrocket_RuleSet.conf`
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
