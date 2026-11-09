# Shadowrocket 规则集与 YouTube 模块

三个手动选择的代理分组：Sensitive（敏感信息）、AI、Honor-of-Kings（王者荣耀国际服），其余沿用原版 default 规则。

配置导入链接（Shadowrocket → 配置 → 右上角 + → 粘贴 → 下载）：

```
https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/Shadowrocket_RuleSet.conf
```

无分组版（同样的规则，所有走代理的连接都用主页选中的那个节点）：

```
https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/Shadowrocket_RuleSet_NoGroup.conf
```

规则改动只改 `ruleset/` 里的文件，手机上到「配置 → 规则集 URL」点更新即可，不要点「更新配置」。维护说明见 [HANDOFF.md](HANDOFF.md)。

## YouTube 去广告模块

本地运行、固定版本的 YouTube 去广告模块（基于 Maasea 的脚本，不连作者服务器）。Shadowrocket → 配置 → 模块 → 右上角 + → 粘贴：

```
https://raw.githubusercontent.com/bark-jie/youtube-reviewed/main/youtube/YouTube-Enhance.sgmodule
```
