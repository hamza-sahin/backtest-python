from strategy import DioscStrategy

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
        data_location= 'data\data-tv-backtest.csv')

    strategy_diosc.backtest()
    print(strategy_diosc.balance)