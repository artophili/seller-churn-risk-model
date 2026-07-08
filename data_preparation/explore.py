import pandas as pd
import numpy as np


orders = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_orders_dataset.csv")
sellers = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_sellers_dataset.csv")
order_items = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_items_dataset.csv")
reviews = pd.read_csv("C:/Users/Artophilic/Analysis Projects/seller-churn-risk-model/data/Raw/olist_order_reviews_dataset.csv")

print("Orders shape:", orders.shape)
print("Sellers shape:", sellers.shape)
print("Order items shape:", order_items.shape)
print("Reviews shape:", reviews.shape)

print("\nOrder date range:")
print(orders["order_purchase_timestamp"].min(), "to", orders["order_purchase_timestamp"].max())

print("\nOrders missing values:\n", orders.isna().sum())