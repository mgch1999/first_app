from tqdm import tqdm
import requests
import time
from  bs4 import BeautifulSoup
import pandas as pd
import urllib
import math
import re
import numpy as np
from google.cloud import storage as gcs
from google.oauth2 import service_account

def main():
    
    #api呼び出し
    key_path = ""
    credential = service_account.Credentials.from_service_account_file(key_path)
    project_id = ""
    client = gcs.Client(project_id, credentials=credential)
    bucket_name = ""
    gcs_path = ""
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    
    li =[]

    for g in tqdm(range(101, 124)):
        for i in tqdm(range(180)):
            try:
                base_url = f"https://suumo.jp/jj/chintai/ichiran/FR301FC005/?ar=030&bs=040&ta=13&sc=13{g}&cb=0.0&ct=9999999&mb=0&mt=9999999&md=04&et=9999999&cn=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&sngz=&po1=25&po2=99&pc=100&page={i}"
                html = requests.get(base_url)
                soup = BeautifulSoup(html.content, "html.parser")
                contents = soup.find_all("div", class_="property property--highlight js-property js-cassetLink")

                for content in contents:
                    title = content.find("a", class_="js-cassetLinkHref").text
                    a = content.find("a")
                    url = a.get("href")
                    link_url = urllib.parse.urljoin(base_url, url)
                    td_tag0 = content.find_all("td")[0]
                    price = td_tag0.find("div", class_="detailbox-property-point").text
                    td_tag2, td_tag3= content.find_all("td")[2:4]
                    size = td_tag2.find_all("div")[1].text
                    years = td_tag3.find_all("div")[1].text
                    address = content.find_all("td")[4].text.strip()
                    access_div = content.find(class_="detailnote-box")
                    access = access_div.find_all("div")[0].text
                    
                    dic = {"title":title,
                        "price":price,
                        "size":size,
                        "years":years,
                        "address":address,
                        "accesses":access,
                        "url":link_url}
                    
                    li.append(dic)
                    
                    time.sleep(1)

            except:
                pass

    df = pd.DataFrame(li)

    df["prices"] = df["price"].str.strip("万円").astype(float)
    df["yearss"] = df["years"].replace("新築", 0).str.strip("年").str.strip("築").str.strip("年以上").replace(float("NaN"), 0).astype(float)

    #クレンジング
    li = []
    for i in range(len(df)):
        li.append(df["size"][i][:-2])
    df["sizes"] = pd.Series(li)
    df["sizes"] = df["sizes"].astype(float)

    li2 = []
    for g in range(len(df)):
        li2.append(re.sub(r"\D", "", df["accesses"][g]))
    df["accesses"] = pd.Series(li2)
    df["accesses"] = df["accesses"].replace("", np.nan).astype(float)
    df["accesses"] = df["accesses"].fillna(math.floor(df["accesses"].mean()))

    li3 = []
    for h in range(len(df)):
        li3.append("分")
    df1 = pd.DataFrame(li3, columns=["ac"])
    df["access"] = df["accesses"].astype(int).astype(str)
    df["access"] = df["access"].str.cat(df1["ac"])

    df = df[df["prices"] < 50]
    df = df[df["sizes"]  < 100]
    df = df[df["accesses"] < 50]
    df = df[df["yearss"] < 75]

    #GCPにアップロード
    blob.upload_from_string(df.to_csv(index=False))

if __name__ == "__main__":
    main()