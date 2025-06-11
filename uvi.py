import pandas as pd
import pymysql


# 更新資料庫
def update_db():
    api_url = "https://data.moenv.gov.tw/api/v2/uv_s_01?api_key=9b651a1b-0732-418e-b4e9-e784417cadef&limit=1000&sort=datacreationdate%20desc&format=CSV"
    sqlstr = """
        insert ignore into uvi(sitename,uvi,unit,county,wgs84_lon,wgs84_lat,datacreationdate)
        values(%s,%s,%s,%s,%s,%s,%s)
    """
    row_count = 0
    message = ""
    try:
        # 讀取最新的雲端資料
        df = pd.read_csv(api_url)
        df["datacreationdate"] = pd.to_datetime(df["datacreationdate"], format="mixed")
        df = df.dropna(subset=["uvi"])  # 只排除 uvi 欄位為空值的資料
        df = df[df["uvi"] >= 0]  # 過濾合理 uvi 數值
        values = df.values.tolist()

        # 寫入資料庫
        conn = open_db()
        cur = conn.cursor()
        cur.executemany(sqlstr, values)
        row_count = cur.rowcount
        conn.commit()

        print(f"更新{row_count}筆資料成功!!!")
        message = "更新資料庫成功!!!"

    except Exception as e:
        print(e)
        message = f"更新資料失敗:{e}"
    finally:
        if conn is not None:
            conn.close()

    return row_count, message


# 開啟資料庫
def open_db():
    conn = None
    try:
        conn = pymysql.connect(
            host="127.0.0.1", port=3306, user="root", passwd="12345678", db="demo"
        )
    except Exception as e:
        print("資料庫開啟失敗", e)

    return conn


# 從資料庫取資料
def get_uvi_data_from_mysql():
    conn = None
    columns, datas = None, None
    try:
        conn = open_db()
        cur = conn.cursor()
        # sqlstr="(select MAX(datacreationdate) from uvi);"
        sqlstr = """
        SELECT sitename, uvi, county, datacreationdate
        FROM uvi
        WHERE datacreationdate >= CURDATE();
        """
        cur.execute(sqlstr)
        # 輸出資料表欄位
        # print(cur.description)
        columns = [col[0] for col in cur.description]
        # 實際的資料
        datas = cur.fetchall()
    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()

    return columns, datas


# 本地運行
if __name__ == "__main__":
    update_db()
