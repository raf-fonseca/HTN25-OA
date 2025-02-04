# HTN25-OA

This boilerplate contains a Flask + Graphene install with SQLite for GraphQL
endpoints. The current directory is mounted as a volume under `/home/api` so
that you do not have to rebuild the image every time. Building and running the
image will start the Flask server on port 3000.

assumption:

- this database will be used for when hackers apply as well

Good luck!

# To view data table

- docker exec -it api bash
- sqlite3 /db/hackers.db
- .mode column -- Makes output columnar (like Excel)
- .headers on -- Shows column headers
- .width AUTO -- Automatically adjusts column widths
- SELECT \* FROM hackers;
- SELECT \* FROM scans;
- SELECT \* FROM activities;
