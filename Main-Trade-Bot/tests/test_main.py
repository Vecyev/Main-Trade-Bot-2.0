import unittest
from unittest.mock import patch, MagicMock
import main

class TestMain(unittest.TestCase):

    @patch('main.IBKRClient')
    @patch('main.StrategyManager')
    @patch('main.RegressionModel')
    def test_main(self, MockRegressionModel, MockStrategyManager, MockIBKRClient):
        mock_ibkr = MockIBKRClient.return_value
        mock_manager = MockStrategyManager.return_value
        mock_model = MockRegressionModel.return_value
        
        with patch('main.load_config', return_value={
            "symbol": "NVDA", 
            "cost_basis": 650, 
            "log_level": "INFO",
            "ml_model_path": "model.pkl"
        }):
            with patch('main.setup_logging'):
                main.main()
        
        MockIBKRClient.assert_called_once()
        MockStrategyManager.assert_called_once_with(mock_ibkr, symbol="NVDA", cost_basis=650)
        mock_manager.set_ml_model.assert_called_once_with(mock_model)
        mock_manager.run.assert_called_once()

if __name__ == '__main__':
    unittest.main()
