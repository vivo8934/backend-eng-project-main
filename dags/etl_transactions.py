from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import os
import pandas as pd 
import psycopg2


default_args = {
    'owner': 'candidate',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


dag = DAG(
    'etl_transactions',
    default_args=default_args,
    description='ETL pipeline for financial transactions',
    schedule='0 0 * * *',  # Run daily at midnight
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

def extract_step():

    file_path = os.path.join("C:/Users/life mpho/Documents/Data Engineering/adsum-backend-eng-assignment-main/data/financial_transactions.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise ValueError("The input file is empty.")
    except pd.errors.ParserError:
        raise ValueError("Error parsing the input file.")
    df.head()
    output_file_name_1 = 'financial_transactions.csv'
    output_file_path = os.path.join(os.path.dirname(file_path), output_file_name_1)

    try:
        df.to_csv(output_file_path, index=False)
        print(f"File saved successfully to {output_file_path}")
    except IOError:
        raise IOError(f"Could not write to file {output_file_path}.")

                  
def transform_step():

    file_path = os.path.join("C:/Users/life mpho/Documents/Data Engineering/adsum-backend-eng-assignment-main/data/financial_transactions.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    try:
        df = pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise ValueError("The input file is empty.")
    except pd.errors.ParserError:
        raise ValueError("Error parsing the input file.")
    
    if 'amount' in df.columns:
        df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    else:
        raise KeyError("'amount' column not found in the input file.")
    
    if 'transaction_date' in df.columns:
        df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce').dt.strftime('%Y-%m-%d')
    else:
        raise KeyError("'transaction_date' column not found in the input file.")

    df = df.drop_duplicates()
    try:
        df.to_csv(file_path, index=False)
        print(f"Transformed data saved successfully to {file_path}")
    except IOError:
        raise IOError(f"Could not write to file {file_path}.")

def load_step():

    user = 'airflow'
    password = 'airflow'
    host = 'postgres'
    port = '5432'

    with open('C:/Users/life mpho/Documents/Data Engineering/adsum-backend-eng-assignment-main/init-db.sql', 'r') as file:
        sql_script = file.read()

    conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
    conn.autocommit = True  
    cur = conn.cursor()

    try:
        commands = sql_script.split(';')
        for command in commands:
            if command.strip():
                cur.execute(command)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

    conn = psycopg2.connect(dbname='finance_app', user=user, password=password, host=host, port=port)
    cur = conn.cursor()

    df = pd.read_csv("C:/Users/life mpho/Documents/Data Engineering/adsum-backend-eng-assignment-main/data/financial_transactions.csv")
    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO transactions (transaction_id, user_id, amount, transaction_date)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (transaction_id) DO NOTHING;
        """, (row['transaction_id'], row['user_id'], row['amount'], row['transaction_date']))

    conn.commit()
    cur.close()
    conn.close()


task_extract = PythonOperator(
    task_id='extract_step',
    python_callable=extract_step,
    dag=dag
)

task_transform = PythonOperator(
    task_id='transform_step',
    python_callable=transform_step,
    dag=dag
)

task_load = PythonOperator(
    task_id='load_step',
    python_callable=load_step,
    dag=dag
)

task_extract >> task_transform >> task_load

#extract_step()
#transform_step()