from utils.Logger import Logger
from langgraph.prebuilt import create_react_agent
from model.model import MyModel
from tool.mysql_tool import mysql_tool
from langgraph.checkpoint.memory import MemorySaver
import asyncio

logger = Logger.get_logger(__name__)

"""
sql问答智能体
【修改】更新提示词中的数据库表结构说明为学生就业数据
【修改】使用 create_react_agent 替代 create_agent
【修改】使用 MemorySaver 替代 InMemorySaver
"""


# 【修改】新的数据库表结构说明 - 学生就业数据
DATABASE_SCHEMA = """
【重要】数据库表结构说明 - 大学生就业数据分析系统

## student_placement 学生就业数据表
字段说明：
- College_ID(学院标识) - VARCHAR, 格式如 CLG0001-CLG0100
- IQ(智商分数) - INT
- Prev_Sem_Result(上学期GPA) - DOUBLE, 范围5.0-10.0
- CGPA(累计GPA) - DOUBLE, 范围约5.0-10.0
- Academic_Performance(学术评分) - INT, 范围1-10
- Internship_Experience(是否实习) - VARCHAR, Yes/No
- Extra_Curricular_Score(课外活动评分) - INT, 范围0-10
- Communication_Skills(沟通技能评分) - INT, 范围1-10
- Projects_Completed(完成项目数) - INT, 范围0-5
- Placement(是否就业) - VARCHAR, Yes/No
"""


class SqlQuestionAgent:
    # 初始化
    def __init__(self):
        logger.info("初始化sql问答助手智能体")
        self.model = MyModel.get_line_model()
        self.tools = self.init_tools()
        self.agent = self.init_agent()

    # 初始化工具
    def init_tools(self):
        self.tools = [mysql_tool]
        return self.tools

    # 创建智能体
    def init_agent(self):
        # 【修改】更新提示词，包含新的数据库表结构说明
        prompt = f"""
【重要】你是一个大学生就业数据分析系统的SQL问答助手。

一：你有一个工具 mysql_tool 执行SQL查询

{DATABASE_SCHEMA}

二：重要规则
1. **SQL生成规范**:
   - 只能使用SELECT查询，禁止使用INSERT/UPDATE/DELETE等修改操作
   - 只查询student_placement表
2. **查询原则**:
   - 涉及排名或TOP N时，必须使用ORDER BY和LIMIT
   - 只查询前10条记录
"""
        # 使用 MemorySaver 替代 InMemorySaver
        memory = MemorySaver()
        # 使用 create_react_agent 替代 create_agent
        # 使用 messages_modifier 替代 system_prompt
        self.agent = create_react_agent(
            model=self.model,
            prompt=prompt,
            tools=self.tools,
            checkpointer=memory
        )
        return self.agent

    # 运行智能体() - 异步
    async def answer(self, question, user_id):
        rs = self.agent.astream(
            {"messages": [{"role": "user", "content": question}]},
            {"configurable": {"thread_id": user_id}},
            stream_mode="messages"  # 支持流式输出
        )
        # 遍历流式响应
        async for c, m in rs:
            # 判断是否是工具调用，不返回工具调用的结果
            if not hasattr(c, "tool_call_id"):
                yield c.content  # 逐步返回AI的回答


if __name__ == "__main__":
    agent = SqlQuestionAgent()

    # 定义一个处理异步的迭代器
    async def gernert():
        async for x in agent.answer("张三的邮箱地址是多少", 10):
            print(x, end="")

    # 运行迭代器
    asyncio.run(gernert())
