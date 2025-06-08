from flask import Flask, render_template
from datetime import datetime
import pandas as pd
import pymysql
from uvi import get_uvi_data_from_mysql, update_db
import json


app = Flask(__name__)


@app.route("/")
def index():
    columns, datas = get_uvi_data_from_mysql()
    return render_template("index.html", columns=columns, datas=datas)


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
