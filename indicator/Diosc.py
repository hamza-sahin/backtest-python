import pandas as pd
import pandas_ta as ta
import numpy as np
import matplotlib
import indicator


class Diosc():
    def __init__(self, length, avg_length, location):
        self.length = length
        self.avg_length = avg_length
        self.location = location

    def calculate(self):
        df = pd.read_csv(self.location)
        df['time'] = pd.to_datetime(df['time'], unit='s')

        dataframe = pd.DataFrame()

        dataframe['high-low'] = df['high'] - df['low']
        dataframe['high-close'] = abs(df['high'] - df['close'].shift())
        dataframe['low-close'] = abs(df['low'] - df['close'].shift())

        dataframe['true_range'] = dataframe.max(axis=1)
        dataframe['true_range'][0] = np.nan
        dataframe['true_range'][1] = 87.8799999999992

        dataframe['up'] = ta.mom(df['high'], 1)
        dataframe['down'] = -ta.mom(df['low'], 1)

        df['true_range_rma'] = dataframe['true_range'].ewm(alpha=1 / self.length, min_periods=self.length).mean()

        dataframe['plus'] = np.where((dataframe['up'] > dataframe['down']) & (dataframe['up'] > 0), dataframe['up'], 0)
        dataframe['minus'] = np.where((dataframe['down'] > dataframe['up']) & (dataframe['down'] > 0),dataframe['down'], 0)
        df['plus_rma'] = 100 * ta.rma(dataframe['plus'], self.length) / df['true_range_rma']
        df['minus_rma'] = 100 * ta.rma(dataframe['minus'], self.length) / df['true_range_rma']
        df['minus_rma'] = df['minus_rma'].fillna(method='ffill')

        df['diosc'] = df['plus_rma'] - df['minus_rma']
        df['diosc-signal'] = ta.sma(df['diosc'], self.avg_length)
        df['previous-diosc'] = df['diosc'].shift()
        df['previous-sma'] = df['diosc-signal'].shift()

        return df
