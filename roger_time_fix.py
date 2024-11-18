import sqlite3

import pandas as pd

connection = sqlite3.connect("roger.db")

sql = """
SELECT ID,
    DataLaikas
FROM judejimai
ORDER BY ID
"""
sql_upd = """
UPDATE judejimai
    SET Kada = ?
WHERE ID = ?
"""
df = pd.read_sql_query(sql, connection, index_col="ID")  # noqa: PD901

df["DataLaikas"] = pd.to_datetime(df["DataLaikas"])
summer_time_ranges = [
    (pd.Timestamp("2013-03-31"), pd.Timestamp("2013-10-27")),
    (pd.Timestamp("2014-03-30"), pd.Timestamp("2014-10-26")),
    (pd.Timestamp("2015-03-29"), pd.Timestamp("2015-10-25")),
    (pd.Timestamp("2016-03-27"), pd.Timestamp("2016-10-30")),
    (pd.Timestamp("2017-03-26"), pd.Timestamp("2017-10-29")),
    (pd.Timestamp("2018-03-25"), pd.Timestamp("2018-10-28")),
    (pd.Timestamp("2019-03-31"), pd.Timestamp("2019-10-27")),
]


def convert_summer_to_winter(row):  # noqa: ANN001, ANN201
    """Convert."""
    for start, end in summer_time_ranges:
        if start <= row["DataLaikas"] <= end:
            return row["DataLaikas"] - pd.Timedelta(hours=1)
    return row["DataLaikas"]


df["DataLaikas"] = df.apply(convert_summer_to_winter, axis=1)
df["DataLaikas"] -= pd.Timedelta(hours=2)  # to lithuania time zone
for index, row in df.iterrows():
    print(index, row["DataLaikas"])
    connection.execute(
        sql_upd,
        (row["DataLaikas"].strftime("%Y-%m-%d %H:%M:%S"), index),
    )

connection.commit()
