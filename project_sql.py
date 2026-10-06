import pandas as pd
import streamlit as st
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
     "1. Top 10 strongest earthquakes (mag)":
 """SELECT * FROM earthquake ORDER BY mag DESC LIMIT 10;""",

     "2. Top 10 deepest earthquakes (depth_km)":
 """SELECT * FROM  earthquake ORDER BY depth_km DESC LIMIT 10;""",

    "3. Shallow earthquakes < 50 km and mag > 7.5":
"""SELECT * FROM earthquake WHERE depth_km < 50  AND mag > 7.5;""",

"4. Average depth per continent":
"""SELECT 'NOT AVALIABLE' AS NOTE""",

    "5. Average magnitude per magnitude type (magType)":
 """SELECT magType , AVG(mag) AS magnitude FROM earthquake GROUP BY magType;""",

 "6. Year with most earthquakes":
 """SELECT year AS year, COUNT(*) AS total
    FROM earthquake GROUP BY year
    ORDER BY total DESC
    LIMIT 1;""",

"7. Month with highest number of earthquakes":
"""SELECT month AS month ,COUNT(*) AS total
   FROM earthquake GROUP BY month
   ORDER BY total DESC
   LIMIT 1; """,

"8. Day of week with most earthquakes":
"""SELECT DAY AS day_of_week, COUNT(*) AS total
   FROM earthquake GROUP BY DAY
   ORDER BY day_of_week DESC
   LIMIT 1;""",
"9. Count of earthquakes per hour of day":
"""SELECT HOUR( time ) AS hour ,COUNT(*) AS total
   FROM earthquake GROUP BY HOUR(time)
   ORDER BY hour;""",

"10.Most active reporting network (net)":
"""SELECT net, COUNT(*) AS total
FROM earthquake GROUP BY net
ORDER BY total DESC LIMIT 1;""",

"11.Top 5 places with highest casualties":
"""SELECT
    place,
    alert,
    sig,
    mag
FROM earthquake
WHERE alert IN ('orange', 'red')
ORDER BY sig DESC
LIMIT 5;""",

"12.  Total estimated economic loss per continent":
"""SELECT 'NOT AVALIABLE' AS NOTE""",

"13.Average economic loss by alert level":
"""SELECT
    alert,
    COUNT(*) AS total_events,
    AVG(sig) AS avg_sig,
    AVG(mag)AS avg_mag
FROM earthquake
GROUP BY alert
ORDER BY FIELD(alert, 'green', 'yellow', 'orange', 'red');""",

"14.  Count of reviewed vs automatic earthquakes (status)":
"""SELECT status, COUNT(*) AS TOTAL
FROM earthquake GROUP BY status;""",

"15.  Count by earthquake type (type)":
"""Select type, COUNT(*) AS total
FROM earthquake GROUP BY type;""",

"16.  Number of earthquakes by data type (types)":
"""SELECT  types , count(*) as total
FROM earthquake GROUP BY types """,

"17.  Average RMS and gap per continent":
"""SELECT 'NOT AVALIABLE' AS NOTE""",

"18.  Events with high station coverage (nst > threshold)":
"""SELECT *
FROM earthquake
WHERE nst > 50; """,

"19.  Number of tsunamis triggered per year":
"""SELECT 'year' , COUNT(*) AS tsunamis
FROM earthquake WHERE tsunami
GROUP BY 'year';""",

"20.  Count earthquakes by alert levels (red, orange, etc.)":
"""SELECT alert , COUNT(*) AS total
FROM earthquake GROUP BY alert;""",

"21.Find the top 5 countries with the highest average magnitude of earthquakes in the past 5 years":
"""SELECT place , AVG(mag) AS avg_mag 
FROM earthquake
WHERE `time` >= DATE_SUB(NOW(), INTERVAL 5 YEAR)
GROUP BY place
ORDER BY avg_mag DESC
LIMIT 5;""",

"22.Find countries that have experienced both shallow and deep earthquakes within the same month":
"""SELECT
    place,
    `year`,
    `month`
FROM earthquake
GROUP BY place, `year`, `month`
HAVING COUNT(DISTINCT depth_flag) = 2; """,

"23.Compute the year-over-year growth rate in the total number of earthquakes globally":
"""SELECT `year`,
                  COUNT(*) AS total_events,
                  LAG(COUNT(*)) OVER (ORDER BY `year`) AS previous_year_events,
                  ROUND((COUNT(*) - LAG(COUNT(*)) OVER (ORDER BY `year`))
                        / LAG(COUNT(*)) OVER (ORDER BY `year`) * 100, 2) AS growth_percent
           FROM earthquake
           GROUP BY `year`
           ORDER BY `year`;""",

"24. List the 3 most seismically active regions by combining both frequency and average magnitude":
"""SELECT
    place,
    COUNT(*) AS total_events,
    AVG(mag) AS avg_magnitude,
    ROUND(COUNT(*) * AVG(mag), 2) AS score
FROM earthquake
GROUP BY place
ORDER BY score DESC
LIMIT 3;""",

"25. For each country, calculate the average depth of earthquakes within ±5° latitude range of the equator":
"""SELECT place ,AVG(depth_km) AS avg_depth
FROM earthquake 
WHERE latitude BETWEEN -5 AND 5
GROUP BY place;""",

"26. Identify countries having the highest ratio of shallow to deep earthquakes":
"""SELECT
    place,
    SUM(depth_km < 70) AS shallow_count,
    SUM(depth_km > 300) AS deep_count,
    SUM(depth_km < 70) / NULLIF(SUM(depth_km > 300), 0) AS ratio
FROM earthquake
GROUP BY place
HAVING deep_count > 0
ORDER BY ratio DESC
LIMIT 5; """,

"27. Find the average magnitude difference between earthquakes with tsunami alerts and those without":
"""SELECT
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 1) AS tsunami_avg,
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 0) AS no_tsunami_avg,
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 1) -
    (SELECT AVG(mag) FROM earthquake WHERE tsunami = 0) AS magnitude_difference;""",

"28. Using the gap and rms columns, identify events with the lowest data reliability (highest average error margins)":
"""SELECT *
FROM earthquake
ORDER BY gap DESC, rms DESC
LIMIT 10;""",

" 29. Find pairs of consecutive earthquakes (by time) that occurred within 50 km of each other and within 1 hour":
""" SELECT 'NOT AVALIABLE' AS NOTE""",

"30. Determine the regions with the highest frequency of deep-focus earthquakes (depth > 300 km)":
"""SELECT
    place,
    COUNT(*) AS deep_focus
FROM earthquake
WHERE depth_km > 300
GROUP BY place
ORDER BY deep_focus DESC
LIMIT 5;""",

}

import streamlit as st

st.title("🌍 Global Earthquake Dashboard")
st.divider()
with st.sidebar:
    st.title("🌍 Earthquake Project")
    st.caption("SQL analysis dashboard")

    st.markdown("### About")
    st.write(
        "This project collects earthquake data from the USGS API, cleans it with "
        "pandas, stores it in MySQL, and answers analysis questions with SQL queries."
    )

    st.markdown("### Data")
    st.write("- **Source:** USGS Earthquake API")
    st.write("- **Period:** last 5 years")
    st.write("- **Minimum magnitude:** 3")
    st.write("- **Table:** `earthquake` in `earthquake_db`")

    st.markdown("### Pipeline")
    st.write("1. Fetch data from the API (requests)")
    st.write("2. Clean and add new columns (pandas)")
    st.write("3. Store in MySQL (SQLAlchemy)")
    st.write("4. Query with SQL")
    st.write("5. Display results (Streamlit)")

    st.markdown("### Tools")
    st.write("Python, Pandas, MySQL, SQLAlchemy, Streamlit")

    st.markdown("### Key columns")
    st.write(
        "`mag`, `depth_km`, `place`, `time`, `alert`, `tsunami`, "
        "`sig`, `nst`, `gap`, `rms`, `depth_flag`, `mag_flag`"
    )

    st.divider()
 
choice = st.selectbox("Select a query", list(queries.keys()))
 
if st.button("Show Result"):
    try:
        result = pd.read_sql(queries[choice], engine)
        st.dataframe(result)
    except Exception as e:
        st.error(f"Error: {e}")
st.toast("Query ran successfully!", icon="🎉")
