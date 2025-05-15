
# Backend Engineer

## Intro

This assignment is designed to give you an opportunity to showcase your problem-solving skills, technical expertise, and ability to work with Python, Airflow, FastAPI, and databases.



# Assignment Overview

At OpenTax, we process a large volume of tax-related financial transactions. To streamline our workflows, we need a data pipeline to process transactions, a FastAPI service to expose insights, and optimized database queries for performance.

**Your tasks are to:**

1. Extract, Transform, and Load (ETL) financial transaction data using Airflow.  
2. Build a FastAPI service to expose processed data.  
3. Explain how to optimize database queries to improve performance.

## Task A: ETL Pipeline using Apache Airflow

You need to create an Airflow DAG that automates the ETL process for financial transactions.



**Steps:**

1. Extract: Load the transactions from the CSV file into a Pandas DataFrame.  
2. Transform:  
   1. Convert amounts to float.  
   2. Normalize date formats to YYYY-MM-DD.  
   3. Remove duplicate transactions.  
3. Load: Insert the cleaned transactions into a PostgreSQL table (transactions).

Schema for Transactions Table

```
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    transaction_id VARCHAR(50) UNIQUE NOT NULL,
    user_id INT NOT NULL,
    amount FLOAT NOT NULL,
    transaction_date DATE NOT NULL
);
```

**Requirements:**

* The DAG should run daily at midnight.  
* Store logs and metadata in PostgreSQL for auditing.

## Task B: FastAPI Service

You need to build a FastAPI service that exposes transaction data via an API.

**Endpoint:**

* GET /transactions/{user\_id}/summary

**Response:**  
For a given user\_id, return:

* total\_transactions (number of transactions)  
* total\_amount (sum of all transactions)  
* average\_transaction\_amount

**Example Response**

```
{
  "user_id": 123,
  "total_transactions": 50,
  "total_amount": 10240.50,
  "average_transaction_amount": 204.81
}
```

**Requirements:**

* Use SQLAlchemy to interact with PostgreSQL.  
* Ensure proper error handling (e.g., return 404 if no transactions exist for the user).  
* API should be asynchronous (async/await) for efficiency.

## Task C: Database Query Optimization

Explain any performance considerations for handling large datasets.

docker-compose down
docker-compose up -d

sudo chmod -R 777 ./logs

docker exec -it <postgres_container_name_or_id> psql -U your_user -d your_database

\dt  -- list tables
