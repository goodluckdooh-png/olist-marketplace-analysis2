# Olist Marketplace Performance and Delivery Analysis

**Tools:** SQL (SQLite), Python (pandas, SciPy, Matplotlib), Excel, Power BI
**Data:** [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (8 tables, about 100k orders, 2016 to 2018)

## Business question
Olist is an online marketplace that connects sellers with customers. Which factors drive revenue growth and customer satisfaction, and where is the marketplace losing customers?

## Approach
1. **SQL:** loaded 8 tables into SQLite, checked data quality, and built two analysis tables: one row per order (`order_fact`) and one row per item (`items_fact`). Only delivered orders with a delivery date were kept (96,470 orders). Orders with several reviews were averaged to one score (551 orders).
2. **Python:** ran the analysis, a Spearman correlation and a Mann-Whitney test, and made the charts.
3. **Excel:** a summary workbook with formulas (growth rates, shares, weighted averages, seller concentration).
4. **Power BI:** dashboard built from the cleaned CSVs (steps below).

Revenue means item price and excludes freight. The trend covers Jan 2017 to Aug 2018, because the months before and after are incomplete.

## Key findings
1. **Fast growth.** Revenue for Jan to Aug 2018 was R$7.22M against R$2.99M a year earlier (+141%), and orders grew 140%. Nov 2017 (Black Friday) revenue was 52% above October.
2. **Late delivery is the biggest satisfaction problem.** 8% of reviewed orders arrived after the estimated date. They averaged a **2.57** review score, against **4.29** for on-time orders. 54% of late orders got a 1 or 2 star review, against 9% of on-time orders. Orders 4 to 7 days late got low reviews 61% of the time, and 8+ days late 78% of the time. The correlation is statistically significant (Spearman rho = -0.18, p < 0.001, n = 95,824).
3. **Peak periods break delivery.** The late rate jumped from a 3 to 5% baseline to 14.3% in Nov 2017, 16.0% in Feb 2018 and 21.4% in Mar 2018. Average review scores fell from about 4.2 to 3.99, 3.88 and 3.81 in the same months, then recovered.
4. **Revenue is concentrated by geography.** Sao Paulo (SP) is 38.3% of revenue and the top 3 states (SP, RJ, MG) are 63.4%. Delivery takes 8.8 days on average in SP but 26 to 29 days in AM, AP and RR.
5. **A few sellers drive most sales.** The top 10% of sellers (297 of 2,970) generate 67.1% of revenue, and the top 20% generate 82.3%. Some large sellers perform badly: one seller with 108 orders averages 2.27 stars.
6. **Categories.** Health and beauty (R$1.23M), watches and gifts (R$1.17M) and bed, bath and table (R$1.02M) lead on revenue. Bed, bath and table has the most orders (9,272) but one of the lower review scores (3.92).
7. **Low retention.** Only 3.0% of customers (2,801 of 93,350) ordered more than once.
8. **Payments.** Credit card is the most used payment type (74,297 orders, 3.5 installments on average), then boleto bank slips (19,191 orders).

## Recommendations
- Plan delivery capacity before peak periods such as Black Friday, since late rates more than doubled in peak months.
- Show more realistic delivery estimates and send proactive delay alerts, because the review damage starts at 4+ days late.
- Set delivery and review targets for large sellers and review the ones with low scores.
- Add retention actions such as post-delivery follow-ups or coupons, since 97% of customers never reorder.

## Limitations
- Correlation is not proof of cause. Late orders may also differ in product type or region.
- 74% of orders arrive 7+ days before the estimated date, so the estimates look padded and "on time" is generous.
- Only customers who left a review are counted in the review analysis.


