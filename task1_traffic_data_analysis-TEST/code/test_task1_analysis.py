import pandas as pd
import pytest
import numpy as np
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'task1_traffic_data_analysis', 'code')))


from task1_analysis import (
    top_3_ips_after_6pm,
    hour_with_highest_traffic_increase,
    top_3_domains,
    hourly_traffic_top_5_ips
)

@pytest.fixture
def mock_data():
    data = {
        'ip': ['192.168.0.1', '192.168.0.2', '192.168.0.3', '10.0.0.1', '10.0.0.2'] * 3,
        'time': pd.date_range('2025-01-01 17:00', periods=15, freq='h'),
        'gbps': [1, 3, 2, 5, 4, 2, 6, 1, 4, 3, 7, 2, 1, 3, 5]
    }
    df = pd.DataFrame(data)
    df['hour'] = df['time'].dt.hour
    return df

def test_top_3_ips_after_6pm(mock_data):
    result = top_3_ips_after_6pm(mock_data)
    assert len(result) == 3
    assert result.sum() > 0

def test_hour_with_highest_traffic_increase(mock_data):
    hour, increase = hour_with_highest_traffic_increase(mock_data)
    assert isinstance(hour, (int, np.integer))
    assert isinstance(increase, (float, np.floating))
    assert increase >= 0

def test_top_3_domains(mock_data):
    result = top_3_domains(mock_data)
    assert all('.' in domain for domain in result.index)
    assert len(result) == 2  # Only 2 domains used

def test_hourly_traffic_top_5_ips(mock_data):
    result = hourly_traffic_top_5_ips(mock_data)
    assert isinstance(result, pd.DataFrame)
    assert result.shape[1] <= 5
