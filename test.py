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


ward = ("千代田区", "中央区", "港区", "新宿区", "文京区", "台東区", "墨田区", "江東区", "品川区", "目黒区", "大田区", "世田谷区", "渋谷区", "中野区", "杉並区",
                                      "豊島区", "北区", "荒川区", "板橋区", "練馬区", "足立区", "葛飾区", "江戸川区")

ymin, ymax = 0, 1500

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
    `prediction-rent-price.dataset1.tokyo_1k`
)
SELECT
ku, avg(prices)
FROM
data_with_ku
GROUP BY 
ku;"""
         
data = client.query(query).to_dataframe()
df = pd.DataFrame(data)
df = df.sort_values("f0_", ascending=False)
st.dataframe(df)
fig, ax = plt.subplots()
ax.bar(df["ku"], height=df["f0_"])
plt.xticks(rotation=90)
st.pyplot(fig)




# area1 = st.selectbox("エリア選択", ward)
# area2 = st.selectbox("比較エリア選択", ward)
# madori = st.selectbox("間取りタイプ",  ("ワンルーム", "1K", "1LDK"))


# def scatter(madori):

#     if area1 == area2:
#         query = f"""
#         WITH data_with_ku AS (
#         SELECT
#         *,
#         CASE 
#             WHEN address LIKE '%{area1}%' THEN '{area1}' 
#         END AS ku
#         FROM
#             `prediction-rent-price.dataset1.{madori}`
#         )
#         SELECT
#         *
#         FROM
#         data_with_ku;"""

#         data = client.query(query).to_dataframe()
#         df = pd.DataFrame(data)
#         df1 = df.loc[(df["ku"]==area1)]
        
#         fig, ax = plt.subplots()
#         ax.scatter(df1["sizes"], df1["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
#         plt.xlabel("面積(m2)")
#         plt.ylabel("家賃(万円)")
#         plt.legend()
#         st.pyplot(fig)
        
#     else:
#         query = f"""
#         WITH data_with_ku AS (
#         SELECT
#         *,
#         CASE 
#             WHEN address LIKE '%{area1}%' THEN '{area1}' 
#             WHEN address LIKE '%{area2}%' THEN '{area2}'
#         END AS ku
#         FROM
#             `prediction-rent-price.dataset1.{madori}`
#         )
#         SELECT
#         *
#         FROM
#         data_with_ku;"""

#         data = client.query(query).to_dataframe()
#         df = pd.DataFrame(data)
#         df1 = df.loc[(df["ku"]==area1)]
#         df2 = df.loc[(df["ku"]==area2)]

#         fig, ax = plt.subplots()
#         ax.scatter(df1["sizes"], df1["prices"], alpha=0.4, color="dodgerblue",s=10, label=area1)
#         ax.scatter(df2["sizes"], df2["prices"], alpha=0.1, color="orange",s=10, label=area2)
#         plt.xlabel("面積(m2)")
#         plt.ylabel("家賃(万円)")
#         plt.legend()
#         st.pyplot(fig)
# class Select():
#     def __init__(self, area1, area2, madori):
#         self.area1 = area1
#         self.area2 = area2
#         self.madori = madori

#     def select_scatter(self): 
#         if self.area1 == area2:
#             self.area1 = area1 
#             self.area2 = area2  
#             if self.madori == "ワンルーム":
#                 scatter("tokyo_1r")
#             elif self.madori == "1K":
#                 scatter("tokyo_1k")
#             else:
#                 scatter("tokyo_1ldk")
#         else:
#             self.area1 = area1
#             if self.madori == "ワンルーム":
#                 scatter("tokyo_1r")
#             elif self.madori == "1K":
#                 scatter("tokyo_1k")
#             else:
#                 scatter("tokyo_1ldk")

# scatter_plot = Select(area1, area2, madori)
# scatter_plot.select_scatter()

# fig, ax = plt.subplots()
# plt.hist(df1["prices"],alpha=0.3, bins=50, color="dodgerblue", label=area1)
# plt.vlines(df1["prices"].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1, label=f"平均家賃({area1})")
# plt.xlabel("家賃(万円)")
# plt.ylabel("物件数")
# plt.legend()
# st.pyplot(fig)

# fig, ax = plt.subplots()
# plt.boxplot(df["prices"])
# st.pyplot(fig)



# fig, ax = plt.subplots()
# plt.hist(df1["prices"],alpha=0.4, color="dodgerblue", bins=50, label=area1)
# plt.hist(df2["prices"],alpha=0.3, color="orange", bins=50, label=area2)
# plt.vlines(df1["prices"].mean(), ymin, ymax, color="dodgerblue", linestyle='dashed', linewidth=1, label=f"平均家賃({area1})")
# plt.vlines(df2["prices"].mean(), ymin, ymax, color="orange", linestyle='dashed', linewidth=1, label=f"平均家賃({area2})" )
# plt.xlabel("家賃(万円)")
# plt.ylabel("物件数")
# plt.legend()
# st.pyplot(fig)

