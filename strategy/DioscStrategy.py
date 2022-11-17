import indicator.Diosc as DioscIndicator
import Strategy

class DioscStrategy():
    def __init__(self, 
                 length,
                 avg_length,
                 start_balance = None,
                 is_compound_enabled = None,
                 tradable_ratio = None,
                 contrat_limit = None,
                 comission_rate = None,
                 leverage = None,
                 is_long_positions_enabled = None,
                 long_tp = None,
                 long_sl = None,
                 is_short_positions_enabled = None,
                 short_tp = None,
                 short_sl = None,
                 is_close_signals_enabled = None,
                 balance = None,
                 long_tp_price = None,
                 short_tp_price = None,
                 long_sl_price = None,
                 short_sl_price = None,
                 data_location = None):
        self.short_sl_price = short_sl_price
        self.long_sl_price = long_sl_price
        self.short_tp_price = short_tp_price
        self.long_tp_price = long_tp_price
        self.balance = balance
        self.is_close_signals_enabled = is_close_signals_enabled
        self.short_sl = short_sl
        self.short_tp = short_tp
        self.is_short_positions_enabled = is_short_positions_enabled
        self.long_sl = long_sl
        self.long_tp = long_tp
        self.is_long_positions_enabled = is_long_positions_enabled
        self.leverage = leverage
        self.comission_rate = comission_rate
        self.contrat_limit = contrat_limit
        self.tradable_ratio = tradable_ratio
        self.is_compound_enabled = is_compound_enabled
        self.start_balance = start_balance
        self.length = length
        self.avg_length = avg_length
        self.diosc = DioscIndicator.Diosc(length=length,avg_length=avg_length, location= data_location)
        self.dataframe = self.diosc.calculate()
        self.in_long_position = False
        self.in_short_position = True
        self.trade_count = 0
        self.entry_price = 0
        self.position_quantity = 0
        self.quantity = 0,

    def backtest(self):
        for bardata in self.dataframe.itertuples():
            self.calculate_bar(bar_index = bardata.Index)

    def calculate_bar(self, bar_index):
        bardata = self.dataframe[bar_index]
        prev_bardata = self.dataframe[bar_index - 1]
        self.check_sltp(bardata['high'], bardata['low'])

        is_short_signal = bardata['diosc'] <= bardata['diosc-signal'] and prev_bardata['diosc'] > prev_bardata['diosc-signal']
        is_long_signal = bardata['diosc'] >= bardata['diosc-signal'] and prev_bardata['diosc'] < prev_bardata['diosc-signal']

        if (self.is_close_signals_enabled):
            if (self.in_long_position and is_short_signal):
                self.close_position(Strategy.OrderSide.Buy, bardata['close'], Strategy.CloseReason.CloseBuy)
                return
            if (self.in_short_position and is_long_signal):
                self.close_position(Strategy.OrderSide.Sell, bardata['close'], Strategy.CloseReason.CloseSell)
                return                

        if (self.is_long_positions_enabled and not self.in_long_position and is_long_signal):
            self.calculate_position_quantity(bardata['close'])
            self.open_position(bardata['close'], Strategy.OrderSide.Buy)

        if (self.is_short_positions_enabled and not self.in_short_position and is_short_signal):
            self.calculate_position_quantity(bardata['close'])
            self.open_position(bardata['close'], Strategy.OrderSide.Sell)

    def calculate_position_quantity(self, close):
        self.quantity = self.balance / close
        self.position_quantity = self.quantity * self.leverage * self.tradable_ratio
        
        if (self.position_quantity > self.contrat_limit):
            self.position_quantity = self.contrat_limit
        
        self.quantity -= self.position_quantity / self.leverage

    def open_position(self, close, order_side):
        self.entry_price = close
        self.trade_count += 1

        if (order_side == Strategy.OrderSide.Buy):
            self.long_tp_price = self.entry_price + self.entry_price * (self.long_tp / 100)
            self.long_sl_price = self.entry_price - self.entry_price * (self.long_sl / 100)
            self.in_long_position = True
        else:
            self.short_tp_price = self.entry_price - self.entry_price * (self.short_tp / 100)
            self.short_sl_price = self.entry_price + self.entry_price * (self.short_sl / 100)
            self.in_long_position = False

    def close_position(self, order_side, close, close_reason):
        if (order_side == Strategy.OrderSide.Buy):
            limit_side = Strategy.OrderSide.Sell
        else:
            limit_side = Strategy.OrderSide.Buy
        
        price_change = (1 - self.entry_price / close)
        prev_balance = self.balance

        if (order_side == Strategy.OrderSide.Buy):
            self.balance = self.balance + (self.balance * self.leverage * price_change) - (self.balance * 2 * self.comission_rate / 100 * self.leverage)
            self.in_long_position = False
        else:
            self.balance = self.balance - (self.balance * self.leverage * price_change) - (self.balance * 2 * self.comission_rate / 100 * self.leverage)
            self.in_short_position = False

    def check_sltp(self, high, low):
        if (self.in_long_position):
            if (self.long_tp_price < high):
                self.close_position(Strategy.OrderSide.Buy, self.long_tp_price, Strategy.CloseReason.LongTp)
            elif (self.long_sl_price > low):
                self.close_position(Strategy.OrderSide.Buy, self.long_sl_price, Strategy.CloseReason.LongSl)

        if (self.in_short_position):
            if (self.short_tp_price > low):
                self.close_position(Strategy.OrderSide.Buy, self.short_tp_price, Strategy.CloseReason.ShortTp)
            elif (self.short_sl_price < high):
                self.close_position(Strategy.OrderSide.Buy, self.short_sl_price, Strategy.CloseReason.ShortSl)

    def get_dataframe(self):
        return self.dataframe