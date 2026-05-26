-- find all accounts for a given customer
SELECT * FROM "account"
WHERE "customer_id" = (
    SELECT "id" FROM "customer"
    WHERE "username" = 'crist931'
);

-- find all the budgets for a given customer
SELECT * FROM "budgets"
WHERE "customer_id" = (
    SELECT "id" FROM "customer"
    WHERE "username" = 'crist931'
);

-- find all the loans for a given customer
SELECT * FROM "loans"
WHERE "customer_id" = (
    SELECT "id" FROM "customer"
    WHERE "username" = 'crist931'
);

-- find all the customers with credit account
SELECT * FROM "customer"
WHERE "id" IN (
    SELECT "customer_id" FROM "account"
    WHERE "account_type" = 'credit'
);

-- transaction history
SELECT * FROM "transactions"
WHERE "account_id" = 1
ORDER BY "transaction_date" DESC;

-- update balance for a deposit money
UPDATE "account"
SET "balance" = "balance" + 100
WHERE "id" = 1;

-- transfers between accounts
BEGIN TRANSACTION;
UPDATE "account" SET "balance" = "balance" - 100 WHERE "id" = 1 AND "balance" >= 100;
UPDATE "account" SET "balance" = "balance" + 100 WHERE "id" = 2;
INSERT INTO "transfers" ("from_account_id", "to_account_id", "amount", "status")
VALUES (1,2,100,'approved');
COMMIT;

-- simulate a failed transfer
BEGIN TRANSACTION;
UPDATE "account" SET "balance" = "balance" - 10000 WHERE "id" = 1 AND "balance" >= 10000;
ROLLBACK;

-- customers with the higher number of loans
SELECT "customer"."username", COUNT("loans"."id") AS "total_loans" FROM "customer"
JOIN "loans" ON "loans"."customer_id" = "customer"."id"
GROUP BY "customer"."id", "customer"."username"
ORDER BY "total_loans" DESC;

-- add a new customer
INSERT INTO "customer" ("id", "first_name", "last_name", "username", "password", "email")
VALUES (1, 'Christian', 'Macias', 'crist931', 'RiFeynman5', 'cristianfma3108@gmail.com' );

-- add the account for that customer
INSERT INTO "account" ("id", "customer_id", "balance", "account_type", "account_number")
VALUES (1, 1, 0, 'credit', '10AS90');
