# Airflow DAG definition for modular traffic analysis and email alerts

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.utils.dates import days_ago
from datetime import datetime

# Modular utility functions from traffic_utils.py
from traffic_utils import (
    filter_low_traffic_ips,
    branch_am_pm,
    run_am_task,
    run_pm_task,
)

# -------------------
# Default Configuration
# -------------------

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1), # Automatically sets yesterday as start point
}

dag = DAG(
    'traffic_analysis_dag',
    default_args=default_args,
    schedule_interval='@daily', # Daily traffic analysis
    catchup=False,              # Avoid backfilling for missed dates
    description="Modular Traffic Analysis with AM/PM branching and email alerts",
)

# -------------------
# TASK 1: Filter low-traffic IPs (bottom 20%)
# -------------------

filter_task = PythonOperator(
    task_id='filter_low_traffic',
    python_callable=filter_low_traffic_ips,
    dag=dag,
)

# -------------------
# TASK 2: Branching - Decide whether to run AM and/or PM based on filtered data
# -------------------

branch_task = BranchPythonOperator(
    task_id='branch_am_pm',
    python_callable=branch_am_pm, # Returns one or both task_ids
    dag=dag,
)

# -------------------
# TASK 3: AM Task (Weekend Only)
# Sends top 3 high-traffic AM records if current day is Saturday or Sunday
# -------------------

am_task_op = PythonOperator(
    task_id='am_task',
    python_callable=lambda **kwargs: run_am_task(kwargs['execution_date']),
    provide_context=True, # Required to pass execution_date from Airflow
    dag=dag,
)

# -------------------
# TASK 4: PM Task (Always runs if PM data exists)
# Sends top 3 high-traffic PM records
# -------------------

pm_task_op = PythonOperator(
    task_id='pm_task',
    python_callable=run_pm_task,
    dag=dag,
)

# -------------------
# DAG Workflow Definition
# -------------------
# Order of execution:
# 1️⃣ filter_low_traffic → 2️⃣ branch_am_pm → 3️⃣ am_task and/or pm_task

filter_task >> branch_task >> [am_task_op, pm_task_op]
