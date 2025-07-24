# Traffic Data Analysis with Apache Airflow

This project contains solutions to two data engineering tasks using Python and Apache Airflow. It involves traffic log analysis, filtering, branching, and automated email alerts.

---

## 📌 Task 1: Python-Based Traffic Analysis

**Dataset:** `task_2.csv` — traffic data for a hosting provider for one day.

### ✅ Goals & Python Implementations:

- 🔹 **Top 3 high traffic IPs after 6PM**
- 🔹 **Find the hour with the highest traffic increase**
- 🔹 **Top 3 domains by total traffic**  
  (Domain = first two parts of IP, e.g., `172.64` from `172.64.205.7`)
- 🔹 **Traffic movement for top 5 IPs across all hours**
- 🔹 **Memory and performance optimization applied**  
  (Code modularized with vectorized operations & minimal data copies)

➡️ All code is available in `task1_analysis.py`, with reusable functions and testable outputs.

---

## 📌 Task 2: Airflow DAG for Traffic Pipeline

**Dataset:** `traffic_data.csv` — daily traffic log processed using an Apache Airflow DAG.

### ✅ DAG Overview (runs once daily at midnight):

1. **Filter out 20% of IPs** based on lowest total traffic
2. **Branch task execution into AM and PM traffic**
3. **PM Branch:**  
   - Send top 3 high-traffic IPs to a configured Outlook email address  
   - Runs **daily**
4. **AM Branch:**  
   - If the execution date is a **weekend**, send top 3 AM IPs via email  
   - If it's a **weekday**, skip the AM task
5. Outputs are saved as CSV files in the `output/` folder

➡️ Core DAG logic is implemented in `traffic_dag.py`  
➡️ Helper logic (filtering, branching, emailing) in `traffic_utils.py`

---

## 🧪 Testing

- Unit tests use `pytest` and can be run via:

```bash
pytest tests/ -v
