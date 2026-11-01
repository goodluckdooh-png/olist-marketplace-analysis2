import sqlite3, pandas as pd, os
U='data/'  # put the 8 Olist CSV files in a folder named data/
db='olist.db'
if os.path.exists(db): os.remove(db)
con=sqlite3.connect(db)
files={'orders':'olist_orders_dataset.csv','items':'olist_order_items_dataset.csv','payments':'olist_order_payments_dataset.csv',
'reviews':'olist_order_reviews_dataset.csv','products':'olist_products_dataset.csv','sellers':'olist_sellers_dataset.csv',
'customers':'olist_customers_dataset.csv','category_translation':'product_category_name_translation.csv'}
for t,f in files.items():
    df=pd.read_csv(U+f, encoding='utf-8-sig', dtype={'customer_zip_code_prefix':str,'seller_zip_code_prefix':str})
    df.to_sql(t,con,index=False)
    print(t, df.shape)
con.close()
