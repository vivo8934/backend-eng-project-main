from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
import os
import pandas as pd
import logging
import psycopg2

default_args = {
    'owner': 'mfundo',
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
    schedule='0 0 * * *',  
    start_date=datetime(2023, 1, 1),
    catchup=False,
)

def extract_step():
    file_path = os.getenv('FINANCIAL_TRANSACTIONS_PATH', 'data/financial_transactions.csv')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    
    try:
        df = pd.read_csv(file_path)
        logging.info("File successfully loaded.")
    except pd.errors.EmptyDataError:
        raise ValueError("The input file is empty.")
    except pd.errors.ParserError:
        raise ValueError("Error parsing the input file.")
    
    df.to_csv(file_path, index=False)
    logging.info(f"File saved successfully to {file_path}")

def transform_step():
    file_path = os.getenv('FINANCIAL_TRANSACTIONS_PATH', 'data/financial_transactions.csv')
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    df = pd.read_csv(file_path)

    expected_columns = {'transaction_id', 'user_id', 'amount', 'transaction_date'}
    actual_columns = set(df.columns)
    if not expected_columns.issubset(actual_columns):
        raise KeyError(f"Missing required columns: {expected_columns - actual_columns}")

    df['amount'] = df['amount'].astype(str).str.replace('[\$,]', '', regex=True)
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')

    df = df[(df['amount'] >= 0) & (df['transaction_date'] <= datetime.today())]
    df.dropna(inplace=True)
    df.drop_duplicates(inplace=True)

    df.to_csv(file_path, index=False)
    logging.info(f"Transformed data saved to {file_path}")

from psycopg2.extras import execute_values
def load_step():
    user, password, host, port = 'airflow', 'airflow', 'postgres', '5432'
    conn = psycopg2.connect(dbname='finance_app', user=user,password=password, host=host, port=port)
    cur = conn.cursor()
    

    df = pd.read_csv(os.getenv('FINANCIAL_TRANSACTIONS_PATH', 'data/financial_transactions.csv'))
    data_tuples = list(df.itertuples(index=False, name=None))

    insert_query = """
        INSERT INTO transactions (transaction_id, user_id, amount, transaction_date)
        VALUES %s
        ON CONFLICT (transaction_id) DO NOTHING;
    """
    execute_values(cur, insert_query, data_tuples)
    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"Inserted {len(data_tuples)} records successfully.")

task_extract = PythonOperator(task_id='extract_step', python_callable=extract_step, dag=dag)
task_transform = PythonOperator(task_id='transform_step', python_callable=transform_step, dag=dag, trigger_rule='all_success')
task_load = PythonOperator(task_id='load_step', python_callable=load_step, dag=dag, trigger_rule='all_success')

task_extract >> task_transform >> task_load
