from collections import defaultdict
import re
import threading
import pandas as pd
from data_fetcher_builder import DataFetcherBuilder

class Store:
    def __init__(self, logger=None, start_time=None):
        self.fetcher_builder = DataFetcherBuilder()
        self.dfs = {}
        self.locks = defaultdict(threading.Lock)
        self.locks_lock = threading.Lock()
        self.logger = logger
        self.start_time = start_time

    def _get_lock(self, key):
        with self.locks_lock:
            return self.locks[key]

    def status(self):
        dfs_status = {}

        for key in self.dfs:
            df = self.dfs.get(key)
            if df is None:
                dfs_status[key] = None
            else:
                dfs_status[key] = {
                    'count': df.shape[0],
                    'min_timestamp': df.index.min().isoformat(),
                    'max_timestamp': df.index.max().isoformat(),
                }

        return {
            'start_time': self.start_time,
            'dfs': dfs_status,
        }

    def get_df_ohlcv(self, exchange=None, market=None, interval=None, price_type=None):
        self.logger.info('get_df_ohlcv {} {} {} {}'.format(exchange, market, interval, price_type))

        key = 'ohlcv,exchange={},market={},interval={},price_type={}'.format(exchange, market, interval, price_type)
        fetcher = self.fetcher_builder.create_fetcher(exchange=exchange, logger=self.logger)

        with self._get_lock(key):
            df = self.dfs.get(key)

            df = fetcher.fetch_ohlcv(
                df=df,
                start_time=self.start_time,
                interval_sec=interval,
                market=market,
                price_type=price_type
            )

            self.dfs[key] = df

        return df

    def get_df_fr(self, exchange=None, market=None):
        self.logger.info('get_df_fr {} {}'.format(exchange, market))

        if exchange == 'bybit':
            if re.search(r'\d', market):
                df = self.get_df_ohlcv(exchange, market, interval=60 * 60, price_type=None)
                df['fr'] = 0.0
                df = df[['fr']]
                return df

            df_pi = self.get_df_ohlcv(exchange, market, interval=60, price_type='premium_index')
            df_pi = df_pi.copy().reset_index()
            df_pi['timestamp'] = df_pi['timestamp'].dt.floor('8H')
            df_pi = pd.concat([
                df_pi.groupby('timestamp')['cl'].mean()
            ], axis=1)
            interest_rate = (0.0006 - 0.0003) / 3.0
            df_pi['fr'] = (df_pi['cl'] + (interest_rate  - df_pi['cl']).clip(-0.0005, 0.0005)).shift(2)
            df_pi = df_pi[['fr']].dropna()
            return df_pi

        key = 'fr,exchange={},market={}'.format(exchange, market)
        fetcher = self.fetcher_builder.create_fetcher(exchange=exchange, logger=self.logger)

        with self._get_lock(key):
            df = self.dfs.get(key)

            df = fetcher.fetch_fr(
                df=df,
                start_time=self.start_time,
                market=market,
            )

            self.dfs[key] = df

        return df