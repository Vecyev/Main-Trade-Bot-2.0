import unittest
from unittest.mock import patch, MagicMock
from strategy.manager import StrategyManager

class TestStrategyManager(unittest.TestCase):

    @patch('strategy.manager.StrategyManager.extract_features', return_value=[1, 2, 3])
    @patch('strategy.manager.StrategyManager.make_decision')
    @patch('strategy.manager.RegressionModel.predict', return_value=[0.5])
    def test_run_with_ml_model(self, mock_predict, mock_make_decision, mock_extract_features):
        mock_ibkr_client = MagicMock()
        manager = StrategyManager(mock_ibkr_client, symbol="NVDA", cost_basis=650)
        mock_ml_model = MagicMock()
        manager.set_ml_model(mock_ml_model)
        
        manager.run()
        
        mock_extract_features.assert_called_once()
        mock_predict.assert_called_once_with([1, 2, 3])
        mock_make_decision.assert_called_once_with([0.5])

if __name__ == '__main__':
    unittest.main()
