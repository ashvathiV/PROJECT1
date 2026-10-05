import requests
import pandas as pd
from datetime import datetime
import numpy as np
import pymysql
from sqlalchemy import create_engine, text, String, DateTime, Float, Text # Import necessary types and text function

url = "https://earthquake.usgs.gov/fdsnws/event/1/query"
all_records = []
start_year = datetime.now().year - 5
end_year = datetime.now().year
for year in range(start_year, end_year + 1):
    for month in range(1, 13):

        start_date = f"{year}-{month:02d}-01"

        if month == 12:
            end_date = f"{year+1}-01-01"
        else:
            end_date = f"{year}-{month+1:02d}-01"

        print(start_date, "→", end_date)
        params = {
            "format": "geojson",
            "starttime": start_date,
            "endtime": end_date,
            "minmagnitude": 3
        }

        print(params)
        response = requests.get(url, params=params)
        if response.status_code != 200:
            print("Request failed:", response.text[:200])
            continue
        try:
            data = response.json()
        except ValueError:
            print("Invalid JSON response:", response.text[:200])
            continue

        if 'features' in data:
            for f in data["features"]:
                p = f["properties"]
                c = f["geometry"]["coordinates"]
                all_records.append({
                   "id": f.get("id"),
                    "mag": p.get("mag"),
                    "place": p.get("place"),
                    "time": p.get("time"),
                    "updated": p.get("updated"),
                    "url": p.get("url"),
                    "felt": p.get("felt"),
                    "cdi": p.get("cdi"),
                    "mmi": p.get("mmi"),
                    "alert": p.get("alert"),
                    "status": p.get("status"),
                    "tsunami": p.get("tsunami"),
                    "sig": p.get("sig"),
                    "net": p.get("net"),
                    "code": p.get("code"),
                    "sources": p.get("sources"),
                    "types": p.get("types"),
                    "nst": p.get("nst"),
                    "dmin": p.get("dmin"),
                    "rms": p.get("rms"),
                    "gap": p.get("gap"),
                    "magType": p.get("magType"),
                    "type": p.get("type"),
                    "title": p.get("title"),
                    "longitude": c[0],
                    "latitude": c[1],
                    "depth_km": c[2]
                })

df = pd.DataFrame(all_records)
df["time"] = pd.to_datetime(df["time"], unit="ms", errors="coerce")
df["updated"] = pd.to_datetime(df["updated"], unit="ms", errors="coerce")
df[["time", "updated"]]

numeric_cols = ["mag", "depth_km", "nst", "dmin", "rms", "gap",
                "magError", "depthError", "magNst", "sig"]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
median_fill = ["mag", "depth_km", "dmin", "rms", "gap"]
zero_fill = ["nst", "magError", "depthError", "magNst", "sig"]

for col in median_fill:
    if col in df.columns:
        df[col] = df[col].fillna(df[col].median())

for col in zero_fill:
    if col in df.columns:
        df[col] = df[col].fillna(0)
mode_fill_cols = ["alert", "status", "net", "magType", "type"]

for col in mode_fill_cols:
    if df[col].isnull().any():
        mode_val = df[col].mode()[0]
        df[col] = df[col].fillna(mode_val)
if "alert" in df.columns:
    df["alert"] = df["alert"].astype(str).str.lower().str.strip()
for col in ["sources", "types"]:
    df[col] = df[col].fillna("unknown")
string_fields = ["magType", "status", "type", "net", "sources", "types"]

for col in string_fields:
    if col in df.columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.replace(r"\s+", " ", regex=True)
            .str.lower()
        )
df["year"] = df["time"].dt.year
df["month"] =df["time"].dt.month
df["day"] = df["time"].dt.day
df["day_of_week"] = df["time"].dt.day_name()
df["depth_flag"] = np.where(df["depth_km"] < 70, "shallow", "deep")
def mag_flag(m):
    if m >= 7:
        return "destructive"
    elif m >= 6:
        return "strong"
    else:
        return "normal"

df["mag_flag"] = df["mag"].apply(mag_flag)

df["mmi"] = df["mmi"].fillna(0)
df["felt"] = df["felt"].fillna(0)
df["cdi"] = df["cdi"].fillna(0)
df = df.drop_duplicates(subset=["id"])
df.to_csv("earthquakes.csv", index=False)
from urllib.parse import quote_plus
import pymysql 
from sqlalchemy import create_engine, text 

password = quote_plus("NewPassword@123")
try:
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="NewPassword@123",
        port=3306,
        database="earthquake_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    print("✅ Connected to MySQL successfully using pymysql!")
    engine = create_engine(f"mysql+pymysql://root:{password}@localhost:3306/earthquake_db")

except Exception as e:
    print(f"Initial pymysql connection failed: {e}")
    engine = create_engine(f"mysql+pymysql://root:{password}@localhost:3306/earthquake_db")

if engine:
    try:
        with engine.connect() as conn:
            print("SQLAlchemy engine created and connected successfully.")
          
    except Exception as e:
        print(f"SQLAlchemy connection failed after engine creation: {e}")
else:
    print("Failed to create SQLAlchemy engine.")
    df.to_sql(
    name="earthquake",
    con= engine,
    if_exists="replace",
    index=False
)
print("Data inserted successfully")
queries = {
     "1. Top 10 strongest earthquakes (mag):"
 """SELECT * FROM earthquake ORDER BY mag DESC LIMIT 10;"""

     "2. Top 10 deepest earthquakes (depth_km):"
 """SELECT * FROM  earthquake ORDER BY depth_km DESC LIMIT 10;"""

 "3. Shallow earthquakes < 50 km and mag > 7.5:"
 """SELECT * FROM earthquake WHERE depth_km < 50  AND mag > 7.5;"""

 "5. Average magnitude per magnitude type (magType)"
 """SELECT magType , AVG(mag) AS magType FROM earthquake GROUP BY magType;"""

 "6. Year with most earthquakes:"
 """SELECT YEAR AS year, COUNT(*) AS total
    FROM earthquake GROUP BY YEAR
    ORDER BY total DESC
    LIMIT 1;"""

"7. Month with highest number of earthquakes:"
"""SELECT MONTH AS MONTH ,COUNT(*) AS total
   FROM earthquake GROUP BY MONTH
   ORDER BY total DESC
   LIMIT 1; """

"8. Day of week with most earthquakes:"
"""SELECT DAY AS day_of_week COUNT(*) AS total
   FROM earthquake GROUP BY DAY
   ORDER BY day_of_week DESC
   LIMIT 1;
   """
"9. Count of earthquakes per hour of day"
"""SELECT HOUR(time) AS hour ,COUNT(*) AS total
   FROM earthquake GROUP BY HOUR(time)
   ORDER BY hour;"""

"10.Most active reporting network (net):"
"""SELECT net, COUNT(*) AS total
FROM earthquake GROUP BY net
ORDER BY total DESC LIMIT 1;"""

"11.Top 5 places with highest casualties:"
"""SELECT
    place,
    alert,
    sig,
    mag
FROM earthquake
WHERE alert IN ('orange', 'red')
ORDER BY sig DESC
LIMIT 5;"""

"13.Average economic loss by alert level:"
"""SELECT
    alert,
    COUNT(*) AS total_events,
    AVG(sig) AS avg_sig,
    AVG(mag)AS avg_mag
FROM earthquake
GROUP BY alert
ORDER BY FIELD(alert, 'green', 'yellow', 'orange', 'red');"""

"14.  Count of reviewed vs automatic earthquakes (status):"\
"""SELECT status, AS TOTAL
FROM earthquake GROUP BY status;"""

"15.  Count by earthquake type (type):"
"""Select type, COUNT(*) AS total
FROM earthquake GROUP BY type;"""

"16.  Number of earthquakes by data type (types):"
"""SELECT  types , count(*) as total
FROM earthquake GROUP BY types """

"18.  Events with high station coverage (nst > threshold):"
"""SELECT *
FROM earthquake
WHERE nst > 50; """

"19.  Number of tsunamis triggered per year:"
"""SELECT year AS year, COUNT(*) AS tsunamis
FROM earthquake WHERE tsunamis = 1
GROUP BY year;"""

"20.  Count earthquakes by alert levels (red, orange, etc.);"
"""SELECT alert , COUNT(*) AS total
FROM earthquake GROUP BY alert"""

"21.Find the top 5 countries with the highest average magnitude of earthquakes in the past 5 years:"
"""SELECT place , AVG(mag) AS avg_mag 
FROM earthquake
WHERE `time` >= DATE_SUB(NOW(), INTERVAL 5 YEAR)
GROUP BY place
ORDER BY avg_mag DESC
LIMIT 5"""

"22.Find countries that have experienced both shallow and deep earthquakes within the same month:"
"""SELECT
    place,
    `year`,
    `month`
FROM earthquake
GROUP BY place, `year`, `month`
HAVING COUNT(DISTINCT depth_flag) = 2; """

"23.Compute the year-over-year growth rate in the total number of earthquakes globally:"
"""SELECT
    `year`,
    COUNT(*) AS total_events,
    (LAG(COUNT(*)) OVER (ORDER BY `year`) AS previous_year_events,
    COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY `year`))
        / LAG(COUNT(*)) OVER (ORDER BY `year`) * 100
     AS growth_percent
FROM earthquake
GROUP BY year
ORDER BY year;"""

"24. List the 3 most seismically active regions by combining both frequency and average magnitude."
"""SELECT
    place,
    COUNT(*) AS total_events,
    AVG(mag) AS avg_magnitude,
    ROUND(COUNT(*) * AVG(mag), 2) AS score
FROM earthquake
GROUP BY place
ORDER BY score DESC
LIMIT 3;"""

"25. For each country, calculate the average depth of earthquakes within ±5° latitude range of the equator:"
"""SELECT place AVG(depth_km) AS avg_depth
FROM earthquake 
WHERE latitude BETWEEN -5 AND 5
GROUP BY place;"""

"26. Identify countries having the highest ratio of shallow to deep earthquakes:"
"""SELECT
    place,
    SUM(depth_km < 70) AS shallow_count,
    SUM(depth_km > 300) AS deep_count,
    SUM(depth_km < 70) / NULLIF(SUM(depth_km > 300), 0) AS ratio
FROM earthquake
GROUP BY place
HAVING deep_count > 0
ORDER BY ratio DESC
LIMIT 5; """

"27. Find the average magnitude difference between earthquakes with tsunami alerts and those without"
"""SELECT
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 1) AS tsunami_avg,
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 0) AS no_tsunami_avg,
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 1) -
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 0) AS magnitude_difference;"""

"28. Using the gap and rms columns, identify events with the lowest data reliability (highest average error margins)"
"""SELECT *
FROM earthquake
ORDER BY gap DESC, rms DESC
LIMIT 10;"""

"30. Determine the regions with the highest frequency of deep-focus earthquakes (depth > 300 km):"
"""SELECT
    place,
    COUNT(*) AS deep_focus
FROM earthquake
WHERE depth_km > 300
GROUP BY place
ORDER BY deep_focus DESC
LIMIT 5;"""

}

import streamlit as st

st.title("🌍 Global Earthquake Dashboard")
