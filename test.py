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

st.set_page_config(layout="wide",
                   initial_sidebar_state="auto")
 
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

ward = ["指定なし", "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区",
                                      "豊島区", "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"]

variable1 = ["面積(m2)", "築年数", "アクセス(分)"]
variable2 = ["家賃(万円)", "面積(m2)", "築年数", "アクセス(分)"]



ymin, ymax = 0, 1500

area1 = st.selectbox("エリア選択", ward)
area2 = st.selectbox("比較エリア選択", ward)
madori = st.selectbox("間取りタイプ",  ("ワンルーム", "1K", "1LDK"))

if madori =="ワンルーム":
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
        WHEN address LIKE '%千代田区%' THEN '千代田区' 
        WHEN address LIKE '%中央区%' THEN '中央区' 
        WHEN address LIKE '%港区%' THEN '港区' 
        WHEN address LIKE '%新宿区%' THEN '新宿区' 
        WHEN address LIKE '%文京区%' THEN '文京区' 
        WHEN address LIKE '%台東区%' THEN '台東区' 
        WHEN address LIKE '%墨田区%' THEN '墨田区' 
        WHEN address LIKE '%江東区%' THEN '江東区' 
        WHEN address LIKE '%品川区%' THEN '品川区' 
        WHEN address LIKE '%目黒区%' THEN '目黒区' 
        WHEN address LIKE '%大田区%' THEN '大田区' 
        WHEN address LIKE '%世田谷区%' THEN '世田谷区' 
        WHEN address LIKE '%渋谷区%' THEN '渋谷区' 
        WHEN address LIKE '%中野区%' THEN '中野区' 
        WHEN address LIKE '%杉並区%' THEN '杉並区' 
        WHEN address LIKE '%豊島区%' THEN '豊島区' 
        WHEN address LIKE '%北区%' THEN '北区' 
        WHEN address LIKE '%荒川区%' THEN '荒川区' 
        WHEN address LIKE '%板橋区%' THEN '板橋区' 
        WHEN address LIKE '%練馬区%' THEN '練馬区' 
        WHEN address LIKE '%足立区%' THEN '足立区' 
        WHEN address LIKE '%葛飾区%' THEN '葛飾区' 
        WHEN address LIKE '%江戸川区%' THEN '江戸川区' 
    END AS ku
    FROM
        `prediction-rent-price.dataset1.{madori}`
    )
    SELECT
    *
    FROM
    data_with_ku
    ;"""

data = client.query(query).to_dataframe()
df = pd.DataFrame(data)

def scatter():
    st.subheader("散布図")
    left, right = st.columns(2)
    with left:
        exp = st.selectbox("説明変数", variable1)
        st.write("目的変数:家賃(万円)")
        if exp == "面積(m2)":
            exp1 = "sizes"
        elif exp == "築年数":
            exp1 = "yearss"
        else:
            exp1 = "accesses"
        s1 = pd.Series(df[exp1])
        s2 = pd.Series(df["prices"])
        st.write(s1.corr(s2))
    with right:
        fig, ax = plt.subplots()
        ax.scatter(df[exp1], df["prices"], alpha=0.4, color="dodgerblue",s=10)
        plt.xlabel(exp)
        plt.ylabel("家賃")
        plt.legend()
        st.pyplot(fig)

def hist():
    left, right = st.columns(2)
    with left:
        exp = st.selectbox("変数", variable2)
        if exp == "面積(m2)":
            exp1 = "sizes"
        elif exp == "築年数":
            exp1 = "yearss"
        elif exp == "アクセス(分)":
            exp1 = "accesses"
        else:
            exp1 = "prices"
        st.write("平均")
        st.write(df[exp1].mean())
    with right:
        fig, ax = plt.subplots()
        plt.hist(df[exp1],alpha=0.4, color="dodgerblue", bins=100)
        plt.vlines(df[exp1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
        plt.xlabel(exp)
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)


def analysis_23(madori):
    left, right = st.columns(2)
    with left:
        avg = pd.pivot_table(df, index="ku", values="prices")
        avg = avg.sort_values("prices", ascending=False)
        st.table(avg.style.format('{:.1f}'))
    with right:
        fig, ax = plt.subplots()
        ax.bar(avg.index, height=avg["prices"], color="dodgerblue")
        plt.xticks(rotation=50)
        st.pyplot(fig)
    
    scatter()
    
    hist()

    

        


def analysis(madori):
    st.write("a")

class Select():
    def __init__(self, area1, area2):
        self.area1 = area1
        self.area2 = area2

    def select_city(self, madori): 
        if self.area1 == "指定なし":
            if self.area2 == "指定なし":
                analysis_23(madori)
            else:
                analysis_23(madori)
        else:
            if self.area2 == "指定なし":
                analysis(madori)
            else:
                analysis(madori)






scatter_plot = Select(area1, area2)
scatter_plot.select_city(madori)


