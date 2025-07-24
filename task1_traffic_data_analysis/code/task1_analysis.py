"""
Modular Network Traffic Analysis Script

Performs:
1. Top 3 IPs after 6PM
2. Hour with highest traffic increase
3. Top 3 domains (first two parts of IP)
4. Hourly traffic movement for top 5 IPs

Assumes:
- CSV input: task_2.csv
- Columns: ip, time, gbps
"""

import pandas as pd

def load_data(filepath: str) -> pd.DataFrame:
    """Load traffic data from CSV."""
    try:
        df = pd.read_csv(filepath, parse_dates=['time'])
        if not {'ip', 'time', 'gbps'}.issubset(df.columns):
            raise ValueError("Missing required columns in the CSV file.")
        df['hour'] = df['time'].dt.hour
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

def top_3_ips_after_6pm(df: pd.DataFrame) -> pd.Series:
    """Return top 3 IPs with highest traffic after 6PM."""
    after_6pm = df[df['hour'] > 18]
    return after_6pm.groupby('ip')['gbps'].sum().sort_values(ascending=False).head(3)

def hour_with_highest_traffic_increase(df: pd.DataFrame) -> tuple:
    """Find the hour with the highest traffic increase."""
    hourly = df.groupby('hour')['gbps'].sum().sort_index()
    diff = hourly.diff()
    return diff.idxmax(), diff.max()

def top_3_domains(df: pd.DataFrame) -> pd.Series:
    """Return top 3 domains based on total traffic."""
    df['domain'] = df['ip'].apply(lambda x: '.'.join(x.split('.')[:2]))
    return df.groupby('domain')['gbps'].sum().sort_values(ascending=False).head(3)

def hourly_traffic_top_5_ips(df: pd.DataFrame) -> pd.DataFrame:
    """Return hourly traffic data for top 5 IPs."""
    top5_ips = df.groupby('ip')['gbps'].sum().nlargest(5).index
    filtered_df = df[df['ip'].isin(top5_ips)]
    return filtered_df.groupby(['hour', 'ip'])['gbps'].sum().unstack(fill_value=0)

def main():
    try:
        df = load_data(r"..\data\task_2.csv")

        print("Top 3 high traffic IPs after 6PM:")
        print(top_3_ips_after_6pm(df), end="\n\n")

        hour, increase = hour_with_highest_traffic_increase(df)
        print(f"Hour with highest traffic increase: {hour} (Increase: {increase:.2f} Gbps)\n")

        print("Top 3 domains by total traffic:")
        print(top_3_domains(df), end="\n\n")

        print("Hourly traffic movement for top 5 IPs:")
        print(hourly_traffic_top_5_ips(df).to_string())

    except Exception as e:
        print(f"Failed to complete analysis: {e}")

if __name__ == "__main__":
    main()
