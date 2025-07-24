"""
Modular CSV Output Network Traffic Analysis Script

Performs:
1. Top 3 IPs after 6PM
2. Hour with highest traffic increase
3. Top 3 domains (first 2 parts of IP)
4. Hourly traffic movement for top 5 IPs

Saves output in `output/` directory.
"""

import pandas as pd
import os

OUTPUT_DIR = r"..\output"

def load_data(filepath: str) -> pd.DataFrame:
    """Load the dataset and parse timestamps."""
    try:
        df = pd.read_csv(filepath, parse_dates=['time'])
        if not {'ip', 'time', 'gbps'}.issubset(df.columns):
            raise ValueError("CSV missing required columns: 'ip', 'time', 'gbps'")
        df['hour'] = df['time'].dt.hour
        return df
    except Exception as e:
        print(f"[ERROR] Failed to load data: {e}")
        raise

def save_top3_ips_after_6pm(df: pd.DataFrame, output_dir: str):
    """Save top 3 IPs with highest traffic after 6PM."""
    try:
        after_6pm = df[df['hour'] > 18]
        result = after_6pm.groupby('ip')['gbps'].sum().sort_values(ascending=False).head(3)
        result.to_csv(os.path.join(output_dir, "top3_ips_after_6pm.csv"))
        return result
    except Exception as e:
        print(f"[ERROR] Task 1.1 failed: {e}")
        raise

def save_hourly_traffic_diff(df: pd.DataFrame, output_dir: str):
    """Save traffic increase between consecutive hours."""
    try:
        hourly_traffic = df.groupby('hour')['gbps'].sum().sort_index()
        hourly_diff = hourly_traffic.diff()
        hourly_diff.to_csv(os.path.join(output_dir, "hourly_traffic_difference.csv"))
        return hourly_diff.idxmax(), hourly_diff.max()
    except Exception as e:
        print(f"[ERROR] Task 1.2 failed: {e}")
        raise

def save_top3_domains(df: pd.DataFrame, output_dir: str):
    """Save top 3 domains (first 2 parts of IP) by traffic."""
    try:
        df['domain'] = df['ip'].apply(lambda x: '.'.join(x.split('.')[:2]))
        result = df.groupby('domain')['gbps'].sum().sort_values(ascending=False).head(3)
        result.to_csv(os.path.join(output_dir, "top3_domains.csv"))
        return result
    except Exception as e:
        print(f"[ERROR] Task 1.3 failed: {e}")
        raise

def save_hourly_top5_ip_traffic(df: pd.DataFrame, output_dir: str):
    """Save hourly traffic distribution of top 5 IPs."""
    try:
        top5_ips = df.groupby('ip')['gbps'].sum().nlargest(5).index
        filtered_df = df[df['ip'].isin(top5_ips)]
        result = filtered_df.groupby(['hour', 'ip'])['gbps'].sum().unstack(fill_value=0)
        result.to_csv(os.path.join(output_dir, "hourly_traffic_top5_ips.csv"))
        return result
    except Exception as e:
        print(f"[ERROR] Task 1.4 failed: {e}")
        raise

def main():
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        df = load_data(r"..\data\task_2.csv")
        save_top3_ips_after_6pm(df, OUTPUT_DIR)
        save_hourly_traffic_diff(df, OUTPUT_DIR)
        save_top3_domains(df, OUTPUT_DIR)
        save_hourly_top5_ip_traffic(df, OUTPUT_DIR)
        print("All tasks completed successfully. Output saved in 'output/' folder.")
    except Exception as e:
        print(f"Pipeline failed: {e}")

if __name__ == "__main__":
    main()
