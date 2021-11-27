import threading
import time
import traceback
import ccxt

class StoreWarpupFtx:
    def __init__(self, store=None, logger=None, min_interval=None):
        self.store = store
        self.logger = logger
        self.min_interval = min_interval

    def start(self):
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def _run(self):
        while True:
            time.sleep(60)
            try:
                self._loop()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                self.logger.error('exception ' + traceback.format_exc())
                time.sleep(60)

    def _loop(self, raise_error=False):
        intervals = [
            15,
            60,
            300,
            900,
            3600,
            14400,
            86400
            ]

        price_types = [
            None,
            'index',
        ]

        ftx = ccxt.ftx()
        markets = list(map(lambda x: x['name'], ftx.publicGetMarkets()['result']))
        current_futures = list(map(lambda x: x['name'], ftx.publicGetFutures()['result']))
        expired_futures = list(map(lambda x: x['name'], ftx.publicGetExpiredFutures()['result']))
        unique_symbols = list(set(markets + current_futures + expired_futures))

        for symbol in unique_symbols:
            for interval in intervals:
                if self.min_interval is not None and interval < self.min_interval:
                    continue

                for price_type in price_types:
                    if price_type == 'index' and '-PERP' not in symbol:
                        continue
                    try:
                        self.store.get_df_ohlcv(
                            exchange='ftx',
                            market=symbol,
                            interval=interval,
                            price_type=price_type,
                            force_fetch=True
                        )
                    except KeyboardInterrupt:
                        raise
                    except Exception as e:
                        if raise_error:
                            raise
                        self.logger.error('exception ' + traceback.format_exc())
                        time.sleep(60)

            try:
                if symbol in (current_futures + expired_futures):
                    self.store.get_df_fr(
                        exchange='ftx',
                        market=symbol,
                        force_fetch=True
                    )
            except KeyboardInterrupt:
                raise
            except Exception as e:
                if raise_error:
                    raise
                self.logger.error('exception ' + traceback.format_exc())
                time.sleep(60)
