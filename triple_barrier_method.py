"""
Triple-barrier method
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.lines as mlines
from dataclasses import dataclass, field

@dataclass
class TripleBarrierMethod:
    """
    
    """
    target_price: pd.Series
    lower_barrier: float
    upper_barrier: float
    time_barrier: int
    df_barrier_price: pd.DataFrame = field(init=False)


    def __post_init__(self):
        """
        post-initialization to construct the barrier price df
        """
        self.df_barrier_price = self._construct_barrier_price_df()
    

    def _construct_barrier_price_df(self) -> pd.DataFrame:
        """
        construct df with target prices, upper and lower barriers
        """
        df_barrier_price = pd.DataFrame(index=self.target_price.index)
        df_barrier_price['target_price'] = self.target_price
        df_barrier_price['lower_barrier_price'] = self.target_price * (1 + self.lower_barrier)
        df_barrier_price['upper_barrier_price'] = self.target_price * (1 + self.upper_barrier)
        return df_barrier_price
    

    def label_data(self) -> pd.DataFrame:
        """
        label the target series based using the triple barrier method
        
        Labels:
        1 if the price crosses the upper barrier within the time limit
        -1 if the price crosses the lower barrier within the time limit
        0 if neither barrier is crossed within the time limit
        """
        labels = np.zeros(len(self.df_barrier_price), dtype=int)

        for idx in range(len(self.df_barrier_price) - self.time_barrier):
            upper_price = self.df_barrier_price['upper_barrier_price'].iloc[idx]
            lower_price = self.df_barrier_price['lower_barrier_price'].iloc[idx]
            
            # extract price window for one index
            price_window = self.df_barrier_price['target_price'].iloc[idx + 1: idx + 1 + self.time_barrier]
            
            # check if the price crosses the upper or lower barrier first
            upper_cross_idx = price_window[price_window > upper_price].index
            lower_cross_idx = price_window[price_window < lower_price].index

            if len(upper_cross_idx) > 0 and len(lower_cross_idx) > 0:
                labels[idx] = 1 if upper_cross_idx[0] < lower_cross_idx[0] else -1
            elif len(upper_cross_idx) > 0:
                labels[idx] = 1
            elif len(lower_cross_idx) > 0:
                labels[idx] = -1

        self.df_barrier_price['label'] = labels.astype(int)
        return self.df_barrier_price
    

    def plot_labels(self, colors: list, title: str):
        """
        plot scatter plot with labels
        
        :param colors: list of colors for each label : -1, 0, 1
        :param title: title
        """
        color_map = {-1: colors[0], 0: colors[1], 1: colors[2]}
        colors = self.df_barrier_price['label'].map(color_map)

        fig, ax = plt.subplots(figsize=(10, 6))
        scatter = ax.scatter(self.df_barrier_price.index, self.df_barrier_price['target_price'], c=colors, label=self.df_barrier_price['label'], edgecolors='black')

        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M'))
        plt.xticks(rotation=45, ha='right')

        ax.set_xlabel('time')
        ax.set_ylabel('price')
        ax.set_title(title)

        legend_labels = [
            mlines.Line2D([], [], color='#ff0000', marker='o', linestyle='None', markersize=10, label='Label -1'),
            mlines.Line2D([], [], color='#7945d9', marker='o', linestyle='None', markersize=10, label='Label 0'),
            mlines.Line2D([], [], color='#0fff00', marker='o', linestyle='None', markersize=10, label='Label 1')
        ]

        ax.legend(handles=legend_labels, title='Labels')
        plt.tight_layout()
        plt.show()
    

    def plot_square(self, date: str, title: str):
        """
        plot line plot with one square representing the barriers for a given date.
        
        :param date: The date for which to plot the barriers
        """
        bottom_rectangle = self.df_barrier_price.loc[date, 'lower_barrier_price']
        top_rectangle = self.df_barrier_price.loc[date, 'upper_barrier_price']
        y_value = self.df_barrier_price.loc[date, 'target_price']

        xmin = pd.to_datetime(date)
        xmax = xmin + pd.Timedelta(days=self.time_barrier)

        plt.figure(figsize=(10, 6))
        # Price
        plt.plot(self.df_barrier_price.index, self.df_barrier_price['target_price'], label='Target Price', color='#382054')
        # Horizontal barriers
        plt.hlines(y=top_rectangle, xmin=xmin, xmax=xmax, colors='green', label=f'Upper barrier')
        plt.hlines(y=y_value, xmin=xmin, xmax=xmax, colors='black', linestyles='dashed')
        plt.hlines(y=bottom_rectangle, xmin=xmin, xmax=xmax, colors='red', label=f'Lower barrier')
        # Vertical barriers
        plt.vlines(x=xmin, ymin=bottom_rectangle, ymax=top_rectangle, colors='grey', linestyles='dashed')
        plt.vlines(x=xmax, ymin=bottom_rectangle, ymax=top_rectangle, colors='blue', label=f'Vertical barrier')

        plt.legend()
        plt.title(title)
        plt.xlabel('time')
        plt.ylabel('price')

        plt.show()


if __name__ == '__main__':

    import yfinance as yf
    
    # test on Apple stock value
    data_daily = yf.download('AAPL', start='2020-01-01', end='2024-12-31', interval='1d')
    target_price = data_daily['Close']

    # barrier settings
    lower_barrier = -0.10
    upper_barrier = 0.10
    time_barrier = 20
    tbm = TripleBarrierMethod(target_price, lower_barrier=lower_barrier, upper_barrier=upper_barrier, time_barrier=time_barrier)
    df_labeled = tbm.label_data()
    tbm.plot_labels(colors=['#ff0000', '#7945d9', '#0fff00'], title='Labeled Price Data')
    tbm.plot_square(date='2022-01-07 00:00:00+00:00', title='Triple-Barrier square exemple')

