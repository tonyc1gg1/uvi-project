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

        history_data = get_history_data(county, days=7)
        df = pd.DataFrame(history_data, columns=["sitename", "uvi", "date"])
        pivot_df = (
            df.pivot_table(index="date", columns="sitename", values="uvi")
            .fillna(0)
            .round(2)
        )
        pivot_df.index = pd.to_datetime(pivot_df.index)
        time_list = pivot_df.index.strftime("%Y-%m-%d").tolist()
        series_data = [
            {"name": site, "type": "line", "data": pivot_df[site].tolist()}
            for site in pivot_df.columns
        ]

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
    app.run(debug=False)
