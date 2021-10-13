from bullets.data_source.data_source_interface import DataSourceInterface, Resolution
from bullets.runner import Runner
from datetime import datetime, timedelta

import math

class Indicators:
    def __init__(self, data_source: DataSourceInterface):
        self.data_source = data_source

    def sma(self, symbol: str, period: int, date: datetime = None):
        """
        Calculates the Simple Moving Average
        Args:
            symbol: Stock symbol
            period: number of days for the average
            date: Date of average / start date
        Returns:
            sma: Average stock price for the given range
        """

        if date is None:
            date = self.data_source.timestamp
        else:
            date = date

        values = []

        for x in range(period):
            #Make sure market is open
            while not Runner._is_market_open(date, Resolution.DAILY):
                date -= timedelta(days=1)

            ##Go back one day
            date -= timedelta(days=1)

        for x in range(period):
            # Make sure market is open
            while not Runner._is_market_open(date, Resolution.DAILY):
                date += timedelta(days=1)

            #Fetch stock value
            price = self.data_source.get_price(symbol=symbol, timestamp=date)
            if price is not None:
                values.append(price)

            ##Go forward one day
            date += timedelta(days=1)

        #Calculate SMA
        sma = sum(values) / len(values)

        return sma
    
    def wma(self, symbol: str, period: int, date: datetime = None):
        """
        Calculates the Weight Moving Average
        Args:
            symbol: Stock symbol
            period: number of days for the average
            date: Date of average / start date
        Returns:
            wma: Average stock price weight for the given range
        """
        if date is None:
            date = self.data_source.timestamp
        else:
            date = date

        weight_total = 0

        wma = 0

        for x in range(period):
            weight_total += x + 1

        for x in range(period):
            # Make sure market is open
            while not Runner._is_market_open(date, Resolution.DAILY):
                date -= timedelta(days=1)

            # Go back one day
            date -= timedelta(days=1)

        for x in range(period):
            # Make sure market is open
            while not Runner._is_market_open(date, Resolution.DAILY):
                date += timedelta(days=1)

            # Fetch stock value
            price = self.data_source.get_price(symbol=symbol, timestamp=date)

            if price is not None:
                current_weight = ((x + 1) / weight_total)
                print("Price: ", price, " Weight: ", x + 1, " / ", weight_total, " = ", current_weight)
                wma += price * current_weight

            # Go forward one day
            date += timedelta(days=1)

        return wma

    def ema(self, symbol: str, period: int, date: datetime = None, smoothing: int = 2):
        """
        Calculates the Simple Moving Average
        Args:
            symbol: Stock symbol
            period: number of days for the average
            date: Date of average / start date
            smoothing: weighted importance of latest data, higher number gives more weight to more recent data
        Returns:
            ema: Exponential average stock price for the given range
        """

        if date is None:
            date = self.data_source.timestamp
        else:
            date = date

        multiplier = smoothing/(period + 1)

        for x in range(period):
            #Make sure market is open
            while not Runner._is_market_open(date, Resolution.DAILY):
                date -= timedelta(days=1)

            ##Go back one day
            date -= timedelta(days=1)

        ema = self.sma(symbol, period, date)
        date += timedelta(days=1)

        for x in range(period):
            # Make sure market is open
            while not Runner._is_market_open(date, Resolution.DAILY):
                date += timedelta(days=1)

            price = self.data_source.get_price(symbol=symbol, timestamp=date)
            if price is not None:
                ema = price*multiplier + ema*(1-multiplier)

            ##Go forward one day
            date += timedelta(days=1)

        return ema

    def macd(self, symbol, date: datetime = None):
        """
        Calculates the Simple Moving Average
        Args:
            symbol: Stock symbol
            date: Calculated date / start date
        Returns:
            MACD
        """

        if date is None:
            date = self.data_source.timestamp
        else:
            date = date

        return self.ema(symbol, 12, date) - self.ema(symbol, 26, date)



    def stdDev(self, symbol: str, period: int, date: datetime = None, smoothing: int = 2):
        stdDev = 0.0
        differences = []
        variance = 0.0
        ema = Indicators.ema(symbol,period,date,smoothing)
        # table of market price for each day in the period
        values = []

        for x in range(period):
            # Make sure market is open
            while not Runner._is_market_open(date, Resolution.DAILY):
                date -= timedelta(days=1)

            ##Go back one day
            date -= timedelta(days=1)

        for x in range(period):
            # Make sure market is open
            while not Runner._is_market_open(date, Resolution.DAILY):
                date += timedelta(days=1)

            # fill each value
            price = self.data_source.get_price(symbol=symbol, timestamp=date)
            if price is not None:
                values.append(price)
            ##Go forward one day
            date += timedelta(days=1)

        # calculate difference between each value and ema
        for x in differences:
            differences[x] = values[x] - ema
            differences[x] = differences[x] * differences[x]
            variance += differences[x]

        # calculate variance
        variance = variance / len(differences)

        #calculate standard deviation
        stdDev = math.sqrt(variance)

        return stdDev


