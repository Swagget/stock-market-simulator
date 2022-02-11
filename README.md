# stonks
This is designed to help you make up your own stock trading strategies and apply it to the past 30 years of the BSE (Bombay Stock Exchange).

## Obtaining Data
This project uses data from https://data.nasdaq.com/. The dataset_downloader.ipynb jupyter notebook explains how the data can be downloaded using an API key from NASDAQ Data Link (formerly known as quandl).

## Simulator
This allows you to buy and sell stocks at whatever time you would like in history. It also calcluates the total profits, realized and unrealized profits.

## Agent
This behaves as a human buying and selling stocks through history. It can be configured to buy and sell stocks based on any rules on any heuristics set on these stock prices.

# Future work
Using this we can test any set of rules and apply then throughout history.
Need to create more advanced heuristics to follow. For example: moving average, previous day-gains, percentage changes over time, total fluctions per n-day, etc.
