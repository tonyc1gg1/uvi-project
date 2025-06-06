from flask import Flask, render_template
from datetime import datetime
import pandas as pd
import pymysql


app = Flask(__name__)


@app.route("/")
def index():
    # return f"<h1>Hello World!</h1><br>{datetime.now()}"
    return render_template("index.html")


@app.route("/uvi_data")
def get_uvi_data():
    api_url = "https://data.moenv.gov.tw/api/v2/uv_s_01?api_key=9b651a1b-0732-418e-b4e9-e784417cadef&limit=1000&sort=datacreationdate%20desc&format=CSV"
    df = pd.read_csv(api_url)
    df["datacreationdate"] = pd.to_datetime(df["datacreationdate"], format="mixed")
    df.dropna()
    df1 = df[df["uvi"] >= 0]
    return df1.values.tolist()


app.run(debug=True)
