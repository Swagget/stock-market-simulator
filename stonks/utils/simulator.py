import pandas as pd
from collections import defaultdict
from datetime import datetime
from linetimer import CodeTimer

from stonks.utils.data_handler import data_handler

class simulator:
    """
    Needs breakdown by stock and respective profits.
    Can start with no limits on investing except only one stock of each item at a time.
    For buy and sell assume middle of the day both times.
    Assuming it's a current_date.
    You can buy/sell whenenver you want. taking "mid" which is avg of high and low
    No problem with buying at any point in time.
    For selling needs to check current holdings at that point in time.
    This way the algo can go through a stock from inception till latest date and interate for each stock.
    Date format is  "yyyy-mm-dd"
    Absoloute is value in rupees.
    Force all quantity to be positive integer > 0.  # Implement later
    """
    def __init__(self):
        self.total_invested_absolute = 0
        self.total_returns_absolute = 0
        self.stock_returns_realised_absolute = defaultdict(lambda : 0)
        # self.stock_invested_absolute = defaultdict(lambda : defaultdict(lambda : 0))
        # This is self.stock_invested_absolute["ticker_code"]["price"] = quantity (this is for imbalanced realised and unrealised profits calculate returns)
        self.stock_invested_absolute = defaultdict(lambda : 0)
        # This is self.stock_invested_absolute["ticker_code"] = price (this makes it easy to calculate returns)
        self.logs = pd.DataFrame(columns=["transactionID", "date", "ticker_code", "action", "quantity", "price", "net_returns", "net_invested"])
        self.current_holdings = defaultdict(lambda : 0)
        # self.current_date = 0

    @staticmethod
    def get_the_current_datetime():
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        return dt_string

    def buy(self, ticker_code, date = None, quantity = 1, buying_price = None):
        if date == None:
            date = simulator.get_the_current_datetime()
        if buying_price is None:
            stock_data = data_handler.get_stock_data(ticker_code = ticker_code, date = date)
            stock_price = stock_data["median"]
        else:
            stock_price = buying_price
        self.current_holdings[ticker_code] += quantity
        self.stock_invested_absolute[ticker_code] += stock_price * quantity
        self.total_invested_absolute += stock_price * quantity
        self.logs = self.logs.append({"transactionID" : len(self.logs), "date" : date, "ticker_code" : ticker_code,
                                       "action" : "buy", "quantity" : quantity, "price" : stock_price,
                                      "net_returns" : "-", "net_invested" : (quantity * stock_price)}, ignore_index=True)
        # print("self.stock_invested_absolute", self.stock_invested_absolute)
        return

    def sell(self, ticker_code, date = None, quantity = 1, selling_price = None):
        if date == None:
            date = simulator.get_the_current_datetime()
        if selling_price is None:
            # print(f"ticker_code: {ticker_code}")
            # print(f"date: {date}")
            stock_data = data_handler.get_stock_data(ticker_code = ticker_code, date = date)
            stock_price = stock_data["median"]
        else:
            stock_price = selling_price
        if self.current_holdings[ticker_code] < quantity:
            if self.current_holdings[ticker_code] > 0:
                print("Not enough stocks to perform this sell.")
            return

        returns_from_this_sell, initial_investment_removed = self.calculate_returns(ticker_code = ticker_code,
                                                              quantity_sold = quantity,
                                                              selling_price = stock_price)

        self.total_returns_absolute += returns_from_this_sell
        self.logs = self.logs.append({"transactionID" : len(self.logs),
                                      "date" : date,
                                      "ticker_code" : ticker_code,
                                       "action" : "sell",
                                      "quantity" : quantity,
                                      "price" : stock_price,
                                      "net_returns" : returns_from_this_sell,
                                      "net_invested" : -initial_investment_removed}, ignore_index=True)
        # self.current_holdings[ticker_code] # Number that is currently held
        # self.stock_invested_absolute[ticker_code] # Total iunvested
        # print("self.stock_invested_absolute : ", self.stock_invested_absolute)
        # print("self.current_holdings : ", self.current_holdings)
        self.stock_returns_realised_absolute[ticker_code] += returns_from_this_sell
        # print("self.stock_returns_realised_absolute", self.stock_returns_realised_absolute)
        # print("selling_price : ", selling_price)
        # print("avg_total_bought : ", avg_total_bought)
        # print("quantity : ", quantity)

        amount_of_investment_removed = initial_investment_removed

        self.total_invested_absolute -= amount_of_investment_removed
        self.stock_invested_absolute[ticker_code] -= amount_of_investment_removed
        self.current_holdings[ticker_code] -= quantity

        # print("return on this sale : ", (quantity * stock_price) - (initial_investment_removed))
        return

    """
    Bought 1 IPL at 90 rupees
    Bought 1 IPL at 100 rupees
    Sold 1 IPL at 105 rupees
    # Holding 2 at 120 price
    
    # 240 - 190  = 50 unrealised
    
    realised is ? 15
    unrealised is also ? 5
    
    If I assume I sold one over the other then realised and unrealised will have different ratios based on which one I'm assuming I sold
    The better logic would be to take the mean, that way realised profits  and unrealised profits will always be in the ratio of how many stocks were sold. 
    
    
    How much have I invested in IPL that I have not sold.
    Achyuth : Take the mean of the shares bought.
    
    Bought pepsi 100 at 20 rupees each
    Bought pepsi 10 at 1000 rupees each
    Sold 10 at 900
    Sold 10 at 800
    Sold 10 at 100
    
    realised ?
    unrealised ? 
    absolute_profits : realised + unrealised
    
    """
    def get_current_value_invested_per_stock(self, ticker_code):
        return self.stock_invested_absolute[ticker_code]/self.current_holdings[ticker_code]

    def calculate_returns(self, ticker_code, quantity_sold, selling_price):
        # By default assums you're selling the cheapest stock that you bought first.
        # IDK why but this feels logical also not sure if this makes nay difference whatsoever.
        # The only difference is that this balances your total returns towards realised profits. the otherway around will push it towards unrealised profits.
        # I'm not doing unrealised profit, maybe later.

        # New logic Assume sold  is compared against is the average of all stocks bought.

        amount_invested_in_stocks_that_are_being_sold = self.get_current_value_invested_per_stock(ticker_code = ticker_code) * quantity_sold

        total_returns = (quantity_sold * selling_price) - amount_invested_in_stocks_that_are_being_sold

        initial_investment_removed = (self.stock_invested_absolute[ticker_code] / self.current_holdings[ticker_code]) * quantity_sold

        return total_returns, initial_investment_removed

        # while quantity_sold > 0: # possible infinite loop is destroying the key (the key is the price at which stocks were bought) doesn't work.
        #     sorted_keys = sorted(list(current_holdings.keys()))
        #     if len(sorted_keys) == 0:
        #         print("Not enough units to be sold")
        #         break
        #     for key in sorted_keys:
        #         if current_holdings[key] == 0:
        #             del current_holdings[key]
        #             continue
        #         if current_holdings[key] >= quantity_sold:
        #             quantity_sold = 0
        #             current_holdings[key] -= quantity_sold
        #         else:
        #             current_holdings[key] = 0
        #             quantity_sold -= current_holdings[key]
        #     sorted_price_keys =
        # self.current_holdings = updated_holdings
        # return absoloute_returns

    def get_holdings_as_of_date(self, date):
        return

    def get_total_valuation_on_date(self):
        return
        return portfolio_valuation
    
    def get_stock_price_on_date(self):
        return
        return stock_price

