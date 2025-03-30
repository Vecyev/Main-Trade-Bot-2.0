import unittest
from unittest.mock import patch
from monitoring.alerts import AlertManager

class TestAlertManager(unittest.TestCase):

    @patch('monitoring.alerts.logging.info')
    def test_send_alert(self, mock_logging_info):
        alert_manager = AlertManager()
        alert_manager.send_alert("Test alert message")
        
        mock_logging_info.assert_called_once_with("Alert: Test alert message")

if __name__ == '__main__':
    unittest.main()
