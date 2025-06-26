import requests
import pandas as pd
from io import StringIO
import pymysql
import os
from dotenv import load_dotenv

load_dotenv(".env")


# 更新資料庫
def update_db():
    api_url = "https://data.moenv.gov.tw/api/v2/uv_s_01?api_key=9b651a1b-0732-418e-b4e9-e784417cadef&limit=1000&sort=datacreationdate%20desc&format=CSV"
    sqlstr = """
        insert ignore into uvi(sitename,uvi,unit,county,wgs84_lon,wgs84_lat,datacreationdate)
        values(%s,%s,%s,%s,%s,%s,%s)
    """
    row_count = 0
    message = ""
    conn = None
    try:
        # 改用 requests 下載，避免 SSL 驗證問題
        response = requests.get(api_url, verify=False, timeout=10)
        response.raise_for_status()

        # 讀取最新的雲端資料
        df = pd.read_csv(StringIO(response.text))
        df["datacreationdate"] = pd.to_datetime(df["datacreationdate"], format="mixed")
        df = df.dropna(subset=["uvi"])  # 排除 uvi 欄位為空值的資料
        df = df[df["uvi"] >= 0]  # 過濾合理 uvi 數值
        values = df.values.tolist()

        # 寫入資料庫
        conn = open_db()
        if conn is None:
            raise Exception("資料庫連線失敗")
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
        if conn:
            conn.close()

    return row_count, message


# 開啟資料庫
def open_db():
    conn = None
    try:
        conn = pymysql.connect(
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT")),
            user=os.environ.get("DB_USER"),
            passwd=os.environ.get("DB_PASSWORD"),
            db=os.environ.get("DB_NAME"),
            charset="utf8mb4",
        )
        return conn
    except Exception as e:
        print("資料庫開啟失敗", e)
        return None


# 從資料庫取資料
def get_uvi_data_from_mysql():
    conn = None
    columns, datas = None, None
    try:
        conn = open_db()
        cur = conn.cursor()

        sqlstr = """
        SELECT sitename, uvi, unit, county, wgs84_lon, wgs84_lat, datacreationdate
        FROM uvi
        WHERE datacreationdate = (SELECT MAX(datacreationdate) FROM uvi)
        """
        cur.execute(sqlstr)
        # 輸出資料表欄位
        columns = [col[0] for col in cur.description]
        # 實際的資料
        datas = cur.fetchall()

    except Exception as e:
        print(e)
    finally:
        if conn is not None:
            conn.close()

    return columns, datas


# 取全部縣市用 (for 地圖 + 總表)
def get_uvi_group_by_county():
    conn = open_db()
    try:
        if conn is None:
            return [], [], []
        cur = conn.cursor()

        # 取全部縣市平均
        sql = """
            SELECT county, ROUND(AVG(uvi), 1) AS uvi_avg
            FROM uvi
            WHERE datacreationdate = (SELECT MAX(datacreationdate) FROM uvi)
            GROUP BY county
        """
        cur.execute(sql)
        datas = cur.fetchall()

        datas_list = [list(row) for row in datas]
        columns = ["城市", "UVI"]

        # for echarts 地圖用的格式
        uvi_data = [{"name": row[0], "value": row[1]} for row in datas_list]

        return columns, datas_list, uvi_data
    finally:
        if conn:
            conn.close()


# 取某一縣市內各測站 (for 表格用)
def get_uvi_by_county(county):
    conn = open_db()
    try:
        if conn is None:
            return [], [], []

        cur = conn.cursor()

        sql = """
            SELECT sitename, uvi
            FROM uvi
            WHERE county = %s
            AND datacreationdate = (SELECT MAX(datacreationdate) FROM uvi)
        """
        cur.execute(sql, (county,))
        datas = cur.fetchall()
        datas_list = [list(row) for row in datas]
        columns = ["測站名稱", "UVI"]

        # 地圖維持使用總平均
        avg_uvi = round(sum(row[1] for row in datas_list) / len(datas_list), 1)
        uvi_data = [{"name": county, "value": avg_uvi}]

        return columns, datas_list, uvi_data
    finally:
        if conn:
            conn.close()


# 取出所有縣市
def get_all_counties():
    conn = open_db()
    try:
        if conn is None:
            return []

        cur = conn.cursor()
        sql = """
            SELECT DISTINCT county
            FROM uvi
            WHERE datacreationdate = (SELECT MAX(datacreationdate) FROM uvi)
        """
        cur.execute(sql)
        result = cur.fetchall()
        counties = sorted([row[0] for row in result])
        return counties
    finally:
        if conn:
            conn.close()


# 歷史監測資料(new)
def get_history_data(county, days=7):
    conn = open_db()
    try:
        if conn is None:
            return []

        cur = conn.cursor()
        sqlstr = """
            SELECT sitename, DATE(datacreationdate) as date, MAX(uvi)
            FROM uvi
            WHERE county = %s
            AND datacreationdate >= NOW() - INTERVAL %s DAY
            GROUP BY sitename, DATE(datacreationdate)
            ORDER BY sitename, date ASC
        """
        cur.execute(sqlstr, (county, days))
        datas = cur.fetchall()
        data_list = [list(row) for row in datas]

        # 建立DataFrame並轉換無數值類型
        df = pd.DataFrame(data_list, columns=["sitename", "date", "uvi"])
        df["uvi"] = pd.to_numeric(df["uvi"], errors="coerce")
        df["date"] = pd.to_datetime(df["date"])

        # 橫軸時間列表
        time_list = sorted(df["date"].dt.strftime("%Y-%m-%d").unique().tolist())

        # 每個測站一條線
        series_data = []
        for site in df["sitename"].unique():
            values = []
            for date in time_list:
                match = df[
                    (df["sitename"] == site)
                    & (df["date"].dt.strftime("%Y-%m-%d") == date)
                ]
                if not match.empty:
                    values.append(round(match["uvi"].values[0], 1))
                else:
                    values.append(None)  # 缺失先補空值
            series_data.append({"name": site, "type": "line", "data": values})

        return time_list, series_data
    finally:
        if conn:
            conn.close()


# 本地運行
if __name__ == "__main__":
    update_db()
