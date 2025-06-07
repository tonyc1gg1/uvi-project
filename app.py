from flask import Flask, render_template
from datetime import datetime
import pandas as pd
import pymysql
from uvi import get_uvi_data_from_mysql


app = Flask(__name__)


@app.route("/")
def index():
    columns, datas = get_uvi_data_from_mysql()
    return render_template("index.html", columns=columns, datas=datas)


if __name__ == "__main__":
    app.run(debug=True)
