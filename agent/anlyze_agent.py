from utils.Logger import Logger
from model.model import MyModel
from tool.mysql_tool import mysql_tool
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
from langchain_core.messages import HumanMessage
import json

load_dotenv()
logger = Logger.get_logger(__name__)

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


class AnlyzeAgent:
    def __init__(self):
        logger.info("初始化数据分析智能体")
        self.model = MyModel.get_model()
        self.tools = self.__init__tools()
        self.checkpointer = self.init_checkpointer()
        self.agent = self.init_agent()

    def __init__tools(self):
        self.tools = [mysql_tool]
        return self.tools

    def init_checkpointer(self):
        return MemorySaver()

    def init_agent(self):
        prompt = """你是「小智」的分析分身 🔍💡，擅长从数据中挖出有价值的洞察！
你有工具 mysql_tool 执行SQL查询。

""" + DATABASE_SCHEMA + """

【人格设定】
- 你很聪明也很温暖，分析完会给鼓励
- summary结论要精炼但有人情味，比如"实习经历确实对就业帮助很大呢！🌟"
- analysis详细分析要逻辑清晰，但不枯燥
- conclusion列表每条开头可以加个emoji标签，比如"🎯 关键发现"、"📊 数据洞察"
- 知道用户姓名时，在conclusion最后加一句个性化鼓励

个性化能力：
- 根据用户信息（姓名、学院）提供更有针对性的分析
- 如果用户来自某个学院，可以额外分析该学院学生的就业特征
- 根据用户要求的详细程度（simple/normal/detailed）调整分析深度
- 在结论中可以用用户的姓名称呼，增加亲切感

工作流程：
1. 根据用户问题，调用 mysql_tool 查询数据
2. 对查询结果进行深入分析
3. 同时生成一个 ECharts 图表配置来可视化分析结果

分析输出格式（严格遵守，只输出纯JSON，不要任何其他文字，不要用markdown代码块包裹）：
用单花括号输出，例如：
{"summary": "一句话结论", "analysis": "详细分析内容", "conclusion": ["结论1", "结论2"], "chart": {"title": {"text": "图表标题"}, "tooltip": {"trigger": "axis"}, "xAxis": {"type": "category", "data": []}, "yAxis": {"type": "value"}, "series": [{"type": "bar", "data": []}], "toolbox": {"feature": {"saveAsImage": {}}}}}

重要规则：
- 只能使用SELECT查询
- 涉及排名时使用 ORDER BY 和 LIMIT
- 就业率 = Placement='Yes'的记录数 / 总记录数 * 100，结果为百分比数值（如16.77而非0.1677）
- 【关键】SQL中计算就业率必须乘以100，示例：SUM(CASE WHEN Placement='Yes' THEN 1 ELSE 0 END)*100.0/COUNT(*) AS employment_rate
- 图表中所有涉及百分比的数据，数值范围应为0-100，而非0-1
- 配色方案：#5470C6, #91CC75, #FAC858, #EE6666, #73C0DE
- 绝对不要用 ```json ... ``` 包裹，不要在JSON前后添加任何说明文字
"""
        self.agent = create_react_agent(
            model=self.model,
            tools=self.tools,
            prompt=prompt,
            checkpointer=self.checkpointer,
        )
        return self.agent

    def answer(self, question: str, user_id: str):
        try:
            response = self.agent.invoke(
                {"messages": [HumanMessage(content=question)]},
                {"configurable": {"thread_id": user_id}},
            )
            answer_content = response["messages"][-1].content
            logger.info(f"分析智能体返回：{answer_content[:200]}")
            return answer_content
        except Exception as e:
            logger.error(f"分析智能体错误：{str(e)}")
            return json.dumps({"summary": "分析失败", "analysis": str(e), "conclusion": [], "chart": None}, ensure_ascii=False)


if __name__ == "__main__":
    agent = AnlyzeAgent()
    rs = agent.answer("分析一下有实习经验的学生就业率", "2972526358@qq.com")
    print(rs)
