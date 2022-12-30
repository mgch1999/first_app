## 東京23区賃貸分析アプリ

このアプリは23区内の賃貸の家賃予測と賃貸データ分析・可視化ができます。  
URL:https://mgch1999-first-app-prediction-iau5bs.streamlit.app/analysis

## 概要

1ページ目で家賃予測、2ページ目でデータ分析という構成になっています。   

![](https://user-images.githubusercontent.com/111175040/209550504-a05fb185-377b-459a-987a-a6ca7cfce9c4.png)  

![](https://user-images.githubusercontent.com/111175040/209551168-f592d52b-ff6b-4963-8941-ef706f6c8fa3.png)

## 技術的特徴

* データ収集  
仮想環境上で2週間に1回、物件サイトsuumoからデータを収集するファイルを定期実行  
データをGCPのgoogle cloud storageに保管

* データ抽出  
組み込みSQLでクエリ実行しbig queryからデータ抽出

* 家賃予測  
面積・築年数・駅からのアクセス時間を独立変数、家賃を従属変数とし、ランダムフォレストで予測 

## 使用言語

python3  
SQL

## 注意点

スクレイピングファイル(tokyo_rent_scrap.py)はセキュリティの関係上APIキーなどを消してあります。

## 製作者

澤谷景成  
mail:beatlove303@gmail.com

## 使用サイト

物件サイトsuumo  
URL:https://suumo.jp/






