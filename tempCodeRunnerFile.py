def filter_data():
    # args=> form
    county = request.form.get("county")
    columns, datas = get_uvi_data_from_mysql()
    df = pd.DataFrame(datas, columns=columns)
    df["uvi"] = pd.to_numeric(df["uvi"], errors="coerce")
    # 取得特定縣市的資料
    df1 = (
        df.groupby("county")
        .get_group(county)
        .groupby("sitename")["uvi"]
        .mean()
        .round(2)
    )
    print(df1)
    print(df["uvi"].dtype)
    print(df["uvi"].apply(type).value_counts())
    return {"county": county}