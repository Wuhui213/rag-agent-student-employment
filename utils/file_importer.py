"""
文件导入工具
支持 CSV 和 Excel 文件导入到 MySQL 数据库
"""

import os
import pandas as pd
import pymysql
from dotenv import load_dotenv
from utils.Logger import Logger

# 加载环境变量
load_dotenv()

logger = Logger.get_logger(__name__)

# student_placement 表的列名
STUDENT_PLACEMENT_COLUMNS = [
    'id',
    'College_ID',
    'IQ',
    'Prev_Sem_Result',
    'CGPA',
    'Academic_Performance',
    'Internship_Experience',
    'Extra_Curricular_Score',
    'Communication_Skills',
    'Projects_Completed',
    'Placement'
]


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        charset='utf8mb4'
    )


def import_file_to_db(file_path: str, filename: str) -> dict:
    """
    将 CSV/Excel 文件导入到 student_placement 表
    
    Args:
        file_path: 文件完整路径
        filename: 文件名
        
    Returns:
        {"success": True, "rows": 数量} 或 {"success": False, "error": "错误信息"}
    """
    try:
        # 获取文件扩展名
        file_ext = os.path.splitext(filename)[1].lower()
        
        if file_ext == '.csv':
            # 读取 CSV 文件
            df = pd.read_csv(file_path, encoding='utf-8')
        elif file_ext in ['.xlsx', '.xls']:
            # 读取 Excel 文件
            df = pd.read_excel(file_path, engine='openpyxl' if file_ext == '.xlsx' else 'xlrd')
        else:
            return {"success": False, "error": f"不支持的文件格式: {file_ext}"}
        
        # 检查是否为空文件
        if df.empty:
            return {"success": False, "error": "文件为空"}
        
        # 标准化列名（去除空格，转为小写）
        df.columns = df.columns.str.strip().str.lower()
        
        # 尝试映射列名
        column_mapping = {
            'college_id': 'College_ID',
            'id': 'id',
            'iq': 'IQ',
            'prev_sem_result': 'Prev_Sem_Result',
            'prev_semester_result': 'Prev_Sem_Result',
            'cgpa': 'CGPA',
            'academic_performance': 'Academic_Performance',
            'internship_experience': 'Internship_Experience',
            'extra_curricular_score': 'Extra_Curricular_Score',
            'communication_skills': 'Communication_Skills',
            'projects_completed': 'Projects_Completed',
            'placement': 'Placement'
        }
        
        # 重命名列
        df = df.rename(columns=column_mapping)
        
        # 检查必需列
        required_cols = ['College_ID', 'IQ', 'Prev_Sem_Result', 'CGPA']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return {
                "success": False, 
                "error": f"文件缺少必需列: {', '.join(missing_cols)}。请确保文件包含以下列: College_ID, IQ, Prev_Sem_Result, CGPA"
            }
        
        # 处理 id 列：如果没有 id 列或者全是空值，则不插入 id，让数据库自动生成
        if 'id' not in df.columns or df['id'].isna().all():
            df = df.drop(columns=['id'], errors='ignore')
        else:
            df['id'] = df['id'].astype(int)
        
        # 确保数值列类型正确
        numeric_columns = ['IQ', 'Prev_Sem_Result', 'CGPA', 'Academic_Performance', 
                         'Extra_Curricular_Score', 'Communication_Skills', 'Projects_Completed']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # 连接到数据库
        con = get_db_connection()
        cursor = con.cursor()
        
        try:
            # 清空表（避免数据重复）
            cursor.execute("TRUNCATE TABLE student_placement")
            logger.info(f"已清空 student_placement 表")
            
            # 准备插入数据
            # 只插入存在于 dataframe 中的列
            insert_columns = [col for col in STUDENT_PLACEMENT_COLUMNS if col in df.columns]
            
            # 构建 INSERT 语句
            placeholders = ', '.join(['%s'] * len(insert_columns))
            insert_sql = f"INSERT INTO student_placement ({', '.join(insert_columns)}) VALUES ({placeholders})"
            
            # 批量插入
            rows_to_insert = df[insert_columns].values.tolist()
            cursor.executemany(insert_sql, rows_to_insert)
            
            # 提交事务
            con.commit()
            
            rows_count = len(df)
            logger.info(f"成功导入 {rows_count} 条数据到 student_placement 表")
            
            return {"success": True, "rows": rows_count}
            
        except Exception as e:
            con.rollback()
            logger.warn(f"数据库导入失败: {str(e)}")
            return {"success": False, "error": f"数据库导入失败: {str(e)}"}
            
        finally:
            cursor.close()
            con.close()
            
    except Exception as e:
        logger.warn(f"文件导入失败: {str(e)}")
        return {"success": False, "error": str(e)}
