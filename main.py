from strategy import DioscStrategy
import time

if __name__ == '__main__':
    strategy_diosc = DioscStrategy.DioscStrategy(
        length = 82, 
        avg_length = 48,
        start_balance = 100,
        is_compound_enabled = True,
        tradable_ratio = 100,
        contrat_limit = 40,
        comission_rate = 0.04,
        balance = 100,
        is_close_signals_enabled = True,
        is_long_positions_enabled = True,
        is_short_positions_enabled = True,
        leverage = 15,
        long_sl = 5,
        long_tp = 0.75,
        short_sl = 5,
        short_tp = 0.75,
        data_location= "data/BINANCE_BTCUSDTPERP, 240.csv",
        start_date = time.strptime("01/01/2022", "%d/%m/%Y"),
        end_date = time.strptime("01/11/2022", "%d/%m/%Y"))

    strategy_diosc.backtest()
    print(strategy_diosc.balance)