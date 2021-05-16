import logging
import os
import sys
import time
from unittest import TestCase

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
from store import Store

class TestStore(TestCase):
    def test_get_df_ohlcv_bybit(self):
        logger = logging.getLogger(__name__)
        store = Store(start_time=time.time() - 24 * 60 * 60, logger=logger)
        df = store.get_df_ohlcv(exchange='bybit', market='BTCUSD', interval=60 * 60, price_type=None)
        self.assertEqual(df.shape[0], 23)

    def test_get_df_ohlcv_ftx(self):
        logger = logging.getLogger(__name__)
        store = Store(start_time=time.time() - 24 * 60 * 60, logger=logger)
        df = store.get_df_ohlcv(exchange='ftx', market='BTC-PERP', interval=60 * 60, price_type=None)
        self.assertEqual(df.shape[0], 23)

    def test_get_df_fr_bybit(self):
        logger = logging.getLogger(__name__)
        store = Store(start_time=time.time() - 32 * 60 * 60, logger=logger)
        df = store.get_df_fr(exchange='bybit', market='BTCUSD')
        self.assertEqual(df.shape[0], 3)

    def test_get_df_fr_bybit_inverse_futures(self):
        logger = logging.getLogger(__name__)
        store = Store(start_time=time.time() - 32 * 60 * 60, logger=logger)
        df = store.get_df_fr(exchange='bybit', market='BTCUSDU21')

        self.assertTrue((df['fr'] == 0).all())

    def test_get_df_fr_ftx(self):
        logger = logging.getLogger(__name__)
        store = Store(start_time=time.time() - 24 * 60 * 60, logger=logger)
        df = store.get_df_fr(exchange='ftx', market='BTC-PERP')
        self.assertEqual(df.shape[0], 24)

    def test_status(self):
        logger = logging.getLogger(__name__)
        store = Store(start_time=time.time() - 24 * 60 * 60, logger=logger)
        store.get_df_ohlcv(exchange='bybit', market='BTCUSD', interval=60 * 60, price_type=None)
        status = store.status()
        print(status)
        self.assertEqual(status['dfs']['ohlcv,exchange=bybit,market=BTCUSD,interval=3600,price_type=None']['count'], 23)