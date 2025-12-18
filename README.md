# astrbot_plugin_psychological

心理委员插件 - 为群成员提供随机3次元美女图片

## 功能说明

这是一个 AstrBot 插件，当群成员输入 `/心理委员` 时，会随机回复一句温馨的提示语，然后从多个 API 中随机选择一个获取并发送一张图片。

## 使用方法

在群聊或私聊中输入以下命令：

```
/心理委员
```

插件会：
1. 随机回复一条提示语（如"稍等一下哦"、"希望这能让你心情好一点"等）
2. 从多个图片 API 中随机选择一个
3. 获取并发送图片

## 特性

- 🎲 随机选择提示语，增加互动趣味性
- 🖼️ 支持多个图片 API，随机调用提高可用性
- ⚡ 异步处理，响应快速
- 🛡️ 完善的错误处理机制

## 安装

1. 将插件目录放置到 `AstrBot/data/plugins/` 目录下
2. 在 AstrBot WebUI 的插件管理页面启用插件
3. 使用 `/心理委员` 命令即可

## 依赖

本插件使用 AstrBot 内置的 `aiohttp` 库，无需额外安装依赖。

## 使用的api

1. https://v2.xxapi.cn/api/
2. https://api.lolimi.cn/API/
3. https://api.xk.ee/cosplay

## 支持

- [AstrBot 官方文档](https://docs.astrbot.app)
- [AstrBot 开发者 QQ 群](https://jq.qq.com/?_wv=1027&k=975206796)

## 版本

当前版本：v1.0.0


