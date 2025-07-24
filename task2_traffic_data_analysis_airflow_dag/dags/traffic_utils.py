import os
import pandas as pd
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# ------------------- Configuration Constants -------------------

# Base directory for input/output (aligned with Airflow dags folder)
BASE_DIR = "/opt/airflow/dags"

# Input file containing raw traffic logs
INPUT_FILE = os.path.join(BASE_DIR, "../data/traffic_data.csv")

# Output folder for processed results
OUTPUT_DIR = os.path.join(BASE_DIR, "../output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Output file paths
FILTERED_PATH = os.path.join(OUTPUT_DIR, "filtered_traffic.csv")
AM_PATH = os.path.join(OUTPUT_DIR, "am_traffic.csv")
PM_PATH = os.path.join(OUTPUT_DIR, "pm_traffic.csv")

# SMTP Email configuration — loaded securely via environment variables
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL", SMTP_USER)


# ------------------- FUNCTION 1 -------------------

def filter_low_traffic_ips(input_file=INPUT_FILE, output_file=FILTERED_PATH):
    """
    Filters out the bottom 20% of IPs based on total traffic usage (gbps).
    This step helps eliminate noisy low-volume traffic which is usually irrelevant for reporting.

    Assumptions:
    - CSV must contain 'gbps' column (numeric).
    - We treat bottom 20% of rows as low-volume (based on row count, not percentile value).

    Returns:
        pd.DataFrame: Filtered DataFrame
    """
    try:
        df = pd.read_csv(input_file)
        if 'gbps' not in df.columns:
            raise ValueError("Missing 'gbps' column in input data.")
        
        # Sort and cut off bottom 20% by traffic
        df_sorted = df.sort_values(by='gbps')
        cutoff = int(len(df_sorted) * 0.2)
        filtered_df = df_sorted.iloc[cutoff:]
        
        filtered_df.to_csv(output_file, index=False)
        return filtered_df

    except Exception as e:
        print(f"[ERROR] Failed to filter low traffic IPs: {e}")
        raise

# ------------------- FUNCTION 2 -------------------

def branch_am_pm(filtered_path=FILTERED_PATH):
    """
    Splits the filtered traffic into two time segments:
        - AM: hours < 12
        - PM: hours >= 12

    Purpose:
    - Allows Airflow to branch execution based on whether AM and/or PM data exists.

    Returns:
        list[str]: list of task_ids to trigger (am_task, pm_task)
    """
    try:
        df = pd.read_csv(filtered_path)
        if df.empty:
            return []

        # Extract hour from 'bf_time' (e.g., "09:30" → 9)
        df['hour'] = df['bf_time'].str.split(':').str[0].astype(int)

        # Create AM and PM DataFrames
        am_df = df[df['hour'] < 12]
        pm_df = df[df['hour'] >= 12]

        # Save outputs
        am_df.to_csv(AM_PATH, index=False)
        pm_df.to_csv(PM_PATH, index=False)

        # Dynamically decide which tasks to run
        tasks = []
        if not am_df.empty:
            tasks.append("am_task")
        if not pm_df.empty:
            tasks.append("pm_task")
        return tasks

    except Exception as e:
        print(f"[ERROR] Failed in branching logic: {e}")
        raise

# ------------------- FUNCTION 3 -------------------
def run_am_task(execution_date: datetime):
    """
    Sends the top 3 high-traffic AM IPs via email — only if the execution falls on a weekend.

    Purpose:
    - Weekends often have different traffic patterns (e.g., gaming, streaming).
    - Business wants to track anomalies during off-peak periods.

    Assumptions:
    - 'bf_time' format is "HH:MM"
    """
    try:
        if execution_date.weekday() >= 5:  # Saturday=5, Sunday=6
            df = pd.read_csv(FILTERED_PATH)
            am_df = df[df['bf_time'].str.startswith(tuple([f"{h:02d}" for h in range(0, 12)]))]
            top_am = am_df.sort_values(by='gbps', ascending=False).head(3)
            top_am.to_csv(AM_PATH, index=False)

            send_email("AM Traffic Report", top_am.to_string(index=False))
        else:
            print("[INFO] Not a weekend. AM task skipped.")

    except Exception as e:
        print(f"[ERROR] Failed to execute AM task: {e}")
        raise

# ------------------- FUNCTION 4 -------------------

def run_pm_task():
    """
    Sends the top 3 high-traffic PM IPs via email.
    PM traffic typically reflects business operations, so this runs daily regardless of weekday.

    Returns:
        None
    """
    try:
        df = pd.read_csv(FILTERED_PATH)
        pm_df = df[df['bf_time'].str.startswith(tuple([f"{h:02d}" for h in range(12, 24)]))]
        top_pm = pm_df.sort_values(by='gbps', ascending=False).head(3)
        top_pm.to_csv(PM_PATH, index=False)

        send_email("PM Traffic Report", top_pm.to_string(index=False))

    except Exception as e:
        print(f"[ERROR] Failed to execute PM task: {e}")
        raise

# ------------------- FUNCTION 5 -------------------

def send_email(subject: str, body: str):
    """
    Sends a plain-text email using SMTP credentials defined in env vars.

    Security:
    - Uses STARTTLS
    - Credentials not hardcoded

    Handles:
    - SMTP login failures
    - Network errors
    """
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = TO_EMAIL

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_USER, TO_EMAIL, msg.as_string())

        print(f"[INFO] Email sent: {subject}")

    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        raise
