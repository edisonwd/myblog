## 使用 brew 安装claude code
> 在 mac 中推荐使用 brew 安装 claude code，所以首先需要[安装 homebrew](https://github.com/Homebrew/brew/releases/)
>

1. 在 github 的 [Homebrew 仓库](https://github.com/Homebrew/brew)中下载对应的安装包：

<!-- 这是一张图片，ocr 内容为：ASSETS HOMEBREW.PKG 121 MB 5 DAYS AGO SHA256:C17D11B271F176... SOURCE CODE (ZIP) 5 DAYS AGO 5 DAYS AGO SOURCE CODE (TAR.GZ) RELEASE ATTESTATION (JSON) 5 DAYS AGO 15 PEOPLE REACTED 熊2 11 3 -->
![](https://cdn.nlark.com/yuque/0/2026/png/22104936/1773665218129-4ef1a37e-5402-48c3-b13b-b402e6274524.png)

下载完成后，双击安装即可

2. 使用 brew 安装 claude code

```shell
brew install --cask claude-code
```

**<font style="color:rgb(25, 27, 31);">Homebrew 不可用解决办法**

<font style="color:rgb(25, 27, 31);">（1）安装 Homebrew

```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

<font style="color:rgb(25, 27, 31);">（2）Homebrew 异常修复

```plain
brew update --force # 更新核心仓库
brew repair # 修复依赖/链接
brew cleanup # 清理缓存
brew doctor # 检查状态，输出Your system is ready to brew即为正常
```

<font style="color:rgb(25, 27, 31);">（3）解决网络问题，切换清华镜像

```plain
# 临时切换（仅当前终端生效）
export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"

# 永久切换（所有终端生效，zsh环境）
echo 'export HOMEBREW_BREW_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git"' >> ~/.zshrc
echo 'export HOMEBREW_CORE_GIT_REMOTE="https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git"' >> ~/.zshrc
# 使环境变量生效
source ~/.zshrc
# 重新更新
brew update
```

<font style="color:rgb(25, 27, 31);">修复后重新执行`<font style="color:rgb(25, 27, 31);background-color:rgb(248, 248, 250);">brew install --cask claude-code`<font style="color:rgb(25, 27, 31);">即可

## 配置 claude code
首次执行 `claude`命令，会报错如下`Failed to connect to api.anthropic.com: ERR_BAD_REQUEST`：

<!-- 这是一张图片，ocr 内容为：WELCOME CLAUDE CODE V2.1.77 TO 水 * 水 * * * UNABLE TO CONNECT TO ANTHROPIC SERVICES FAILED TO CONNECT TO API.ANTHROPIC.COM: ERR_BAD_REQUEST PLEASE CHECK YOUR INTERNET CONNECTION AND NETWORK SETTINGS. NOTE: CLAUDE CODE MIGHT NOT BE AVAILABLE IN YOUR COUNTRY. CHECK SUPPORTED COUNTRIES AT HTTPS://ANTHROPIC.COM/SUPPORTED-COUNTRIES -->
![](https://cdn.nlark.com/yuque/0/2026/png/22104936/1773752677655-a24f8872-7d72-43c2-aad4-84d73cbe78e7.png)

**原因分析**：

初次使用 claude code 时，会强制要求登录 Anthropic 账户，但是网络不通，无法访问 anthropic api 所以报错。

**解决方法**：

通过在 `~/.claude.json` 文件中添加如下配置绕过登录：

```json
{
  "hasCompletedOnboarding": true
}
```

> 参考文档：[https://bailian.console.aliyun.com/cn-beijing?tab=doc#/doc/?type=model&url=2949529](https://bailian.console.aliyun.com/cn-beijing?tab=doc#/doc/?type=model&url=2949529)
>

## 配置 claude code 使用阿里百炼模型
> 购买百炼模型：
>[云小站_专享特惠_云产品推荐-阿里云](https://www.aliyun.com/minisite/goods?userCode=aniq7u1s)

**在 `setting.json` 配置文件中永久设置**：在项目根目录或用户主目录（`~/.claude/settings.json`）创建 `settings.json` 文件，并写入模型配置信息，可分别进行项目级或用户级的永久配置。

使用 vim 写入配置：

```shell
vim ~/.claude/settings.json
```

写入 `settings.json` 文件的内容如下：

```json
{
  "env": {
    "ANTHROPIC_AUTH_TOKEN": "你的令牌",
    "ANTHROPIC_BASE_URL": "https://dashscope.aliyuncs.com/apps/anthropic",
    "ANTHROPIC_MODEL": "kimi-k2.5",
    "ANTHROPIC_DEFAULT_OPUS_MODEL": "qwen3.5-plus",
    "ANTHROPIC_DEFAULT_SONNET_MODEL": "qwen3.5-plus",
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": "qwen3-coder-next"
  },
  "includeCoAuthoredBy": false
}

```

> 参考文档：
>
> [查看或者创建阿里百炼模型 apikey](https://bailian.console.aliyun.com/cn-beijing?tab=model#/api-key)
>

可按任务复杂度配置不同级别的模型，Claude Code 会根据任务类型自动选择合适的模型，其中：

+ `ANTHROPIC_DEFAULT_OPUS_MODEL`：用于复杂推理、架构设计等高难度任务。
+ `ANTHROPIC_DEFAULT_SONNET_MODEL`：用于代码编写、功能实现等日常任务。
+ `ANTHROPIC_DEFAULT_HAIKU_MODEL`：用于语法检查、文件搜索等简单任务。



在`settings.json` 文件配置好模型以后，再次执行 `claude` 命令，输出如下：

<!-- 这是一张图片，ocr 内容为：CLAUDE CODE E V2.1.77  TIPS FOR GETTING STARTED RUN /INIT TO CREATE A CLAUDE.MD FILE WITH INSTRUCTIONS FOR CLAUDE WELCOME BACK! NOTE: YOU HAVE LAUNCHED CLAUDE IN YOUR HOME DIRECTORY. FOR THE BEST EXPERIENCE  RECENT ACTIVITY NO RECENT ACTIVITY  KIMI-K2.5 - API USAGE BILLING /USERS/EDISON 你是谁 2我是 CLAUDE CODE,ANTHROPIC的官方 CLI(命令行界面)工具.我是由 CLAUDE 驱动的交互式编程助手,可以帮助你完成各种软件开发任务,包括: 编写和修改代码 调试和修复BUG 重构和优化代码 运行命令和测试 探索和理解代码库 创建和管理文件 我支持多种编程语言,并且可以直接在你的终端中与你协作完成项目. 有什么我可以帮你的吗? FOR SHORTCUTS -->
![](https://cdn.nlark.com/yuque/0/2026/png/22104936/1773756008287-57ec9828-4b48-428a-ba04-59b669013587.png)

## 添加 docs-langchain mcp
1. 若使用Claude Code，可在终端执行下面指定命令，将MCP服务器添加至当前项目/工作目录（本地作用域）：

```shell
claude mcp add --transport http docs-langchain https://docs.langchain.com/mcp
```

2. 若想全局添加该MCP服务器，使其在所有项目中都能访问，只需在上述命令中增加`--scope user`参数，命令变为:

```shell
claude mcp add --transport http docs-langchain --scope user https://docs.langchain.com/mcp
```

+ 基础命令仅将MCP服务器关联到**当前项目**，作用域为本地。
+ 新增`--scope user`参数后，MCP服务器变为**全局生效**，所有项目均可访问。



在 claude 输入 `/mcp` 查看配置的 mcp 列表：

<!-- 这是一张图片，ocr 内容为：V2.1.77 CLAUDE CODE  TIPS FOR GETTING STARTED CLAUDE.MD FILE WITH INSTRUCTIONS FOR C1 RUN /INIT TO WELCOME BACK! CREATE NOTE: YOU HAVE LAUNCHED CLAUDE IN YOUR HOME DIRECTORY. FOR TH  RECENT ACTIVITY NO ACTIVITY RECENT KIMI-K2.5 - API USAGE BILLING /USERS/EDISON /MCP MANAGE MCP SERVERS 1 SERVER LOCAL MCPS (/USERS/EDISON/.CLAUDE.JSON [PROJECT: /USERS/EDISON])  DOCS-LANGCHAIN CONNECTED HTTPS://CODE.CLAUDE.COM/DOCS/EN/MCP FOR HELP 11 TO NAVIGATE ` ENTER TO CONFIRM ` ESC TO CANCEL -->
![](https://cdn.nlark.com/yuque/0/2026/png/22104936/1773756377618-7b6869e9-7764-45f1-b3f4-49e0a86c6c29.png)



## 添加 pua skills 技能
> 参考文档：[https://openpua.ai/](https://openpua.ai/)
>

**PUA SKILLS 介绍**：让你的 Codex / Claude Code 工作效率翻倍，产出翻倍。PUA 让 AI 不敢放弃，方法论让 AI 有能力不放弃，能动性鞭策让 AI 主动出击而不是被动等待。

使用下面的命令在 claude code 中安装 pua skills ：

```shell
claude plugin marketplace add tanweai/pua
claude plugin install pua@pua-skills
```





### 问题：Token 消耗太快了，如何节省 Token？
Claude Code 会扫描整个项目目录、读取相关代码文件并维护完整对话历史来提供编码建议，因而其 Token 消耗远高于普通对话场景。以下方法可帮助您有效控制消耗：

1. **减少无关文件**：为避免扫描不相关文件而造成 Token 消耗，建议在具体的项目目录中启动 Claude Code，同时仅保留必要的项目文件。
2. **总结对话**：Claude Code 会将历史对话内容作为上下文，当对话长度达到上下文窗口的 95% 时，Claude Code 会自动地总结对话内容。也可以通过执行`/compact`命令来手动地总结对话内容。
3. **精确指令**：模糊的请求会触发非必要的文件扫描，消耗更多的 Token。请在使用 Claude Code 时提出更明确、具体的问题或指令。
4. **分解任务**：在处理复杂任务时，可以将其分解为若干简单任务。
5. **重置上下文**：在开启一个全新的任务之前，使用`/clear`命令重置上下文，避免无关信息消耗 Token。

可以参考 [<font style="color:rgb(19, 102, 236);">Claude Code 官方文档](https://docs.anthropic.com/zh-CN/docs/claude-code/costs)了解更多节省 Token 的技巧。



参考文档

1. [https://github.com/anthropics/claude-code](https://github.com/anthropics/claude-code)
2. [https://brew.sh/](https://brew.sh/)
3. [https://docs.langchain.com/use-these-docs#connect-with-claude-code](https://docs.langchain.com/use-these-docs#connect-with-claude-code)

