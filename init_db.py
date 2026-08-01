"""
数据库初始化脚本
用于创建 MySQL 数据库表结构

【功能】
1. 创建 users 表（登录验证用）
2. 创建 student_placement 表（大学生就业数据）
3. 创建 chat_history 表（聊天记录持久化）
4. 创建 user_preferences 表（用户偏好设置）
5. 插入测试用户数据到 users 表

【使用】
python init_db.py
"""

import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def init_database():
    """初始化数据库表结构"""
    
    # 连接MySQL数据库
    con = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        charset='utf8mb4'
    )
    
    cursor = con.cursor()
    database_name = os.getenv("MYSQL_DATABASE")
    
    try:
        # 创建数据库（如果不存在）
        print(f"创建数据库 {database_name}（如果不存在）...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        cursor.execute(f"USE `{database_name}`")
        print(f"✓ 数据库 {database_name} 就绪")
        
        # ============================================
        # 1. 创建 users 表（登录验证用）
        # ============================================
        print("\n创建 users 表（用户表）...")
        users_table_sql = """
        CREATE TABLE IF NOT EXISTS `users` (
            `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
            `name` VARCHAR(50) NOT NULL COMMENT '用户姓名',
            `email` VARCHAR(100) NOT NULL UNIQUE COMMENT '用户邮箱',
            `phone` VARCHAR(20) DEFAULT NULL COMMENT '用户电话',
            `department` VARCHAR(50) DEFAULT NULL COMMENT '部门',
            `avatar` VARCHAR(255) DEFAULT NULL COMMENT '头像URL',
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            `last_login` TIMESTAMP NULL DEFAULT NULL COMMENT '最后登录时间',
            INDEX `idx_email` (`email`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
        """
        cursor.execute(users_table_sql)
        print("✓ users 表创建成功")
        
        # ============================================
        # 2. 创建 student_placement 表（大学生就业数据）
        # ============================================
        print("\n创建 student_placement 表（大学生就业数据表）...")
        student_table_sql = """
        CREATE TABLE IF NOT EXISTS `student_placement` (
            `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
            `College_ID` VARCHAR(20) NOT NULL COMMENT '学院标识，如CLG0001-CLG0100',
            `IQ` INT COMMENT '智商分数',
            `Prev_Sem_Result` DOUBLE COMMENT '上学期GPA，范围5.0-10.0',
            `CGPA` DOUBLE COMMENT '累计GPA，范围约5.0-10.0',
            `Academic_Performance` INT COMMENT '学术评分，范围1-10',
            `Internship_Experience` VARCHAR(10) COMMENT '是否实习，Yes/No',
            `Extra_Curricular_Score` INT COMMENT '课外活动评分，范围0-10',
            `Communication_Skills` INT COMMENT '沟通技能评分，范围1-10',
            `Projects_Completed` INT COMMENT '完成项目数，范围0-5',
            `Placement` VARCHAR(10) COMMENT '是否就业，Yes/No',
            INDEX `idx_college_id` (`College_ID`),
            INDEX `idx_placement` (`Placement`),
            INDEX `idx_internship` (`Internship_Experience`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大学生就业数据表';
        """
        cursor.execute(student_table_sql)
        print("✓ student_placement 表创建成功")
        
        # ============================================
        # 3. 创建 chat_history 表（聊天记录持久化）
        # ============================================
        print("\n创建 chat_history 表（聊天记录表）...")
        chat_history_sql = """
        CREATE TABLE IF NOT EXISTS `chat_history` (
            `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
            `user_email` VARCHAR(100) NOT NULL COMMENT '用户邮箱',
            `session_id` VARCHAR(50) NOT NULL COMMENT '会话ID',
            `role` VARCHAR(10) NOT NULL COMMENT '角色: user/ai',
            `content` TEXT COMMENT '消息内容',
            `chart_option` JSON DEFAULT NULL COMMENT 'ECharts图表配置(JSON)',
            `msg_type` VARCHAR(20) DEFAULT 'text' COMMENT '消息类型: text/chart/analysis',
            `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            INDEX `idx_user_email` (`user_email`),
            INDEX `idx_session_id` (`session_id`),
            INDEX `idx_created_at` (`created_at`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='聊天记录表';
        """
        cursor.execute(chat_history_sql)
        print("✓ chat_history 表创建成功")
        
        # ============================================
        # 4. 创建 user_preferences 表（用户偏好设置）
        # ============================================
        print("\n创建 user_preferences 表（用户偏好表）...")
        user_preferences_sql = """
        CREATE TABLE IF NOT EXISTS `user_preferences` (
            `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT '偏好ID',
            `user_email` VARCHAR(100) NOT NULL UNIQUE COMMENT '用户邮箱',
            `detail_level` VARCHAR(10) DEFAULT 'normal' COMMENT '回答详细程度: simple/normal/detailed',
            `default_chart_type` VARCHAR(20) DEFAULT 'bar' COMMENT '默认图表类型: bar/line/pie/scatter',
            `theme` VARCHAR(10) DEFAULT 'light' COMMENT '界面主题: light/dark',
            `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX `idx_user_email` (`user_email`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户偏好设置表';
        """
        cursor.execute(user_preferences_sql)
        print("✓ user_preferences 表创建成功")
        
        # ============================================
        # 5. 插入测试用户数据
        # ============================================
        print("\n插入测试用户数据...")
        test_users = [
            ('杨小雨', '3493985772@qq.com', '13800138001', '人工智能与大数据学院'),
            ('张三', 'zhangsan@example.com', '13800138002', '计算机科学学院'),
            ('李四', 'lisi@example.com', '13800138003', '经济管理学院'),
            ('王五', 'wangwu@example.com', '13800138004', '电子信息学院'),
        ]
        
        for name, email, phone, department in test_users:
            try:
                cursor.execute(
                    "INSERT IGNORE INTO `users` (`name`, `email`, `phone`, `department`) VALUES (%s, %s, %s, %s)",
                    (name, email, phone, department)
                )
            except Exception as e:
                print(f"  插入用户 {name} 失败: {e}")
        
        print("✓ 测试用户数据插入完成")
        
        # 提交事务
        con.commit()
        print("\n" + "="*50)
        print("✅ 数据库初始化完成！")
        print(f"  - users 表（用户表）")
        print(f"  - student_placement 表（就业数据表）")
        print(f"  - chat_history 表（聊天记录表）")
        print(f"  - user_preferences 表（用户偏好表）")
        print("="*50)
        
    except Exception as e:
        con.rollback()
        print(f"\n❌ 数据库初始化失败: {e}")
        raise
    finally:
        cursor.close()
        con.close()


if __name__ == "__main__":
    init_database()
