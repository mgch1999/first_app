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
import numpy as np

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

ward1 = ["全体", "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区",
                                      "豊島区", "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"]
ward2 = ["指定なし", "千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区",
                                      "豊島区", "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区"]
variable1 = ["面積(m2)", "築年数", "アクセス(分)"]
variable2 = ["家賃(万円)", "面積(m2)", "築年数", "アクセス(分)"]

area1 = st.sidebar.selectbox("エリア選択", ward1)
area2 = st.sidebar.selectbox("比較エリア選択", ward2)
madori = st.sidebar.selectbox("間取りタイプ",  ("ワンルーム", "1K", "1LDK"))
hennsuu = st.sidebar.selectbox("変数選択", variable2)

if madori =="ワンルーム":
    madori = "tokyo_1r"
elif madori == "1K":
    madori = "tokyo_1k"
else:
    madori = "tokyo_1ldk"

if hennsuu == "面積(m2)":
    hennsuu1 = "sizes"
elif hennsuu == "築年数":
    hennsuu1 = "yearss"
elif hennsuu == "アクセス(分)":
    hennsuu1 = "accesses"
else:
    hennsuu1 = "prices"


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

def analysis1():
    ymin, ymax = 0, 50000
    st.subheader("23区家賃平均")
    left, right = st.columns(2)
    with left:
        avg = pd.pivot_table(df, index="ku", values="prices")
        avg = avg.sort_values("prices", ascending=False)
        st.table(avg.style.format('{:.1f}'))
    with right:
        fig, ax = plt.subplots()
        ax.bar(avg.index, height=avg["prices"], color="dodgerblue", label=area1)
        plt.legend()
        plt.title("家賃平均グラフ")
        plt.xticks(rotation=50)
        st.pyplot(fig)
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
        st.write("相関係数")
        corr1 = round(s1.corr(s2), 2)
        st.write(f"{corr1}")
    with right:
        fig, ax = plt.subplots()
        ax.scatter(df[exp1], df["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
        plt.xlabel(exp)
        plt.ylabel("家賃")
        plt.legend()
        st.pyplot(fig)
    left, right = st.columns(2)
    with left:
        exp = st.selectbox("変数", variable2)
        if exp == "面積(m2)":
            exp1 = "sizes"
            unit = "m2"
        elif exp == "築年数":
            exp1 = "yearss"
            unit = "年"
        elif exp == "アクセス(分)":
            exp1 = "accesses"
            unit = "分"
        else:
            exp1 = "prices"
            unit = "万円"
        st.write("平均")
        avg1 = round(df[exp1].mean(), 2)
        st.write(f"{avg1}{unit}")
    with right:
        fig, ax = plt.subplots()
        plt.hist(df[exp1],alpha=0.4, color="dodgerblue", bins=100, label=area1)
        plt.vlines(df[exp1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
        plt.xlabel(exp)
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)

def analysis2():
    ymin, ymax = 0, 50000
    df_ward2 = df[df["ku"] == area2]
    left, middle1, middle2, right = st.columns(4)
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
        s3 = pd.Series(df_ward2[exp1])
        s4 = pd.Series(df_ward2["prices"])
        st.write("相関係数")
        corr1 = round(s1.corr(s2), 2)
        corr2 = round(s3.corr(s4), 2)
        st.write(f"{area1}:{corr1}")
        st.write(f"{area2}:{corr2}")
    with middle1:
        fig, ax = plt.subplots()
        ax.scatter(df[exp1], df["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
        ax.scatter(df_ward2[exp1], df_ward2["prices"], alpha=0.4, color="orange",s=10, label=area2)
        plt.xlabel(exp)
        plt.ylabel("家賃")
        plt.legend()
        st.pyplot(fig)
    with middle2:
        exp = st.selectbox("変数", variable2)
        if exp == "面積(m2)":
            exp1 = "sizes"
            unit = "m2"
        elif exp == "築年数":
            exp1 = "yearss"
            unit = "年"
        elif exp == "アクセス(分)":
            exp1 = "accesses"
            unit = "分"
        else:
            exp1 = "prices"
            unit = "万円"
        st.write("平均")
        avg1 = round(df[exp1].mean(), 2)
        avg2 = round(df_ward2[exp1].mean(), 2)
        st.write(f"{area1}:{avg1}{unit}")
        st.write(f"{area2}:{avg2}{unit}")
    with right:
        fig, ax = plt.subplots()
        plt.hist(df[exp1],alpha=0.4, color="dodgerblue", bins=100, label=area1)
        plt.hist(df_ward2[exp1],alpha=0.4, color="orange", bins=100, label=area2)
        plt.vlines(df[exp1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
        plt.vlines(df_ward2[exp1].mean(), ymin, ymax, color="orange", linestyle='dashed', linewidth=1)
        plt.xlabel(exp)
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)
    
def analysis3():
    ymin, ymax = 0, 1500
    df_ward1 = df[df["ku"] == area1]
    left, middle1, middle2, right = st.columns(4)
    with left:
        exp = st.selectbox("説明変数", variable1)
        st.write("目的変数:家賃(万円)")
        if exp == "面積(m2)":
            exp1 = "sizes"
        elif exp == "築年数":
            exp1 = "yearss"
        else:
            exp1 = "accesses"
        s1 = pd.Series(df_ward1[exp1])
        s2 = pd.Series(df_ward1["prices"])
        st.write("相関係数")
        corr1 = round(s1.corr(s2), 2)
        st.write(f"{corr1}")
    with middle1:
        fig, ax = plt.subplots()
        ax.scatter(df_ward1[exp1], df_ward1["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
        plt.xlabel(exp)
        plt.ylabel("家賃")
        plt.legend()
        st.pyplot(fig)
    with middle2:
        exp = st.selectbox("変数", variable2)
        if exp == "面積(m2)":
            exp1 = "sizes"
            unit = "m2"
        elif exp == "築年数":
            exp1 = "yearss"
            unit = "年"
        elif exp == "アクセス(分)":
            exp1 = "accesses"
            unit = "分"
        else:
            exp1 = "prices"
            unit = "万円"
        st.write("平均")
        avg1 = round(df_ward1[exp1].mean(), 2)
        st.write(f"{area1}:{avg1}{unit}")
    with right:
        fig, ax = plt.subplots()
        plt.hist(df_ward1[exp1],alpha=0.4, color="dodgerblue", bins=100, label=area1)
        plt.vlines(df_ward1[exp1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
        plt.xlabel(exp)
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)

def analysis4():
    ymin, ymax = 0, 1500
    df_ward1 = df[df["ku"] == area1]
    df_ward2 = df[df["ku"] == area2]
    left, right = st.columns(2)
    with right:
        avg = pd.pivot_table(df, index="ku", values=hennsuu1)
        avg = avg.sort_values(hennsuu1, ascending=False)
        fig, ax = plt.subplots()
        ax.bar(avg.index, height=avg[hennsuu1], color="dodgerblue")
        plt.legend()
        plt.xticks(rotation=50)
        st.pyplot(fig)
    with left:
        fig, ax = plt.subplots()
        plt.title("散布図")
        ax.scatter(df_ward1[hennsuu1], df_ward1["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
        ax.scatter(df_ward2[hennsuu1], df_ward2["prices"], alpha=0.4, color="orange",s=10, label=area2)
        plt.xlabel(hennsuu)
        plt.ylabel("家賃")
        plt.legend()
        st.pyplot(fig)
    left, right = st.columns(2)
    with right:
        plt.title("ヒストグラム")
        fig, ax = plt.subplots()
        plt.hist(df_ward1[hennsuu1],alpha=0.4, color="dodgerblue", bins=100, label=area1)
        plt.hist(df_ward2[hennsuu1],alpha=0.4, color="orange", bins=100, label=area2)
        plt.vlines(df_ward1[hennsuu1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
        plt.vlines(df_ward2[hennsuu1].mean(), ymin, ymax, color="orange", linestyle='dashed', linewidth=1)
        plt.xlabel(hennsuu)
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)
    with left:
        bins = np.arange(0, 30, 3)
        freq = pd.DataFrame({f"{area2}":df_ward2[hennsuu1].value_counts(bins=bins, sort=False),
                             f"{area1}":df_ward1[hennsuu1].value_counts(bins=bins, sort=False)})
        freq[area1], freq[area2] = freq[area1]/freq[area1].sum(), freq[area2]/freq[area2].sum()
        colors = ["lightcoral", "darkorange", "gold", "lightgreen", "mediumturquoise", "dodgerblue", "mediumblue", "mediumorchid", "mediumvioletred"]
        label = ["0~3万円", "3~6万円", "6~9万円", "9~12万円", "12~15万円", "15~18万円", "18~21万円", "21~24万円" , "24~27万円"]
        fig, ax = plt.subplots()
        left_data = pd.Series(np.zeros(len(freq.columns)), index=freq.columns.tolist())
        for i in range(len(freq.index)):
            bar_list = ax.barh(freq.columns, freq.iloc[i], color=colors[i], left=left_data, height=0.5)
            left_data += freq.iloc[i]
        ax.legend(label, loc='upper left', bbox_to_anchor=(1, 1), fontsize=10)
        plt.xlim([0, 1])
        st.pyplot(fig)
        
    




    # with left:
    #     exp = st.selectbox("説明変数", variable1)
    #     st.write("目的変数:家賃(万円)")
    #     if exp == "面積(m2)":
    #         exp1 = "sizes"
    #     elif exp == "築年数":
    #         exp1 = "yearss"
    #     else:
    #         exp1 = "accesses"
    #     s1 = pd.Series(df_ward1[exp1])
    #     s2 = pd.Series(df_ward1["prices"])
    #     s3 = pd.Series(df_ward2[exp1])
    #     s4 = pd.Series(df_ward2["prices"])
    #     st.write("相関係数")
    #     corr1 = round(s1.corr(s2), 2)
    #     corr2 = round(s3.corr(s4), 2)
    #     st.write(f"{area1}:{corr1}")
    #     st.write(f"{area2}:{corr2}")
    # with middle1:
    #     fig, ax = plt.subplots()
    #     ax.scatter(df_ward1[exp1], df_ward1["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
    #     ax.scatter(df_ward2[exp1], df_ward2["prices"], alpha=0.4, color="orange",s=10, label=area2)
    #     plt.xlabel(exp)
    #     plt.ylabel("家賃")
    #     plt.legend()
    #     st.pyplot(fig)
    # with middle2:
    #     exp = st.selectbox("変数", variable2)
    #     if exp == "面積(m2)":
    #         exp1 = "sizes"
    #         unit = "m2"
    #     elif exp == "築年数":
    #         exp1 = "yearss"
    #         unit = "年"
    #     elif exp == "アクセス(分)":
    #         exp1 = "accesses"
    #         unit = "分"
    #     else:
    #         exp1 = "prices"
    #         unit = "万円"
    #     st.write("平均")
    #     avg1 = round(df_ward1[exp1].mean(), 2)
    #     avg2 = round(df_ward2[exp1].mean(), 2)
    #     st.write(f"{area1}:{avg1}{unit}")
    #     st.write(f"{area2}:{avg2}{unit}")
    # with right:
    #     fig, ax = plt.subplots()
    #     plt.hist(df_ward1[exp1],alpha=0.4, color="dodgerblue", bins=100, label=area1)
    #     plt.hist(df_ward2[exp1],alpha=0.4, color="orange", bins=100, label=area2)
    #     plt.vlines(df_ward1[exp1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
    #     plt.vlines(df_ward2[exp1].mean(), ymin, ymax, color="orange", linestyle='dashed', linewidth=1)
    #     plt.xlabel(exp)
    #     plt.ylabel("物件数")
    #     plt.legend()
    #     st.pyplot(fig)
class Select():
    def __init__(self, area1, area2):
        self.area1 = area1
        self.area2 = area2

    def select_city(self): 
        if self.area1 == "全体" and self.area2 == "指定なし":
            analysis1()
        elif area1 == "全体" and area2 != "指定なし":
            analysis2()
        elif area1 != "全体" and area2 == "指定なし":
            analysis3()
        elif area1 == area2:
            analysis3()
        else:
            analysis4()
    
scatter_plot = Select(area1, area2)
scatter_plot.select_city()


