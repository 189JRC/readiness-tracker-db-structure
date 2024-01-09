# readiness-tracker-db-structure

1) Create venv and activate
2) Install requirements.txt
3) Create .env in top level directory and copy template.env to it
4) Create a db schema in MySQL workbench
4) Adjust db variables in .env to reference your local MySQL db schema
5) Run flask db upgrade to create tables
6) Run db_script.py to populate tables with dummy data