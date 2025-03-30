import unittest
from unittest.mock import patch, MagicMock
from utils.ibkr_interface import IBKRClient

class TestIBKRClient(unittest.TestCase):

    @patch('utils.ibkr_interface.IBKRClient.get_historical_data')
    def test_get_historical_data(self, mock_get_historical_data):
        client = IBKRClient()
        client.get_historical_data("NVDA")
        mock_get_historical_data.assert_called_once_with("NVDA")
    
    @patch('utils.ibkr_interface.IBKRClient.get_current_market_data')
    def test_get_current_market_data(self, mock_get_current_market_data):
        client = IBKRClient()
        client.get_current_market_data("NVDA")
        mock_get_current_market_data.assert_called_once_with("NVDA")
    
    @patch('utils.ibkr_interface.IBKRClient.place_order')
    def test_place_order(self, mock_place_order):
        client = IBKRClient()
        client.place_order("NVDA", 10, "BUY", 650)
        mock_place_order.assert_called_once_with("NVDA", 10, "BUY", 650)
    
    @patch('utils.ibkr_interface.IBKRClient.get_account_balance')
    def test_get_account_balance(self, mock_get_account_balance):
        client = IBKRClient()
        client.get_account_balance()
        mock_get_account_balance.assert_called_once()
    
    @patch('utils.ibkr_interface.IBKRClient.get_open_positions')
    def test_get_open_positions(self, mock_get_open_positions):
        client = IBKRClient()
        client.get_open_positions()
        mock_get_open_positions.assert_called_once()

if __name__ == '__main__':
    unittest.main()
