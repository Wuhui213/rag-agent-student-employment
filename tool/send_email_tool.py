from schema.emailSchema import EmailSchema  # 邮件配置
import smtplib  # smtp邮件发送服务
from email.mime.text import MIMEText  # 创建邮件内容
from dotenv import load_dotenv
import os
from langchain.tools import tool
from pydantic import BaseModel, Field


# 这里直接使用你自己定义的 EmailSchema，完全统一参数
@tool("send_email", args_schema=EmailSchema)
def send_email(to: str, subject: str, content: str) -> str:
    """
    发送邮件工具

    【参数说明】
    to: 收件人邮箱
    subject: 邮件主题
    content: 邮件内容

    【技术要点】
    1. 使用SMTP协议发送邮件
    2. QQ邮箱需要使用SSL连接（端口465）
    3. 需要使用授权码而非密码
    """
    load_dotenv()
    email_user = os.getenv("EMAIL_USER")
    email_password = os.getenv("EMAIL_PASSWORD")
    email_host = os.getenv("EMAIL_HOST")

    if not email_user or not email_password or not email_host:
        return "你的环境变量没有配置完整，请检查！"

    # 创建邮件消息对象
    msg = MIMEText(content, "plain", "utf-8")
    msg['Subject'] = subject
    msg['From'] = email_user
    msg['To'] = to

    try:
        # 使用SSL链接SMTP服务器
        with smtplib.SMTP_SSL(email_host, 465) as server:
            # 登录邮箱
            server.login(email_user, email_password)
            server.sendmail(email_user, to, msg.as_string())

            print("发送成功")
            return f"邮件发送成功"
    except Exception as e:
        print(f"发送失败")
        return f"发送失败:{str(e)}"
