"""将 CSV 示例数据导入 MySQL 的 student_placement 表。"""

import csv
import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_PATH = BASE_DIR / "data" / "sample_student_placement.csv"
DATA_FILE_PATH = Path(os.getenv("DATA_FILE_PATH", str(DEFAULT_DATA_PATH)))
if not DATA_FILE_PATH.is_absolute():
    DATA_FILE_PATH = BASE_DIR / DATA_FILE_PATH


def get_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "localhost"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "usermessage"),
        charset="utf8mb4",
    )


def import_data():
    if not DATA_FILE_PATH.exists():
        print(f"错误：数据文件不存在：{DATA_FILE_PATH}")
        return False

    con = get_connection()
    cursor = con.cursor()

    try:
        print("清空 student_placement 表现有数据...")
        cursor.execute("TRUNCATE TABLE student_placement")

        print(f"读取数据文件：{DATA_FILE_PATH}")
        with DATA_FILE_PATH.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        insert_sql = """
        INSERT INTO student_placement (
            College_ID, IQ, Prev_Sem_Result, CGPA, Academic_Performance,
            Internship_Experience, Extra_Curricular_Score, Communication_Skills,
            Projects_Completed, Placement
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        data_batch = [
            (
                row["College_ID"],
                int(row["IQ"]),
                float(row["Prev_Sem_Result"]),
                float(row["CGPA"]),
                int(row["Academic_Performance"]),
                row["Internship_Experience"],
                int(row["Extra_Curricular_Score"]),
                int(row["Communication_Skills"]),
                int(row["Projects_Completed"]),
                row["Placement"],
            )
            for row in rows
        ]

        cursor.executemany(insert_sql, data_batch)
        con.commit()

        cursor.execute("SELECT COUNT(*) FROM student_placement")
        count = cursor.fetchone()[0]
        print(f"数据导入完成，共导入 {count} 条记录")
        return True
    except Exception as e:
        con.rollback()
        print(f"导入失败：{e}")
        return False
    finally:
        cursor.close()
        con.close()


if __name__ == "__main__":
    success = import_data()
    if success:
        print("可以启动后端了：python main.py")
