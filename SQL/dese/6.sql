SELECT "name" FROM "schools"
WHERE "id" IN (
    SELECT "school_id" FROM "graduation_rates"
    WHERE "graduated" = 100
);
-- Expected multiple school_id with several students graduated on time
