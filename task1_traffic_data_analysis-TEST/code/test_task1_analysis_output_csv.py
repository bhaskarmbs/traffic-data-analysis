import pandas as pd
import os
import shutil
import pytest
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'task1_traffic_data_analysis', 'code')))

from task1_analysis_output_csv import (
    load_data,
    save_top3_ips_after_6pm,
    save_hourly_traffic_diff,
    save_top3_domains,
    save_hourly_top5_ip_traffic
)

@pytest.fixture
def mock_df():
    data = {
        'ip': ['192.168.0.1', '192.168.0.2', '10.0.0.1', '192.168.0.1', '10.0.0.2'] * 3,
        'time': pd.date_range("2025-01-01 17:00", periods=15, freq="h"),
        'gbps': [2, 4, 1, 5, 3, 3, 6, 2, 5, 1, 7, 2, 1, 2, 4]
    }
    df = pd.DataFrame(data)
    df['hour'] = df['time'].dt.hour
    return df

@pytest.fixture(scope="module", autouse=True)
def temp_output_dir():
    temp_dir = "output"
    os.makedirs(temp_dir, exist_ok=True)
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_save_top3_ips_after_6pm(mock_df, temp_output_dir):
    result = save_top3_ips_after_6pm(mock_df, temp_output_dir)
    assert result.shape[0] == 3
    assert os.path.exists(os.path.join(temp_output_dir, "top3_ips_after_6pm.csv"))

def test_save_hourly_traffic_diff(mock_df, temp_output_dir):
    hour, increase = save_hourly_traffic_diff(mock_df, temp_output_dir)
    assert isinstance(hour, (int, np.integer, type(pd.NA)))  # allow int or numpy.int32 or pd.NA
    assert isinstance(increase, (float, np.floating, type(pd.NA)))
    assert os.path.exists(os.path.join(temp_output_dir, "hourly_traffic_difference.csv"))

def test_save_top3_domains(mock_df, temp_output_dir):
    result = save_top3_domains(mock_df, temp_output_dir)
    assert len(result) <= 3
    assert all('.' in domain for domain in result.index)
    assert os.path.exists(os.path.join(temp_output_dir, "top3_domains.csv"))

def test_save_hourly_top5_ip_traffic(mock_df, temp_output_dir):
    result = save_hourly_top5_ip_traffic(mock_df, temp_output_dir)
    assert isinstance(result, pd.DataFrame)
    assert result.shape[1] <= 5
    assert os.path.exists(os.path.join(temp_output_dir, "hourly_traffic_top5_ips.csv"))
