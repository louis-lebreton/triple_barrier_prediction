"""
@author: Louis Lebreton
Equity Strategy
"""

import pandas as pd
from dataclasses import dataclass, field

@dataclass
class EquityStrategy:
    """
    this class models an equity trading strategy that simulates buying and selling of shares over time
    It evaluates the performance of the strategy based on profit and maximum drawdown

    Attributes:
        buy_number: number of shares to buy when a buy signal is encountered
        sell_number: number of shares to sell when a sell signal is encountered
        cash: initial cash available for trading
        shares: initial number of shares held
        transaction_fee: fee applied to each transaction (buy/sell)
        dca_strategy: If a Dollar-Cost Averaging (DCA) strategy is selected
        dca_cash: Amount of cash to invest periodically as part of the DCA strategy
        equity_curve: series that tracks the equity value over time
        df: df containing market data and TBM labels
    """
    buy_number: int = 1
    sell_number: int = 1
    cash: float = 100
    shares: int = 0
    transaction_fee: float = 0.1  # transaction fee per buy/sell
    dca_strategy: bool = False
    dca_cash: float = 0
    equity_curve: pd.Series = field(default_factory=pd.Series)
    df: pd.DataFrame = field(default=None)

    def __post_init__(self):
        if self.df is not None:
            self.buy_and_sell()

    def buy_and_sell(self) -> None:
        """
        function that buys and sells shares
        :df: dataframe containing columns 'target_price' and 'label'
        :return: equity curve
        """
        equity_curve = []

        cash = self.cash
        shares = self.shares

        for index, row in self.df.iterrows():
            
            if self.dca_strategy:
                shares += self.dca_cash / row['target_price'] # if DCA: number of shares chosen according the target price

            if row['label'] == 1 and cash > 0:
                # buy x share
                shares += self.buy_number
                cash -= (row['target_price'] * self.buy_number) + self.transaction_fee
            elif row['label'] == -1 and shares > 0:
                # sell x share
                shares -= self.sell_number
                cash += (row['target_price'] * self.sell_number) - self.transaction_fee

            # calculate current equity value
            equity = cash + (shares * row['target_price'])
            equity_curve.append(equity)

        self.equity_curve = pd.Series(equity_curve)

    def calculate_profit(self) -> float:
        """
        function that calculates the total profit from the equity curve
        :equity_curve: list or pandas series containing equity values over time
        :return: total profit
        """
        initial_equity = self.equity_curve.iloc[0]
        final_equity = self.equity_curve.iloc[-1]
        return final_equity - initial_equity

    def calculate_maximum_drawdown(self) -> float:
        """
        calculates the maximum drawdown (MDD) from an equity curve
        :equity_curve: list or pandas series containing equity values over time
        :return: value of maximum drawdown
        """
        peak = self.equity_curve.cummax()
        drawdown = self.equity_curve - peak
        max_drawdown = drawdown.min()
        return abs(max_drawdown)

    def fitness_function(self, weight_p: float = 0.5, weight_mdd: float = 0.5) -> float:
        """
        fitness function combining profit and maximum drawdown
        :weight_p: weight of profit
        :weight_mdd: weight of maximum drawdown
        :return: value of the fitness function
        """
        profit = self.calculate_profit()
        mdd = self.calculate_maximum_drawdown()
        return weight_p * profit - weight_mdd * mdd
    
    def calculate_sharpe_ratio(self, risk_free_rate: float = 0.0) -> float:
        """
        Calculates the sharpe ratio of the strategy

        :param risk_free_rate: risk-free rate used in the sharpe ratio calculation (default is 0.0).
        :return: sharpe ratio value
        """
       
        daily_returns = self.equity_curve.pct_change().dropna()
        mean_return = daily_returns.mean()
        std_dev_return = daily_returns.std()

        if std_dev_return == 0:
            return 0.0 

        sharpe_ratio = (mean_return - risk_free_rate) / std_dev_return
        return sharpe_ratio
