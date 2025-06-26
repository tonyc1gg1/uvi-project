from flask import Flask, render_template, request
from datetime import datetime
import pandas as pd
from uvi import (
    get_uvi_data_from_mysql,
    update_db,
    get_uvi_group_by_county,
    get_uvi_by_county,
    get_all_counties,
    get_history_data,
)


app = Flask(__name__)


@app.route("/filter", methods=["POST"])
def filter_data():
    # args=> form
    try:
        county = request.form.get("county")
        columns, datas = get_uvi_data_from_mysql()
        df = pd.DataFrame(datas, columns=columns)

        print("【初始 uvi 型別】", df["uvi"].dtype)
        print("【初始 uvi 類型分布】")
        print(df["uvi"].apply(type).value_counts())

        df["uvi"] = pd.to_numeric(df["uvi"], errors="coerce")
        df_county = df[df["county"] == county].copy()

        print("【初始 uvi 型別】", df["uvi"].dtype)
        print("【初始 uvi 類型分布】")
        print(df["uvi"].apply(type).value_counts())

        df_county["uvi"] = pd.to_numeric(df_county["uvi"], errors="coerce")

        # 取得特定縣市的資料
        df1 = df_county.groupby("sitename")["uvi"].mean().round(1)

        print("【平均結果】")
        print(df1)

        return {"county": county, "result": df1.to_dict()}
    except Exception as e:
        print("🚨 發生錯誤：", str(e))
        return {"error": str(e)}, 500


# 首頁
@app.route("/")
def index():
    county = request.args.get("county", "ALL")
    counties = get_all_counties()
    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if county == "ALL":
        columns, datas, uvi_data = get_uvi_group_by_county()
        series_data = None
        time_list = None
    else:
        columns, datas, uvi_data = get_uvi_by_county(county)
        _, _, uvi_data = get_uvi_group_by_county()

        time_list, series_data = get_history_data(county, days=7)

    return render_template(
        "index.html",
        columns=columns,
        datas=datas,
        counties=counties,
        selected_county=county,
        uvi_data=uvi_data,
        nowtime=nowtime,
        time_list=time_list,
        series_data=series_data,
    )


# 更新資料庫
@app.route("/update_db")
def update_uvi_db():
    count, message = update_db()
    nowtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    result = {"時間": nowtime, "更新筆數": count, "結果": message}

    return render_template("update_result.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)
