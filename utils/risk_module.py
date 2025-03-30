# risk_module.py
from typing import List, Tuple, Dict

class Trade:
    def __init__(self, strike: float, delta: float, premium: float, underlying_price: float, shares: int,
                 required_capital: float = None):
        """
        Represents an option trade for risk and allocation calculations.
        
        Parameters:
            strike (float): Option strike price.
            delta (float): Option delta.
            premium (float): Option premium per share.
            underlying_price (float): Current price of the underlying.
            shares (int): Number of shares per contract (typically 100).
            required_capital (float, optional): Capital required if assigned; defaults to strike * shares.
        """
        self.strike = strike
        self.delta = delta
        self.premium = premium
        self.underlying_price = underlying_price
        self.shares = shares
        self.required_capital = required_capital if required_capital is not None else strike * shares


def calculate_assignment_risk_penalty(trade: Trade, available_capital: float, capital_buffer: float = 0.2) -> float:
    """
    Calculate a penalty score based on assignment risk relative to available capital.
    Penalizes trades that require more capital than allowed after reserving a safety buffer.
    
    Parameters:
        trade (Trade): The trade object.
        available_capital (float): Total capital available for assignment risk.
        capital_buffer (float, optional): Fraction of capital reserved as a safety buffer (default 0.2).
    
    Returns:
        float: Penalty score (higher means worse risk profile).
    """
    allowed_capital = available_capital * (1 - capital_buffer)
    if trade.required_capital > allowed_capital:
        penalty = ((trade.required_capital - allowed_capital) / allowed_capital) * 10
    else:
        penalty = 0.0
    return penalty


def adjust_trade_score(base_score: float, trade: Trade, available_capital: float, capital_buffer: float = 0.2) -> float:
    """
    Adjust the base trade score by incorporating an assignment risk penalty.
    
    Parameters:
        base_score (float): The initial trade score based on your bot's conviction logic.
        trade (Trade): The trade being evaluated.
        available_capital (float): Total available capital.
        capital_buffer (float, optional): Fraction of capital to reserve (default 0.2).
    
    Returns:
        float: The adjusted trade score.
    """
    risk_penalty = calculate_assignment_risk_penalty(trade, available_capital, capital_buffer)
    return base_score - risk_penalty


def compute_allocation_size(available_capital: float, max_allocation_percent: float = 0.1) -> float:
    """
    Compute the maximum dollar allocation for a trade based on available capital.
    
    Parameters:
        available_capital (float): Total capital available.
        max_allocation_percent (float, optional): Maximum percentage of available capital to allocate (default 0.1).
    
    Returns:
        float: Maximum dollar amount to allocate to the trade.
    """
    return available_capital * max_allocation_percent


def evaluate_trades(trade_scores: List[Tuple[Trade, float]], available_capital: float, 
                    capital_buffer: float = 0.2, max_allocation_percent: float = 0.1) -> List[Dict]:
    """
    Evaluate a list of trades, adjusting each trade's base score for assignment risk and computing an allocation size.
    
    Parameters:
        trade_scores (List[Tuple[Trade, float]]): List of tuples (trade, base_score) where:
            - trade is a Trade object.
            - base_score is the initial score (float) from your bot's conviction logic.
        available_capital (float): Total available capital.
        capital_buffer (float, optional): Safety buffer fraction (default 0.2).
        max_allocation_percent (float, optional): Maximum allocation percent (default 0.1).
    
    Returns:
        List[Dict]: A list of dictionaries with the keys:
            - 'trade': The Trade object.
            - 'base_score': Original score.
            - 'adjusted_score': Score after applying the assignment risk penalty.
            - 'allocation_size': Dollar amount that can be allocated to the trade.
    """
    evaluations = []
    for trade, base_score in trade_scores:
        adjusted_score = adjust_trade_score(base_score, trade, available_capital, capital_buffer)
        allocation_size = compute_allocation_size(available_capital, max_allocation_percent)
        evaluations.append({
            "trade": trade,
            "base_score": base_score,
            "adjusted_score": adjusted_score,
            "allocation_size": allocation_size
        })
    return evaluations


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create a dummy trade for testing
    trade_example = Trade(strike=250, delta=0.3, premium=5, underlying_price=260, shares=100)
    base_score_example = 8.0
    available_capital_example = 10000.0

    trade_scores = [(trade_example, base_score_example)]
    evaluations = evaluate_trades(trade_scores, available_capital_example)
    for eval in evaluations:
        print("Evaluation:", eval)
