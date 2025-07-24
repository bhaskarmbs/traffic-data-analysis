import os
import pandas as pd
import pytest
from datetime import datetime
from unittest import mock
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'task2_traffic_data_analysis_airflow_dag', 'dags')))

from traffic_utils import (
    filter_low_traffic_ips,
    branch_am_pm,
    run_am_task,
    run_pm_task,
    send_email,
    FILTERED_PATH,
    AM_PATH,
    PM_PATH
)

# -------------------------
# Sample input data
# -------------------------
@pytest.fixture
def sample_csv(tmp_path):
    file_path = tmp_path / "sample.csv"
    data = {
        'ip': ['1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4', '5.5.5.5'],
        'gbps': [1, 2, 3, 4, 5],
        'bf_time': ['08:00', '10:30', '12:15', '15:45', '18:30']
    }
    pd.DataFrame(data).to_csv(file_path, index=False)
    return file_path


# -------------------------
# Tests
# -------------------------

def test_filter_low_traffic_ips(sample_csv, tmp_path):
    out_file = tmp_path / "filtered.csv"
    result = filter_low_traffic_ips(str(sample_csv), str(out_file))
    df = pd.read_csv(out_file)

    # Bottom 20% (1 row) should be dropped
    assert len(df) == 4
    assert '1.1.1.1' not in df['ip'].values

def test_branch_am_pm(tmp_path):
    df = pd.DataFrame({
        'ip': ['1.1.1.1', '2.2.2.2', '3.3.3.3'],
        'gbps': [10, 20, 30],
        'bf_time': ['08:00', '13:00', '19:00']
    })
    df.to_csv(FILTERED_PATH, index=False)
    tasks = branch_am_pm(FILTERED_PATH)
    assert 'am_task' in tasks
    assert 'pm_task' in tasks
    assert os.path.exists(AM_PATH)
    assert os.path.exists(PM_PATH)

@mock.patch('traffic_utils.send_email')
def test_run_am_task_on_weekend(mock_send_email, tmp_path):
    df = pd.DataFrame({
        'ip': ['1.1.1.1', '2.2.2.2'],
        'gbps': [5, 15],
        'bf_time': ['09:00', '10:00']
    })
    df.to_csv(FILTERED_PATH, index=False)

    saturday = datetime(2024, 7, 6)  # Saturday
    run_am_task(saturday)
    
    mock_send_email.assert_called_once()
    assert os.path.exists(AM_PATH)

@mock.patch('traffic_utils.send_email')
def test_run_am_task_on_weekday_skips(mock_send_email, tmp_path):
    df = pd.DataFrame({
        'ip': ['1.1.1.1'],
        'gbps': [5],
        'bf_time': ['09:00']
    })
    df.to_csv(FILTERED_PATH, index=False)

    tuesday = datetime(2024, 7, 2)  # Tuesday
    run_am_task(tuesday)

    mock_send_email.assert_not_called()

@mock.patch('traffic_utils.send_email')
def test_run_pm_task(mock_send_email, tmp_path):
    df = pd.DataFrame({
        'ip': ['3.3.3.3', '4.4.4.4'],
        'gbps': [30, 40],
        'bf_time': ['13:00', '22:00']
    })
    df.to_csv(FILTERED_PATH, index=False)

    run_pm_task()
    mock_send_email.assert_called_once()
    assert os.path.exists(PM_PATH)

@mock.patch('smtplib.SMTP')
def test_send_email_success(mock_smtp):
    send_email("Test Subject", "Body here")
    instance = mock_smtp.return_value.__enter__.return_value
    instance.sendmail.assert_called_once()
