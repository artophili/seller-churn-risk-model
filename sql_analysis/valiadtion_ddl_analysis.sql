CREATE TABLE orders (
    order_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50),
    order_status VARCHAR(20),
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP
);

CREATE TABLE order_items (
    order_id VARCHAR(50),
    order_item_id INT,
    product_id VARCHAR(50),
    seller_id VARCHAR(50),
    shipping_limit_date TIMESTAMP,
    price DECIMAL(10,2),
    freight_value DECIMAL(10,2)
);



WITH order_seller_pairs AS (
    SELECT DISTINCT oi.order_id, oi.seller_id, o.order_purchase_timestamp
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
),
baseline AS (
    SELECT seller_id, COUNT(*) AS order_count
    FROM order_seller_pairs
    WHERE order_purchase_timestamp >= '2017-04-01'
      AND order_purchase_timestamp < '2018-01-01'
    GROUP BY seller_id
)
SELECT
    COUNT(*) AS unique_sellers,
    ROUND(AVG(order_count), 2) AS mean_orders,
    MIN(order_count) AS min_orders,
    MAX(order_count) AS max_orders
FROM baseline;

--Validating the discrepancy in the seller count
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM order_items;

SELECT order_id, COUNT(*) FROM orders GROUP BY order_id HAVING COUNT(*) > 1;

SELECT COUNT(DISTINCT seller_id) FROM order_items;
SELECT COUNT(DISTINCT TRIM(seller_id)) FROM order_items;

--Checking the baseline order count
SELECT COUNT(*) FROM orders
WHERE order_purchase_timestamp >= '2017-04-01'
  AND order_purchase_timestamp < '2018-01-01';