-- customer table
CREATE TABLE "customer" (
    "id" INTEGER NOT NULL,
    "first_name" TEXT NOT NULL,
    "last_name" TEXT,
    "username" TEXT NOT NULL UNIQUE,
    "password" TEXT NOT NULL,
    "started" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "email" TEXT UNIQUE,
    PRIMARY KEY("id")
);
--  create budget table
CREATE TABLE "budgets" (
    "id" INTEGER,
    "customer_id" INTEGER,
    "budget_name" TEXT NOT NULL,
    "limit_amount" DECIMAL(15,2) NOT NULL CHECK ("limit_amount" >= 0),
    "current_amount" NUMERIC NOT NULL,
    "start_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY("id"),
    FOREIGN KEY("customer_id") REFERENCES "customer"("id")
);
-- loan table
CREATE TABLE "loans" (
    "id" INTEGER,
    "customer_id" INTEGER,
    "loan_name" TEXT NOT NULL,
    "interest_rate" NUMERIC NOT NULL CHECK("interest_rate" BETWEEN 0 AND 1),
    "loan_amount" DECIMAL(15,2) NOT NULL CHECK ("loan_amount" >= 0),
    "current_balance" NUMERIC NOT NULL,
    PRIMARY KEY("id"),
    FOREIGN KEY("customer_id") REFERENCES "customer"("id")
);
-- account table
CREATE TABLE "account" (
    "id" INTEGER NOT NULL,
    "customer_id" INTEGER,
    "balance" DECIMAL(15,2) NOT NULL CHECK ("balance" >= 0),
    "account_type" TEXT CHECK ("account_type" IN ('checking', 'savings', 'credit')),
    "account_number" TEXT NOT NULL UNIQUE,
    PRIMARY KEY("id"),
    FOREIGN KEY("customer_id") REFERENCES "customer"("id")
);
-- transaction table
CREATE TABLE "transactions" (
    "id" INTEGER,
    "account_id" INTEGER,
    "transaction_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "transaction_type" TEXT CHECK ("transaction_type" IN ('deposits', 'withdrawals', 'transfers')),
    "amount" DECIMAL(15,2) NOT NULL CHECK ("amount" > 0),
    "status" TEXT CHECK ("status" IN ('pending', 'approved')),
    PRIMARY KEY("id"),
    FOREIGN KEY("account_id") REFERENCES "account"("id")
);
-- transfers table
CREATE TABLE "transfers" (
    "id" INTEGER,
    "from_account_id" INTEGER,
    "to_account_id" INTEGER,
    "amount" DECIMAL(15,2) NOT NULL CHECK ("amount" > 0),
    "transfers_date" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "status" TEXT CHECK ("status" IN ('pending', 'approved')),
    PRIMARY KEY("id"),
    FOREIGN KEY ("from_account_id") REFERENCES "account"("id"),
    FOREIGN KEY ("to_account_id") REFERENCES "account"("id")
);

-- create indexes
CREATE INDEX "user_index" ON "customer"("username");
CREATE INDEX "balance_index" ON "account"("balance");
CREATE INDEX "account_number_index" ON "account"("account_number");
CREATE INDEX "amount_index" ON "transactions"("amount");
CREATE INDEX "transfer_status_index" ON "transfers"("status");

-- create views

-- pending transfers information
CREATE VIEW "pending_transfers" AS
SELECT "from_account_id", "to_account_id", "amount", "transfers_date" FROM "transfers"
WHERE "status" = 'pending';

-- account information for a customer
CREATE VIEW "customer_account_info" AS
SELECT "id"."customer", "first_name"."customer", "last_name"."customer", "balance"."account", "account_number"."account"
FROM "customer"
JOIN "account" ON "account"."customer_id" = "customer"."id";

-- customer loan info
CREATE VIEW "customer_loan_info" AS
SELECT "id"."customer", "first_name"."customer", "last_name"."customer", COUNT("id"."loans") AS "total_loans"
FROM "customer"
JOIN "loans" ON "loans"."customer_id" = "customer"."id";
