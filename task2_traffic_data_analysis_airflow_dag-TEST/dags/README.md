# Airflow Traffic Analysis DAG

This project analyzes network traffic logs using Apache Airflow in a modular and testable way.

## 🚀 Features

- Filter out bottom 20% IPs by traffic
- Branch into AM/PM processing
- Send top 3 traffic reports via Outlook email
- AM task runs only on weekends
- Modular logic (`traffic_utils.py`)
- Full pytest coverage

## 📁 Project Structure

