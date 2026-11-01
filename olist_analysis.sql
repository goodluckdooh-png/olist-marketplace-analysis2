-- Olist Marketplace Performance & Delivery Analysis (SQLite)
-- Scope: delivered orders with a delivery date (96,470 orders). Revenue = item price, excluding freight.

-- 1. Order-level fact table (one row per order)
DROP TABLE IF EXISTS order_fact;
CREATE TABLE order_fact AS
WITH rev AS (
  SELECT order_id, COUNT(*) AS n_items, SUM(price) AS item_revenue, SUM(freight_value) AS freight
  FROM items GROUP BY order_id
),
rv AS (  -- 551 orders have more than one review, so average to one score per order
  SELECT order_id, AVG(review_score) AS review_score FROM reviews GROUP BY order_id
)
SELECT o.order_id, c.customer_unique_id, c.customer_state,
       o.order_purchase_timestamp AS purchase_ts,
       substr(o.order_purchase_timestamp,1,7) AS purchase_month,
       r.n_items, r.item_revenue, r.freight, rv.review_score,
       julianday(o.order_delivered_customer_date) - julianday(o.order_purchase_timestamp) AS delivery_days,
       julianday(o.order_delivered_customer_date) - julianday(o.order_estimated_delivery_date) AS delay_days
FROM orders o
JOIN customers c USING(customer_id)
JOIN rev r USING(order_id)
LEFT JOIN rv USING(order_id)
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL;

-- 2. Item-level fact table (one row per item, for category and seller analysis and Power BI)
DROP TABLE IF EXISTS items_fact;
CREATE TABLE items_fact AS
SELECT i.order_id, i.order_item_id, f.purchase_month, f.customer_state,
       COALESCE(t.product_category_name_english, 'unknown') AS category,
       i.seller_id, s.seller_state, i.price, i.freight_value,
       f.review_score, f.delivery_days, f.delay_days,
       CASE WHEN f.delay_days > 0 THEN 1 ELSE 0 END AS is_late
FROM items i
JOIN order_fact f USING(order_id)
JOIN products p USING(product_id)
LEFT JOIN category_translation t USING(product_category_name)
JOIN sellers s USING(seller_id);

-- 3. Monthly trend (Jan 2017 to Aug 2018, earlier and later months are incomplete)
SELECT purchase_month, COUNT(*) AS orders, ROUND(SUM(item_revenue),0) AS revenue,
       ROUND(AVG(item_revenue),2) AS avg_order_value, ROUND(AVG(review_score),2) AS avg_review,
       ROUND(100.0*AVG(CASE WHEN delay_days>0 THEN 1.0 ELSE 0 END),1) AS pct_late
FROM order_fact WHERE purchase_month BETWEEN '2017-01' AND '2018-08'
GROUP BY 1 ORDER BY 1;

-- 4. Top categories by revenue
SELECT category, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(price),0) AS revenue,
       ROUND(AVG(review_score),2) AS avg_review
FROM items_fact GROUP BY 1 ORDER BY revenue DESC LIMIT 12;

-- 5. Customer state: revenue, delivery speed, satisfaction
SELECT customer_state, COUNT(*) AS orders, ROUND(SUM(item_revenue),0) AS revenue,
       ROUND(AVG(delivery_days),1) AS avg_delivery_days, ROUND(AVG(review_score),2) AS avg_review
FROM order_fact GROUP BY 1 ORDER BY revenue DESC;

-- 6. Delivery delay vs review score
SELECT CASE WHEN delay_days<=-7 THEN '1. 7+ days early'
            WHEN delay_days<=0  THEN '2. On time (0-7 days early)'
            WHEN delay_days<=3  THEN '3. 1-3 days late'
            WHEN delay_days<=7  THEN '4. 4-7 days late'
            ELSE '5. 8+ days late' END AS delivery_bucket,
       COUNT(*) AS orders, ROUND(AVG(review_score),2) AS avg_review,
       ROUND(100.0*AVG(CASE WHEN review_score<=2 THEN 1.0 ELSE 0 END),1) AS pct_low_reviews
FROM order_fact WHERE review_score IS NOT NULL GROUP BY 1 ORDER BY 1;

-- 7. Seller performance and concentration
SELECT seller_id, seller_state, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(price),0) AS revenue,
       ROUND(AVG(review_score),2) AS avg_review
FROM items_fact GROUP BY 1,2 ORDER BY revenue DESC;

-- 8. Repeat customers
SELECT COUNT(*) AS customers, SUM(n>1) AS repeat_customers, ROUND(100.0*SUM(n>1)/COUNT(*),2) AS pct_repeat
FROM (SELECT customer_unique_id, COUNT(*) AS n FROM order_fact GROUP BY 1);
