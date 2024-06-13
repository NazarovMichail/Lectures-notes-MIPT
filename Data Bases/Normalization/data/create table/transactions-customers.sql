CREATE TABLE "transactions" (
  "transaction_id" integer PRIMARY KEY,
  "product_id" integer,
  "brand" varchar,
  "customer_id" integer,
  "transaction_date" timestamp,
  "online_order" boolean,
  "order_status" varchar
);

CREATE TABLE "customers" (
  "customer_id" integer PRIMARY KEY,
  "first_name" varchar,
  "last_name" varchar,
  "gender" varchar,
  "DOB" timestamp,
  "job_title" varchar,
  "job_industry_category" varchar,
  "wealth_segment" varchar,
  "deceased_indicator" varchar,
  "owns_car" varchar,
  "property_valuation" integer,
  "postcode" integer
);

CREATE TABLE "address" (
  "postecode" integer PRIMARY KEY,
  "addres" varchar,
  "state" text,
  "country" varchar
);

CREATE TABLE "products" (
  "product_id" integer PRIMARY KEY,
  "brand" varchar,
  "product_line" varchar,
  "product_class" varchar,
  "product_size" varchar,
  "list_price" float,
  "standard_cost" float
);

ALTER TABLE "customers" ADD FOREIGN KEY ("postcode") REFERENCES "address" ("postecode");

ALTER TABLE "transactions" ADD FOREIGN KEY ("customer_id") REFERENCES "customers" ("customer_id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("product_id");
