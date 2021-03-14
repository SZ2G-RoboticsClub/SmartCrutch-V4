QQ机器人开发笔记(1) 背景知识

QQ如今是我们常用的通讯平台，本人近来在学习机器人开发时，发现不少内容都难以找到/过于专业化，于是写此笔记

**由于本人仍在学习当中，若有错误还请多多指教**

虽然QQ并没有像微信一样严格打击第三方客户端，却也与对机器人持包容开放的态度的Telegram不同，QQ并没有提供直接可用的程序接口。因此，若要想编写QQ机器人，需要一套相对复杂的程序组。

一般来说，一个QQ机器人主要由3个部分组成: **QQ协议端**、**机器人框架** 以及 **插件** (即我们机器人的功能组件)，这也是最重要的几个基础概念。

## 协议端

由于QQ官方并没有提供直接可用的程序接口，所以我们需要一个自己的接口

协议端 的作用是**模拟QQ客户端**与QQ服务器进行交流，**提供与QQ进行交流的API。**

其本质上就是一个与QQ服务器联络、把消息解码并为框架**提供API接口**的**伪造的QQ客户端**。 

因为需要及时适配QQ服务器的更新，协议端可能也需要频繁更新

目前常见的QQ 协议端有:

- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) (基于 [MiraiGo](https://github.com/Mrs4s/MiraiGo))
- [cqhttp-mirai-embedded](https://github.com/yyuueexxiinngg/cqhttp-mirai/tree/embedded)
- [Mirai](https://github.com/mamoe/mirai) + [cqhttp-mirai](https://github.com/yyuueexxiinngg/cqhttp-mirai)
- [Mirai](https://github.com/mamoe/mirai) + [Mirai Native](https://github.com/iTXTech/mirai-native) + [CQHTTP](https://github.com/richardchien/coolq-http-api)
- [OICQ-http-api](https://github.com/takayama-lily/onebot) (基于 [OICQ](https://github.com/takayama-lily/oicq))
- *酷Q (已停止开发)*

## 机器人框架

机器人框架 则是**调用这些API的包装**，便于我们在**不同的编程语言**中调用。

部分框架仅仅提供了一些基础的包装，如 [aiocqhttp](https://github.com/nonebot/aiocqhttp)，仅仅作为一个Python与协议端交互的SDK；而也有一些框架包装的十分顶层，如 [nonebot2](https://github.com/nonebot/nonebot2)，还提供了许多的基础逻辑处理功能

机器人框架一般会使用 WebSocket 或 HTTP 协议与QQ协议端通讯，其通讯内容一般都遵守特定的格式 —— [**Onebot标准**](https://github.com/howmanybots/onebot) (也叫「CQHTTP协议」) 。

也就是说，如果一个协议端支持Onebot标准，而一个框架也支持Onebot标准，那么它们互相就是"兼容"的。 

目前常见的、仍在活跃开发的支持Onebot标准的机器人框架有:

- [nonebot](https://github.com/nonebot/nonebot) (Python3)
- [nonebot2](https://github.com/nonebot/nonebot2) (Python3)
- [koishi](https://github.com/koishijs/koishi) (TypeScript)
- takayama-lily/[onebot](https://github.com/takayama-lily/onebot) (JavaScript)
- [zhamao-framework](https://github.com/zhamao-robot/zhamao-framework) (PHP)
- [OneBot-YaYa](https://github.com/Yiwen-Chan/OneBot-YaYa) (Go)
- [Sora](https://github.com/Yukari316/Sora) (C#)
- [...](https://github.com/topics/onebot)

我们当然也可以手动编写程序直接调用协议端，但并不建议。在笔记的第二章我们会尝试通过浏览器手动调用协议端用于测试其部署是否成功。

## 插件

而插件，即**功能组件**，是我们**真正需要编写的、为不同功能的机器人提供真正的 "功能"的程序**。

通常而言，插件是基于其对应的开发框架的，不同框架的插件不能混用，如 nonebot 的插件 不可在 nonebot2 中直接使用，更不可能接入 koishi (它们甚至不是同一种语言的代码)

因此，我们有一个插件ping，可让机器人接到命令/ping 时回复 pong!，整个机器人的运行过程应该是这样的：

1. 我们从客户端向QQ服务器发送信息/ping，QQ服务器将这条信息发送给机器人所使用的模拟客户端，即 **QQ协议端**
2. 协议端将消息解码后，将消息转为 OneBot标准 发送至 **机器人框架**
3. 机器人框架识别信息内容，发现这是一条命令，调用到**插件** ping 
4. ping 插件接到信息后，调用框架发送 pong! 
5. 框架将此回复发送给协议端
6. 协议端将命令发送给QQ服务器，最后我们得到这条回复

以上就是QQ机器人的**协议端**、**机器人框架** 和 **插件** 这三大基本概念。

在此后的笔记中，本人将会使用 **go-cqhttp** 为协议端、**nonebot** 为框架介绍机器人的开发。

你也可以来尝试一下笔者开发的机器人DeltaBot，欢迎提issues ~

DeltaBot: 一个基于NoneBot和go-cqhttp的QQ机器人github.com