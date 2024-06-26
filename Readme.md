# Health 365 Backend

------

This project has been created to fulfill the requirements of Health360 Company.
- **Credit**:  [Samrand Hassan](mailto:samrand96@gmail.com)
- **Date**: April 30th , 2024
- Job description has been mentioned in this file [Job](Job.md)
- Requirements of this project are mentioned in this file [Requirements](Requirements.md)

-----

## How To Run

1. Clone this project into your computer and go into it
```
git clone https://github.com/samrand96/health365.git && cd health365
```
2. Make sure to create a python virtual environment and  install the requirements of this project

```
python -m venv .venv
```
- For Mac & Linux
```
source /.venv/bin/activate
```
- For Windows (CMD)
```
./.venv/bin/activate.bat
```
- Then install the dependency of this project
```
pip install -r requirements.txt
```

3. Create Postgres Database
4. Edit .env file by adding the connection path of your postgresDB into the DB_URL
5. After finishing these setup basically you can run the command below to run the application
```
python -m uvicorn main:app --reload
```
-------
## System Architecture

![ER Diagram](extra/db.png?raw=true "The Entity Relation Diagram of The Database")


-------
