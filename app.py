from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd
import pymysql
from uvi import get_uvi_data_from_mysql, update_db
import json


app = Flask(__name__)


#
@app.route("/filter", methods=["POST"])
def filter_data():
    # args=> form
    county = request.form.get("county")
    columns, datas = get_uvi_data_from_mysql()
    df = pd.DataFrame(datas, columns=columns)
    # 取得特定縣市的資料
    df1 = (
        df.groupby("county")
        .get_group(county)
        .groupby("sitename")["uvi"]
        .mean()
        .round(2)
    )
    print(df1)
    return {"county": county}


@app.route("/")
def index():
    # 取得資料庫最新的資料
    columns, datas = get_uvi_data_from_mysql()
    # 取出不同縣市給select
    df = pd.DataFrame(datas, columns=columns)
    # 排序縣市
    counties = sorted(df["county"].unique().tolist())

    # 選取縣市後的資料(預設ALL)
    county = request.args.get("county", "ALL")
    # 替換正體字為地圖可對應名稱

    df = pd.DataFrame(datas, columns=columns)

    if county != "ALL":
        # 取得特定縣市的資料
        df = df.groupby("county").get_group(county)
        columns = df.columns.tolist()
        datas = df.values.tolist()

    uvi_by_county = (
        df.groupby("county")["uvi"]
        .mean()
        .round(2)
        .reset_index()
        .rename(columns={"county": "name", "uvi": "value"})
    )

    uvi_data = uvi_by_county.to_dict(orient="records")
    # # 繪製所需資料
    # x_data = df["sitename"].to_list()
    # y_data = df["uvi"].to_list()

    return render_template(
        "index.html",
        columns=columns,
        datas=datas,
        counties=counties,
        selected_county=county,
        # x_data=x_data,
        # y_data=y_data,
        uvi_data=uvi_data,
    )


# 更新資料庫
@app.route("/update_db")
def update_uvi_db():
    count, message = update_db()
    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = json.dumps(
        {"時間": nowtime, "更新筆數": count, "結果": message}, ensure_ascii=False
    )
    return result


if __name__ == "__main__":
    app.run(debug=True)
