from streamlit_folium import folium_static
import folium
from google.cloud import bigquery
import streamlit as st
from google.oauth2 import service_account
from sklearn.linear_model import LinearRegression
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
