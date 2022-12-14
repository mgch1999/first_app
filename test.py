from streamlit_folium import folium_static
import folium
from google.cloud import bigquery
import streamlit as st
from google.oauth2 import service_account
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
import googlemaps
import matplotlib.pyplot as plt
import japanize_matplotlib


def get_credentials(credential):
    if credential == "gcp_service_account":
        return service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
    elif credential == "googlemapsapi":
        return googlemaps.Client(key=st.secrets["googlemapsapi"]["googleapikey"])
    else:
        return None


credentials = get_credentials("gcp_service_account")
gmaps = get_credentials("googlemapsapi")
        
client = bigquery.Client(
            credentials=credentials,
            project=credentials.project_id,
        )

st.subheader("希望条件を選択")

area = st.selectbox("エリア", ("千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区",
                    "豊島区", "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区", "指定なし"))

if area == "指定なし":
    area = ""
else:
    area = area

madori = st.selectbox("間取りタイプ",  ("ワンルーム", "1K", "1LDK"))

if madori == "ワンルーム":
    madori = "tokyo_1r"

elif madori == "1K":
    madori = "tokyo_1k"

else:
    madori = "tokyo_1ldk"



size = st.slider("面積(m2)", 0, 50, 25)
year = st.slider('築年数', 0, 100, 5)
access = st.slider('アクセス(分)', 0, 60, 5)


query = f"""
SELECT * FROM prediction-rent-price.dataset1.{madori}
WHERE address like "%{area}%";
"""
data = client.query(query).to_dataframe()

df = pd.DataFrame(data)


x = df[["sizes", "yearss", "accesses"]]
y = df[["prices"]]

X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

model = RandomForestRegressor()
model.fit(X_train, y_train)

pred = model.predict([[size, year, access]])[0] 
pred = round(pred, 2)

st.subheader(f"推定家賃は{pred}万円です。")

df = df[df["prices"] <= pred]
df = df[df["sizes"] >= size]
df = df[df["yearss"] <= year]
df = df[df["accesses"] <= access]

df1 = df[["title", "price", "size", "years", "access", "address", "url"]]

st.subheader("推定家賃よりもお得な物件はこちら↓")
st.dataframe(df1)


df2 = pd.pivot_table(data=df1, index="address")

map = folium.Map(location=[35.6895, 139.7390], zoom_start=11)

for i in range(0, len(df2)):

    gmap_list = gmaps.geocode(df2.index[i])

    ll = gmap_list[0]["geometry"]["location"]
    lat = ll["lat"]
    lng = ll["lng"]
    
    folium.Marker([lat, lng]).add_to(map)

st.subheader("物件マップ")
folium_static(map)


ward = ("指定なし","千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区",
                                      "豊島区", "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区")

ymin, ymax = 0, 1500

area1 = st.sidebar.selectbox("エリア選択", ward)
area2 = st.sidebar.selectbox("比較エリア選択", ward)
madori = st.sidebar.selectbox("間取りタイプ",  ("ワンルーム", "1K", "1LDK"))


if area1 == "指定なし":
    pass

else :
    area1 = area1
    
    if area2 == "指定なし":
        
        if madori == "ワンルーム":
            madori = "tokyo_1r"
        
        elif madori == "1K":
            madori = "tokyo_1k"
        
        else:
            madori = "tokyo_1ldk"

        query = f"""
        WITH data_with_ku AS (
        SELECT
        *,
        CASE 
            WHEN address LIKE '%{area1}%' THEN '{area1}' 
        END AS ku
        FROM
            `prediction-rent-price.dataset1.{madori}`
        )
        SELECT
        *
        FROM
        data_with_ku;"""

        data = client.query(query).to_dataframe()
        df = pd.DataFrame(data)
        df1 = df.loc[(df["ku"]==area1)]

        fig, ax = plt.subplots()
        ax.scatter(df1["sizes"], df1["prices"], alpha=0.3, color="dodgerblue",s=10, label=area1)
        plt.xlabel("面積(m2)")
        plt.ylabel("価格(万円)")
        plt.legend()
        st.pyplot(fig)

        fig, ax = plt.subplots()
        plt.hist(df1["prices"],alpha=0.3, bins=50, color="dodgerblue", label=area1)
        plt.vlines(df1["prices"].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1, label=f"平均家賃({area1})")
        plt.xlabel("家賃(万円)")
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)
        
        fig, ax = plt.subplots()
        plt.boxplot(df["prices"])
        st.pyplot(fig)

    else:
        area2 == area2

        if madori == "ワンルーム":
            madori = "tokyo_1r"
        
        elif madori == "1K":
            madori = "tokyo_1k"
        
        else:
            madori = "tokyo_1ldk"


        query = f"""
        WITH data_with_ku AS (
        SELECT
        *,
        CASE 
            WHEN address LIKE '%{area1}%' THEN '{area1}' 
            WHEN address LIKE '%{area2}%' THEN '{area2}'
        END AS ku
        FROM
            `prediction-rent-price.dataset1.{madori}`
        )
        SELECT
        *
        FROM
        data_with_ku;"""

        data = client.query(query).to_dataframe()
        df = pd.DataFrame(data)
        df1 = df.loc[(df["ku"]==area1)]
        df2 = df.loc[(df["ku"]==area2)]

        fig, ax = plt.subplots()
        ax.scatter(df1["sizes"], df1["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
        ax.scatter(df2["sizes"], df2["prices"], alpha=0.1, color="orange",s=10, label=area2)
        plt.xlabel("面積(m2)")
        plt.ylabel("家賃(万円)")
        plt.legend()
        st.pyplot(fig)
        
    
        fig, ax = plt.subplots()
        plt.hist(df1["prices"],alpha=0.4, color="dodgerblue", bins=50, label=area1)
        plt.hist(df2["prices"],alpha=0.3, color="orange", bins=50, label=area2)
        plt.vlines(df1["prices"].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1, label=f"平均家賃({area1})")
        plt.vlines(df2["prices"].mean(), ymin, ymax, color="orange", linestyle='dashed', linewidth=1, label=f"平均家賃({area2})" )
        plt.xlabel("家賃(万円)")
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)

