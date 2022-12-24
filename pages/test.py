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
variable = ["家賃(万円)", "面積(m2)", "築年数", "アクセス(分)"]
colors = ["lightcoral", "darkorange", "gold", "lightgreen", "mediumturquoise", "dodgerblue", "mediumblue", "mediumorchid", "mediumvioletred"]

area1 = st.sidebar.selectbox("エリア選択", ward1)
area2 = st.sidebar.selectbox("比較エリア選択", ward2)
madori = st.sidebar.selectbox("間取りタイプ",  ("ワンルーム", "1K", "1LDK"))
hennsuu = st.sidebar.selectbox("変数選択", variable)

bins_price = np.arange(0, 30, 3)
bins_size_1ldk = np.arange(10, 110, 10)
bins_size = np.arange(10, 40, 3)
bins_years = np.arange(0, 50, 5)
bins_access = np.arange(0, 20, 2)
label_price = ["3万円以下", "3~6万円", "6~9万円", "9~12万円", "12~15万円", "15~18万円", "18~21万円", "21~24万円" , "24万円以上"]
label_size = ["10~13m2", "13~16m2", "16~19m2", "19~22m2", "22~25m2", "25~28m2", "28~31m2", "31~34m2", "34m2以上"]
label_size_1ldk = ["10~20m2", "20~30m2", "30~40m2", "40~50m2", "50~60m2", "60~70m2", "70~80m2", "80~90m2", "90m2以上"]
label_years = ["5年以下", "5~10年", "10~15年", "15~20年", "20~25年", "25~30年", "30~35年", "35~40年", "40年以上"]
label_access = ["2分以下", "2~4分", "4~6分", "6~8分", "8~10分", "10~12分", "12~14分", "14~16分" ,"16分以上"]

if madori =="ワンルーム":
    madori = "tokyo_1r"
elif madori == "1K":
    madori = "tokyo_1k"
else:
    madori = "tokyo_1ldk"

if hennsuu == "面積(m2)":
    hennsuu1, bins, label = "sizes", bins_size, label_size
elif hennsuu == "築年数":
    hennsuu1, bins, label = "yearss", bins_years, label_years
elif hennsuu == "アクセス(分)":
    hennsuu1, bins, label = "accesses", bins_access, label_access
else:
    hennsuu1, bins, label = "prices", bins_price, label_price

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

df_ward1 = df[df["ku"] == area1]
df_ward2 = df[df["ku"] == area2]

def bar():
    avg = pd.pivot_table(df, index="ku", values=hennsuu1)
    avg = avg.sort_values(hennsuu1, ascending=False)
    fig, ax = plt.subplots()
    plt.title(f"平均{hennsuu}")
    if area1 == "全体" and area2 == "指定なし":
        bar_list = ax.bar(avg.index, height=avg[hennsuu1], color="dodgerblue")
        plt.xticks(rotation=90)
        st.pyplot(fig)
    elif area1 == "全体" and area2 != "指定なし" or area1 == area2:
        bar_list = ax.bar(avg.index, height=avg[hennsuu1], color="lightgray")
        ai = avg.index
        for i in range(len(avg)):
            if ai[i] == area2:
                bar_list[i].set_color("dodgerblue")
        plt.xticks(rotation=90)
        st.pyplot(fig)
    elif area1 != "全体" and area2 != "指定なし":
        bar_list = ax.bar(avg.index, height=avg[hennsuu1], color="lightgray")
        ai = avg.index
        for i in range(len(avg)):
            if ai[i] == area1:
                bar_list[i].set_color("dodgerblue")
            elif ai[i] == area2:
                bar_list[i].set_color("orange")
        plt.xticks(rotation=90)
        st.pyplot(fig)
    else:
        bar_list = ax.bar(avg.index, height=avg[hennsuu1], color="lightgray")
        ai = avg.index
        for i in range(len(avg)):
            if ai[i] == area1:
                bar_list[i].set_color("dodgerblue")
        plt.xticks(rotation=90)
        st.pyplot(fig)

def scatter():
    fig, ax = plt.subplots()
    plt.title("散布図")
    if area1 == "全体" and area2 == "指定なし":
        ax.scatter(df[hennsuu1], df["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
        plt.xlabel(hennsuu)
        plt.ylabel("家賃")
        plt.legend()
        st.pyplot(fig)
    elif area1 == "全体" and area2 != "指定なし":
        ax.scatter(df[hennsuu1], df["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
        ax.scatter(df_ward2[hennsuu1], df_ward2["prices"], alpha=0.4, color="orange",s=10, label=area2)
        plt.xlabel(hennsuu)
        plt.ylabel("家賃")
        plt.legend()
        st.pyplot(fig)
    elif area1 != "全体" and area2 == "指定なし" or area1 == area2:
        ax.scatter(df_ward1[hennsuu1], df_ward1["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
        plt.xlabel(hennsuu)
        plt.ylabel("家賃")
        plt.legend()
        st.pyplot(fig)
    else:
        ax.scatter(df_ward1[hennsuu1], df_ward1["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
        ax.scatter(df_ward2[hennsuu1], df_ward2["prices"], alpha=0.4, color="orange",s=10, label=area2)
        plt.xlabel(hennsuu)
        plt.ylabel("家賃")
        plt.legend()
        st.pyplot(fig)

def hist():
    fig, ax = plt.subplots()
    plt.title("ヒストグラム")
    if area1 == "全体" and area2 == "指定なし":
        ymin, ymax = 0, 50000
        ax.hist(df[hennsuu1],alpha=0.4, color="dodgerblue", bins=100, label=area1)
        plt.vlines(df_ward1[hennsuu1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
        plt.xlabel(hennsuu)
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)
    elif area1 == "全体" and area2 != "指定なし":
        ymin, ymax = 0, 50000
        ax.hist(df[hennsuu1],alpha=0.4, color="dodgerblue", bins=100, label=area1)
        ax.hist(df_ward2[hennsuu1],alpha=0.4, color="orange", bins=100, label=area2)
        plt.vlines(df[hennsuu1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
        plt.vlines(df_ward2[hennsuu1].mean(), ymin, ymax, color="orange", linestyle='dashed', linewidth=1)
        plt.xlabel(hennsuu)
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)
    elif area1 != "全体" and area2 == "指定なし" or area1 == area2:
        ymin, ymax = 0, 1500
        ax.hist(df_ward1[hennsuu1],alpha=0.4, color="dodgerblue", bins=100, label=area1)
        plt.vlines(df_ward1[hennsuu1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
        plt.xlabel(hennsuu)
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)
    else:
        ymin, ymax = 0, 1500
        ax.hist(df_ward1[hennsuu1],alpha=0.4, color="dodgerblue", bins=100, label=area1)
        ax.hist(df_ward2[hennsuu1],alpha=0.4, color="orange", bins=100, label=area2)
        plt.vlines(df_ward1[hennsuu1].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1)
        plt.vlines(df_ward2[hennsuu1].mean(), ymin, ymax, color="orange", linestyle='dashed', linewidth=1)
        plt.xlabel(hennsuu)
        plt.ylabel("物件数")
        plt.legend()
        st.pyplot(fig)
class Ratio:
    def __init__(self, bins, label):
        self.bins = bins 
        self.label = label

    def ratio1(self):
        freq = pd.DataFrame({f"{area1}":df[hennsuu1].value_counts(bins = self.bins, sort=False)})
        freq[area1] = freq[area1]/freq[area1].sum()
        fig, ax = plt.subplots()
        left_data = pd.Series(np.zeros(len(freq.columns)), index=freq.columns.tolist())
        for i in range(len(freq.index)):
            bar_list = ax.barh(freq.columns, freq.iloc[i], color=colors[i], left=left_data, height=0.5)
            left_data += freq.iloc[i]
        ax.legend(self.label, loc='upper left', bbox_to_anchor=(1, 1))
        plt.xlim([0, 1])
        st.pyplot(fig)
    
    def ratio2(self):
        freq = pd.DataFrame({f"{area2}":df_ward2[hennsuu1].value_counts(bins = self.bins, sort=False),
                             f"{area1}":df[hennsuu1].value_counts(bins = self.bins, sort=False)})
        freq[area1], freq[area2] = freq[area1]/freq[area1].sum(), freq[area2]/freq[area2].sum()
        fig, ax = plt.subplots()
        left_data = pd.Series(np.zeros(len(freq.columns)), index=freq.columns.tolist())
        for i in range(len(freq.index)):
            bar_list = ax.barh(freq.columns, freq.iloc[i], color=colors[i], left=left_data, height=0.5)
            left_data += freq.iloc[i]
        ax.legend(self.label, loc='upper left', bbox_to_anchor=(1, 1))
        plt.xlim([0, 1])
        st.pyplot(fig)

    def ratio3(self):
        freq = pd.DataFrame({f"{area1}":df_ward1[hennsuu1].value_counts(bins = self.bins, sort=False)})
        freq[area1] = freq[area1]/freq[area1].sum()
        fig, ax = plt.subplots()
        left_data = pd.Series(np.zeros(len(freq.columns)), index=freq.columns.tolist())
        for i in range(len(freq.index)):
            bar_list = ax.barh(freq.columns, freq.iloc[i], color=colors[i], left=left_data, height=0.5)
            left_data += freq.iloc[i]
        ax.legend(self.label, loc='upper left', bbox_to_anchor=(1, 1))
        plt.xlim([0, 1])
        st.pyplot(fig)
    
    def ratio4(self):
        freq = pd.DataFrame({f"{area2}":df_ward2[hennsuu1].value_counts(bins = self.bins, sort=False),
                             f"{area1}":df_ward1[hennsuu1].value_counts(bins = self.bins, sort=False)})
        freq[area1], freq[area2] = freq[area1]/freq[area1].sum(), freq[area2]/freq[area2].sum()
        fig, ax = plt.subplots()
        left_data = pd.Series(np.zeros(len(freq.columns)), index=freq.columns.tolist())
        for i in range(len(freq.index)):
            bar_list = ax.barh(freq.columns, freq.iloc[i], color=colors[i], left=left_data, height=0.5)
            left_data += freq.iloc[i]
        ax.legend(self.label, loc='upper left', bbox_to_anchor=(1, 1))
        plt.xlim([0, 1])
        st.pyplot(fig)

def ratio():
    ana = Ratio(bins, label)
    if area1 == "全体" and area2 == "指定なし":
        ana.ratio1()
    elif area1 == "全体" and area2 != "指定なし":
        ana.ratio2()
    elif area1 != "全体" and area2 == "指定なし" or area1 == area2: 
        ana.ratio3
    else:
        ana.ratio4

ratio()



   
    
#     table = pd.DataFrame({area1:[df_ward1["prices"].mean(), df_ward1["sizes"].mean(), df_ward1["yearss"].mean(), df_ward1["accesses"].mean()],
#                           area2:[df_ward2["prices"].mean(), df_ward2["sizes"].mean(), df_ward2["yearss"].mean(), df_ward2["accesses"].mean()]},
#                           index=["平均家賃(万円)", "面積(m2)", "築年数", "アクセス(分)"])
#     st.table(table.style.format('{:.1f}'))




   
# class Select():
#     def __init__(self, area1, area2):
#         self.area1 = area1
#         self.area2 = area2

#     def select_city(self): 
#         if self.area1 == "全体" and self.area2 == "指定なし":
#             analysis1()
#         elif area1 == "全体" and area2 != "指定なし":
#             analysis2()
#         elif area1 != "全体" and area2 == "指定なし":
#             analysis3()
#         elif area1 == area2:
#             analysis3()
#         else:
#             analysis4()
    
# scatter_plot = Select(area1, area2)
# scatter_plot.select_city()

