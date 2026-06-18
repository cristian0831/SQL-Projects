# Context

With growing demands and cut-throat competitions in the market, a Superstore Giant is seeking your knowledge in understanding what works best for them. They would like to understand which products, regions, categories and customer segments they should target or avoid.

You can even take this a step further and try and build a Regression model to predict Sales or Profit.

Go crazy with the dataset, but also make sure to provide some business insights to improve.

# Dataset description

## Order and logistic

* RowID: unique row identifier.
* OrderID: Groups all items in one transaction. One order can have multiple rows (products).
* Order Date: When the customer placed the order.
* Ship Date: When the order was dispatched. Difference with Order Date = shipping days
* Ship Mode: 4 modes: Same Day, First Class, Second Class, Standard.

## Customer

* CustomerID: Unique per customer
* Customer Name: Label only 
* Segment: 3 types: Consumer, Corporate, Home Office.

## Geography

* Country, City/State, region, postal code

## Product

* ProductID: Unique per product SKU
* Category: 3 categories: Furniture, Office Supplies, Technology. 
* Sub-Category: 17 sub-categories (Tables, Chairs, Phones, Binders...).
* Product Name: Full name. 

## Finantials

* Sales: Revenue for that line item
* Quantity: Number of units sold.
* Discount: Discount rate applied (0 to 1).
* Profit: Net profit after cost and discount.

# Questions to answer

Is the business growing? 
Which type of customer is most profitable?
Which regions are profitable?


# Pipeline 

## Phase 1:
Load CSV into SQL inspect nulls, types, date ranges, enginer feature 

## Phase 2:
Business Performance

## Phase 3: 
Deep EDA

## Phase 4: 
Regression Model

## Phase 5: 
Insigths and recomendation

