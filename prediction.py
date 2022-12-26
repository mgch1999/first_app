from streamlit_folium import folium_static
import folium
from google.cloud import bigquery
import streamlit as st
from google.oauth2 import service_account
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import pandas as pd
import googlemaps

#ページ設定
st.set_page_config(layout="wide",
                   initial_sidebar_state="expanded")

#api呼び出し
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

#サイドバー関連
markdown1 = "使用方法"
markdown2 = "このアプリは、東京23区内の賃貸物件を対象に希望条件下の家賃を予測します。お得な物件リストは、推定家賃よりも安く、指定した条件よりも築浅、面積が大きく、駅までのアクセス時間が短い物件を抽出したリストです。"
st.sidebar.subheader(markdown1)
st.sidebar.write(markdown2)

st.title("23区家賃予測アプリ")
st.subheader("希望条件を選択")

#条件選択
left, right = st.columns(2)
with left:
    area = st.selectbox("エリア", ("千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区",
                        "豊島区", "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区", "指定なし"))
    if area == "指定なし":
        area = ""
    else:
        area = area
with right:
    madori = st.selectbox("間取りタイプ",  ("ワンルーム", "1K", "1LDK"))
    if madori == "ワンルーム":
        madori = "tokyo_1r"
    elif madori == "1K":
        madori = "tokyo_1k"
    else:
        madori = "tokyo_1ldk"

s1, s2, s3 = st.columns(3)
with s1:
    size = st.slider("面積(m2)", 0, 50, 25)
with s2:
    year = st.slider('築年数', 0, 100, 5)
with s3:
    access = st.slider('アクセス(分)', 0, 60, 5)

#クエリ実行
query = f"""
SELECT * FROM prediction-rent-price.dataset1.{madori}
WHERE address like "%{area}%";
"""
data = client.query(query).to_dataframe()
df = pd.DataFrame(data)

#ランダムフォレストで予測
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

#リストとマップ表示
left, right = st.columns(2)
with left:
    st.subheader("お得な物件リスト")
    st.dataframe(df1)
with right:
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
