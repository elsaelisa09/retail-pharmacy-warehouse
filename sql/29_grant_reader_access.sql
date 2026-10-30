BEGIN;

GRANT CONNECT
ON DATABASE retail_pharmacy_dw
TO pharmacy_reader;

GRANT USAGE
ON SCHEMA marts
TO pharmacy_reader;

GRANT SELECT
ON ALL TABLES IN SCHEMA marts
TO pharmacy_reader;

ALTER DEFAULT PRIVILEGES
FOR ROLE postgres
IN SCHEMA marts
GRANT SELECT ON TABLES TO pharmacy_reader;

COMMIT;