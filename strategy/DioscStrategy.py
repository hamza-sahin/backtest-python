import indicator.Diosc as DioscIndicator
import strategy.Strategy as Strategy
import time
import pandas

class DioscStrategy():
    def __init__(self, 
                 length,
                 avg_length,
                 start_balance = 100,
                 is_compound_enabled = True,
                 tradable_ratio = 100,
                 contrat_limit = 40,
                 comission_rate = 0.04,
                 leverage = 15,
                 is_long_positions_enabled = True,
                 long_tp = 1,
                 long_sl = 1,
                 is_short_positions_enabled = True,
                 short_tp = 1,
                 short_sl = 1,
                 is_close_signals_enabled = True,
                 balance = 100,
                 long_tp_price = 0.0,
                 short_tp_price = 0.0,
                 long_sl_price = 0.0,
                 short_sl_price = 0.0,
                 data_location = None,
                 start_date = "",
                 end_date = ""):
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
        self.in_short_position = False
        self.trade_count = 0
        self.entry_price = 0
        self.position_quantity = 0
        self.quantity = 0,
        self.start_date = start_date,
        self.end_date = end_date

    def backtest(self):
        print(self.start_date)
        for bardata in self.dataframe.itertuples():
            date = time.strptime(bardata.time, "%d/%m/%Y")
            if (date >= self.start_date and date <= self.end_date):
                self.calculate_bar(bar_index = bardata.Index)

    def calculate_bar(self, bar_index):
        bardata = self.dataframe.iloc[bar_index]
        prev_bardata = self.dataframe.iloc[bar_index - 1]
        self.check_sltp(bardata['high'], bardata['low'], bardata['time'])

        is_short_signal = bardata['diosc'] <= bardata['diosc-signal'] and prev_bardata['diosc'] > prev_bardata['diosc-signal']
        is_long_signal = bardata['diosc'] >= bardata['diosc-signal'] and prev_bardata['diosc'] < prev_bardata['diosc-signal']

        if (self.is_close_signals_enabled):
            if (self.in_long_position and is_short_signal):
                self.close_position(Strategy.OrderSide.Buy, bardata['close'], Strategy.CloseReason.CloseBuy, bardata['time'])
                return
            if (self.in_short_position and is_long_signal):
                self.close_position(Strategy.OrderSide.Sell, bardata['close'], Strategy.CloseReason.CloseSell, bardata['time'])
                return                

        if (self.is_long_positions_enabled and not self.in_long_position and is_long_signal):
            self.calculate_position_quantity(bardata['close'])
            self.open_position(bardata['close'], Strategy.OrderSide.Buy, bardata['time'])

        if (self.is_short_positions_enabled and not self.in_short_position and is_short_signal):
            self.calculate_position_quantity(bardata['close'])
            self.open_position(bardata['close'], Strategy.OrderSide.Sell, bardata['time'])

    def calculate_position_quantity(self, close):
        self.quantity = self.balance / close
        self.position_quantity = self.quantity * self.leverage * self.tradable_ratio
        
        if (self.position_quantity > self.contrat_limit):
            self.position_quantity = self.contrat_limit
        
        self.quantity -= self.position_quantity / self.leverage

    def open_position(self, close, order_side, time):
        self.entry_price = close
        self.trade_count += 1
        print(time)
        if (order_side == Strategy.OrderSide.Buy):
            self.long_tp_price = self.entry_price + self.entry_price * (self.long_tp / 100)
            self.long_sl_price = self.entry_price - self.entry_price * (self.long_sl / 100)
            self.in_long_position = True
            print(f"-----------------------------------------")
            print(f"##############   < {self.trade_count} >   ##############")
            print("LONG SIGNAL TRIGGERED")
            print(f"LONG POSITION OPENED -> PRICE: {round(self.entry_price,2)}")
            print(f"TP: {round(self.long_tp_price,2)} , SL: {round(self.long_sl_price,2)}")
        else:
            self.short_tp_price = self.entry_price - self.entry_price * (self.short_tp / 100)
            self.short_sl_price = self.entry_price + self.entry_price * (self.short_sl / 100)
            self.in_short_position = True
            print(f"-----------------------------------------")
            print(f"##############   < {self.trade_count} >   ##############")
            print("SHORT SIGNAL TRIGGERED")
            print(f"SHORT POSITION OPENED -> PRICE: {round(self.entry_price,2)}")
            print(f"TP: {round(self.short_tp_price,2)} , SL: {round(self.short_sl_price, 2)}")

    def close_position(self, order_side, close, close_reason, time):
      
        price_change = (1 - self.entry_price / close)
        prev_balance = self.balance

        if (order_side == Strategy.OrderSide.Buy):
            self.balance = self.balance + (self.balance * self.leverage * price_change) - (self.balance * 2 * self.comission_rate / 100 * self.leverage)
            self.in_long_position = False
        else:
            self.balance = self.balance - (self.balance * self.leverage * price_change) - (self.balance * 2 * self.comission_rate / 100 * self.leverage)
            self.in_short_position = False

        print(time)
        print(f"{close_reason} TRIGGERED");
        print(f"{order_side} POSITION CLOSED -> PRICE: {round(close, 2)}");
        print(f"Price Change: %{round(100*price_change,2)}");
        print(f"                      PnL: {round(self.balance - prev_balance, 2)} $");
        print(f"                      Balance: {round(self.balance, 2)} $");
        print(f"--------------   < {self.trade_count} >   --------------");


    def check_sltp(self, high, low, time):
        if (self.in_long_position):
            if (self.long_tp_price < high):
                self.close_position(Strategy.OrderSide.Buy, self.long_tp_price, Strategy.CloseReason.LongTp, time)
            elif (self.long_sl_price > low):
                self.close_position(Strategy.OrderSide.Buy, self.long_sl_price, Strategy.CloseReason.LongSl, time)

        if (self.in_short_position):
            if (self.short_tp_price > low):
                self.close_position(Strategy.OrderSide.Sell, self.short_tp_price, Strategy.CloseReason.ShortTp, time)
            elif (self.short_sl_price < high):
                self.close_position(Strategy.OrderSide.Sell, self.short_sl_price, Strategy.CloseReason.ShortSl, time)

    def get_dataframe(self):
        return self.dataframe