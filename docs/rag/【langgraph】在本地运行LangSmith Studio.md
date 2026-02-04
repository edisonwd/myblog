## 概述
在本地用 LangChain 构建代理时，**显示 agent 的流程和内部发生的情况**、实时交互并及时调试问题会很有帮助。LangSmith Studio 是一个免费的可视化界面，用于从本地机器开发和测试 LangChain agent。

Studio 可以连接本地运行的 agent，展示 agent 的每一步执行过程：发送给模型的提示、工具调用及其结果，以及最终输出。可以测试不同的输入，检查中间状态，并迭代 agent 的行为，而无需额外的代码或部署。

## 在本地运行langgraph
### 安装 langgraph-cli[inmem]
使用下面的命令安装

```shell
# Python >= 3.11 is required.
pip install --upgrade "langgraph-cli[inmem]"
```

### 准备 langgraph agent
如果已经有一个 langgraph agent ，可以直接使用它。

下面是一个包含 subgraph 子图的 **Agentic RAG **系统设计。

主要流程

1. **用户提问**
2. **意图识别与问题重写**
3. **进入 **`**RAG Agent**`** 主流程**
4. **调用子图：Generate Initial Answer（生成初始回答）**
5. **子图内部：**
    - **生成子问题**
    - **并行检索多个来源**
    - **聚合答案生成初步回复**
6. **推荐后续问题**
7. **输出最终结果**

用于演示构建 langgraph 图的代码实现如下：

```python
# backend/core/rag/state.py
from typing import Annotated, List, Dict, Optional
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import add_messages


class MainState:
    messages: Annotated[List[AnyMessage], add_messages]
    original_question: str
    rewritten_question: Optional[str]
    intent: str
    intermediate_answers: List[str]
    final_answer: str
    recommended_questions: List[str]


# nodes/generate_sub_questions.py
from langchain_core.prompts import PromptTemplate

_prompt = PromptTemplate.from_template(
    "请将以下问题分解为 2-3 个更具体的子问题：\n\n{question}"
)


async def generate_sub_questions(state: dict):
    question = state["rewritten_question"] or state["original_question"]
    sub_questions = []
    return {
        **state,
        "intermediate_answers": [],  # 清空中间答案
        "sub_questions": sub_questions
    }


async def retrieve_by_query(state: dict):
    pass


async def generate_final_answer(state: dict):
    pass


async def intent_recognition(state: dict):
    pass

async def start_agent_search(state: dict):
    pass

async def format_initial_query(state: dict):
    pass

async def recommend_questions(state: dict):
    pass

async def format_initial_answer(state: dict):
    pass

# backend/core/rag/agent/generate_initial_answer/graph_builder.py
from langgraph.graph import StateGraph, END


def build_generate_initial_answer_subgraph():
    graph = StateGraph(MainState)

    # 添加节点
    graph.add_node("generate_sub_questions", generate_sub_questions)
    graph.add_node("retrieve", retrieve_by_query)
    graph.add_node("generate_answer", generate_final_answer)

    # 设定边
    graph.set_entry_point("generate_sub_questions")
    graph.add_edge("generate_sub_questions", "retrieve")
    graph.add_edge("retrieve", "generate_answer")
    graph.add_edge("generate_answer", END)

    return graph


# backend/core/rag/agent/main/graph_builder.py
from langgraph.graph import StateGraph, START, END

def build_main_graph():
    workflow = StateGraph(MainState)

    # 普通节点
    workflow.add_node("intent_recognition", intent_recognition)
    workflow.add_node("start_agent_search", start_agent_search)
    workflow.add_node("format_initial_query", format_initial_query)
    workflow.add_node("recommend_questions", recommend_questions)
    workflow.add_node("format_initial_answer", format_initial_answer)

    # ✅ 嵌套子图（关键！）
    initial_answer_graph = build_generate_initial_answer_subgraph().compile(name="InitialAnswerSubgraph")
    workflow.add_node("generate_initial_answer_subgraph", initial_answer_graph)

    # 边连接
    workflow.add_edge(START, "intent_recognition")

    workflow.add_conditional_edges(
        "intent_recognition",
        lambda s: "continue" if s.get("intent") != "irrelevant" else "end",
        {
            "continue": "start_agent_search",
            "end": END
        }
    )

    workflow.add_edge("start_agent_search", "format_initial_query")
    workflow.add_edge("format_initial_query", "generate_initial_answer_subgraph")
    workflow.add_edge("generate_initial_answer_subgraph", "recommend_questions")
    workflow.add_edge("recommend_questions", "format_initial_answer")
    workflow.add_edge("format_initial_answer", END)

    return workflow


def studio_graph(config: RunnableConfig | None = None):
    """Studio entry point that reuses optional config overrides."""
    print(f' config: {config}')
    return build_main_graph()

```



如果需要实现上述流程项目结构建议如下：

```latex
backend/
├── core/
│   └── rag/
│       ├── agent/
│       │   ├── main/
│       │   │   └── graph_builder.py        # 主图
│       │   └── generate_initial_answer/
│       │       ├── graph_builder.py        # 子图
│       │       └── nodes/
│       │           ├── generate_sub_questions.py
│       │           ├── retrieve.py
│       │           └── generate_answer.py
│       ├── state.py                        # 共享状态
│       └── tools.py                        # 工具函数

```

### 创建 .env 文件设置环境变量
> **不要提交包含敏感信息的 .env 文件到 git 中**
>

如果你不想让数据被追踪到 LangSmith，可以在应用的 `.env `文件中设置 `LANGSMITH_TRACING=false`，关闭追踪后，本地服务器不会有数据流出。

```shell
# 禁止数据被追踪到 LangSmith
LANGSMITH_TRACING=false
```

### 创建 langgraph.json 配置文件
> 关于配置文件 JSON 对象中每个键的详细说明，请参阅[ LangGraph 配置文件说明](https://docs.langchain.com/langsmith/cli#python-4)。
>

LangGraph CLI 使用配置文件来定位你的agent并管理依赖关系。在你的应用目录中创建一个`langgraph.json`文件。`langgraph.json` 的基本配置如下：

```json
{
  "$schema": "https://langgra.ph/schema.json",
  "dependencies": ["."],
  "graphs": {
    "chat": "chat.graph:graph"
  }
  "env": ".env"
}
```

`langgraph.json` 的配置字段说明如下：

| **字段**       | **解释**                                                                                                                                                                                                                    |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `$schema`      | 指定该 JSON 文件遵循 LangSmith Studio 的 schema 规范，用于编辑器自动补全和校验。                                                                                                                                            |
| `dependencies` | 告诉 LangSmith 在启动时需要加载哪些代码依赖。   这里指定了 `["."]`，意味着系统会进入`langgraph.json`文件所在的当前目录寻找 `pyproject.toml`/ `setup.py`/ `requirements.txt`来安装或识别本地包结构，确保自定义模块可被导入。 |
| `graphs`       | 定义了多个可在 LangSmith Studio 中可视化和调试的“可执行图”（Graphs），每个键是一个图的 ID，值是其 Python 路径。                                                                                                             |
| `env`          | 指定环境变量文件路径 `.env`，LangSmith 会在运行时读取其中的内容（如 `LANGCHAIN_API_KEY`, `OPENAI_API_KEY` 等），用于连接模型和启用追踪。                                                                                    |




演示代码使用的 `langgraph.json`的配置如下：

```json
{
  "$schema": "https://langgra.ph/schema.json",
  "dependencies": ["./backend"],
  "graphs": {
    "agentic_rag": "./backend/core/rag/agent_search/main/test_graph.py:studio_graph"
  },
  "env": ".env"
}
```



### 启动 langsmith studio 
使用下面的命令启动开发服务器，将你的agent连接到Studio：

```shell
langgraph dev
```

服务器运行后，您的代理即可通过 API（`http://127.0.0.1:2024`）和 Studio UI（`https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024`）访问。

访问 langsmith studio  生成的实例代码的 agent 流程图如下：


当 Studio 与你的本地代理连接后，你可以快速迭代优化代理的行为。运行测试输入，检查完整的执行轨迹，包括提示词、工具参数、返回值以及令牌消耗和延迟等指标。当出现问题时，Studio 会捕获异常及其周围的上下文状态，帮助你理解问题发生的原因。

**开发服务器支持热重载**——当你在代码中修改提示词或工具签名时，Studio 会立即反映这些变更。你可以从任意步骤重新运行对话流程，以测试所做的修改，而无需从头开始。这一工作流可灵活扩展，适用于从简单的单工具代理到复杂的多节点图结构等各种场景。

## 问题记录
### 启动 langgraph dev 报错： No module named
**原因分析**：dependencies 路径不正确

+ **langgraph dev** 底层会启动一个 FastAPI 服务，并根据你的 langgraph.json 中的 `dependencies` 字段动态导入 Python 模块。这个过程依赖于 Python 的模块搜索路径（sys.path） 和 正确的项目结构与包声明。

解决方法：确保你在正确的目录下运行命令

+ 最可靠的方式是将你的本地包注册为“已安装包”，在 `backend/` 目录下创建 `pyproject.toml`
+ 如果你暂时不想改结构，可以用环境变量强制添加路径：

```shell
PYTHONPATH=$PYTHONPATH:./backend langgraph dev
```

### langsmith studio 的 graph 无法显示子图
**原因分析**：只有编译后的 graph 才能作为节点嵌入，在将 subgraph 编译时设置  `graph_builder().compile(name="InitialAnswerSubgraph", checkpointer=False)`其中 `compile` 方法中指定了 `checkpointer=False`表示子图不会使用和继承任何 checkpointer， 导致也无法显示子图

> 这里使用的 `langgraph==1.0.7`，无法显示子图的原因就在上面描述的这样，当去掉 checkpointer=False 或者设置为 checkpointer=True/None 都可以正常显示子图。具体原因还没详细研究。
>

**解决方法**：在编译子图的 `complie`方法中**去掉** `checkpointer=False` 或者**设置为**`checkpointer=True/None` 都可以正常显示子图。





参考文档

[https://docs.langchain.com/oss/python/langgraph/studio](https://docs.langchain.com/oss/python/langgraph/studio)

[https://docs.langchain.com/langsmith/cli#python-4](https://docs.langchain.com/langsmith/cli#python-4)

