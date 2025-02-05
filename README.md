# HTN25-OA

This boilerplate contains a Flask + Graphene install with SQLite for GraphQL
endpoints. The current directory is mounted as a volume under `/home/api` so
that you do not have to rebuild the image every time. Building and running the
image will start the Flask server on port 3000.

assumption:

- this database will be used for when hackers apply as well

Good luck!



sqlite3 /db/hackers.db

-- Then try these commands:

.mode column   -- Makes output columnar (like Excel)
.headers on    -- Shows column headers
.width AUTO    -- Automatically adjusts column widths

-- Now you can run your queries and they'll be nicely formatted:
SELECT * FROM hackers;

-- Other useful commands:
.tables        -- Lists all tables in the database
.schema       -- Shows the CREATE statements for all tables
.mode box   