from stonks.utils.simulator import simulator
from stonks.utils.data_handler import data_handler, indicator_handler
from tqdm import tqdm
import random
from linetimer import CodeTimer

from deprecated import deprecated


class agent:
    """
    Given:
        All info this needs can be obtained from the data_handler.
        All actions this wants to execute can be done through the simulator.
        I will append the SMA(simple moving average) for 20 days.

    Controls/Constraints temporarily until the next level:
        It should have infinite money.
        It should handle one stock at a time.
        It should handle one day at a time.
        It should follow the rules/strategy I set for it.
        It has access to moving average over 20 days.
        I'm not sure if I should throw all the data I can generate at it or should it ask? Throwing it all is the best bet.

    Functions:
        Just buy and sell.
        It will have it's own instance of a simulator.
        When it's initialised it will need a list of indicators it will be fed.


    """
    def __init__(self, list_of_indicators = None, rules_to_follow = None):
        self.sim = simulator()
        self.indicator_handler = indicator_handler(list_of_indicators)
        self.rules = rules_to_follow
        self.date = "2011-11-30"
        self.failed_ticker_codes = []


    def set_rules_to_follow(self, rules_to_follow):
        """

        :param rules_to_follow:
        A list of rules. Each rule is a condition and action.
        If a condition is satisfied then the action is recommended.
        The order of the rules is 1>2>3. Whichever condition is satisfied it recommends that action.
        format : [{"action" : "{buy/sell/nothing}", "operator"}]

        :return:
        """
        self.rules = rules_to_follow

    def set_basic_strat_1(self):
        # This seems to cover pretty much everything for a single day. But needs a time adjustment parameter.
        # Also needs and and or operators for the rules.
        # But implementing all that might not help for the initial experiment and I can't think of a way for the reinforcement algo to work with it.
        # That said I have to come up with new ways for the algo to generate it's own rules and test them. I'd rather not look at previous research
        # I should be able to come up with something, and then I'll see what other people came up with.
        buy_rule = {"action" : "buy", "LHS" : "Close", "operation" : ">", "RHS" : "indicator:SMA,length:20,offset:0", "LHS modifier" : 1, "RHS modifier" : 1.04}
        sell_rule = {"action" : "sell", "LHS" : "Close", "operation" : "<=", "RHS" : "indicator:SMA,length:20,offset:0", "LHS modifier" : 1, "RHS modifier" : 1}
        # The Format of the rhs came from the indicator handler class documentation.
        self.set_rules_to_follow([buy_rule, sell_rule])

    @deprecated(reason="This is cassed far too many times and is causing 3x time complexity. "
                       "If there's a way to truly inline this that would be great. "
                       "For now all this code is in execute_single_stock.")
    def execute_rules(self, stock_data_till_today):
        """
        Current constraint is the the rules can only be tested for a single day.
        The agent will be able to control the date.
        This will execute how much to buy/sell and at what price to avoid further fetching.


        :param stock_data_till_today: This is a df with a single stocks data from inception till today.
        :return:
        """
        with CodeTimer('Executing the "execute_rules" function', silent=False):

            with CodeTimer('Grabbing today\'s data', silent=False):
                todays_data = stock_data_till_today[stock_data_till_today["Date"] == self.date].iloc[0].to_dict()
                to_return = {"action" : "buy", "stock_price" : todays_data["median"], "quantity" : 1}
            with CodeTimer('Iterating through the rules', silent=False):
                for rule in self.rules:
                    lhs = todays_data[rule["LHS"]]*rule["LHS modifier"]
                    rhs = todays_data[rule["RHS"]]*rule["RHS modifier"]
                    if eval(f"lhs{rule['operation']}rhs"):
                        to_return["action"] = rule["action"]
                        return to_return
                    to_return["action"] = "hold"
            return to_return

    def react(self, stock_data_till_today):
        """
        There are  multiple ways for the agent to use the stock data:
        1. Use a single day's data.
        2. use the entire history or to an arbitrary point of time.

        Both these require vastly different inputs? I can create a way to cover the 2 and still cover the 1.
        But idk why that's helpful. The most generic solution is to give the agent all the data and it'll
        use only what it needs.

        Also does the agent need the simulator data? Probably does but I can't figure out why. Also irrelevant to the
        parameters of this function because any data it needs about this can come from self.sim.

        :param stock_data_till_today: This is a df with a single stocks data from inception till today.

        :return: Action that should be done today. 3 things : buy, sell, nothing.
        Q: Is that all?
        A: No, but it's enough for now.
        """

    def single_observation(self, stock_observation):
        # execute strategy and perform simulator operations.
        # action = self.run_current_strategy(relevant_information)
        return


    def run(self, ticker_code = None, date = None, number_of_stocks = 10):
        """
        Run the agent if anything is unspecified then it runs it iteratively for every single ticker_code or date or both.
        :return:
        """
        # lambda_rule_executor = lambda x:self.execute_rules(x[x["Date"]<=self.date])
        if (date is None) and (ticker_code is None): # For now only dealing with this case.
            all_ticker_codes = data_handler.get_ticker_code_list()
            with CodeTimer('Total processing time', silent = False, unit = "s"):
                number_of_stocks = min(number_of_stocks,len(all_ticker_codes))
                for ticker_code in tqdm(random.sample(all_ticker_codes, number_of_stocks)):
                    with CodeTimer('Processing a stock', silent = True, unit = "s"):
                        try:
                            with CodeTimer('Reading data', silent = True):
                                stock_df = data_handler.get_stock_data(ticker_code = ticker_code)
                            self.execute_single_stock(stock_df, ticker_code)
                        except KeyboardInterrupt:
                            print('Interrupted')
                            break
                        except:
                            print("Failed ticker_code : ", ticker_code)
                            self.failed_ticker_codes.append(ticker_code)
                        # self.run_single_stock_for_each_date(stock_df, ticker_code, lambda_rule_executor = lambda_rule_executor)

    def execute_single_stock(self, stock_df, ticker_code):
        # for date in tqdm(stock_df["Date"].values):
        for date in stock_df["Date"].values:
            # This needs to be corrected to go though dates individually.
            # This will cause missing data bugs, weekends/holidays/unknown reasons this missing data needs to be handled
            # I need to find out how platforms handle this.
            # Specifically how the indicators like 20-day moving average handle this.

            self.date = date
            # with CodeTimer('Executing rules', silent = False):
            #     recommended_action = self.execute_rules(stock_df[stock_df["Date"]<=self.date])

            # with CodeTimer('Executing rules lambda style', silent = False):
            #     execute_rule_lambda = lambda x:self.execute_rules(x[x["Date"]<=self.date])
            #     recommended_action = execute_rule_lambda(stock_df)

            # with CodeTimer('Executing rules smart lambda style', silent = False):
            #     recommended_action = lambda_rule_executor(stock_df)

            with CodeTimer('Executing rules inline', silent = True): # This is just too good to let go of. Despite uglyness.
                todays_data = stock_df[stock_df["Date"] == self.date].iloc[0].to_dict()
                recommended_action = {"action": "buy", "stock_price": todays_data["median"], "quantity": 1}
                for rule in self.rules:
                    lhs = todays_data[rule["LHS"]] * rule["LHS modifier"]
                    rhs = todays_data[rule["RHS"]] * rule["RHS modifier"]
                    if eval(f"lhs{rule['operation']}rhs"):
                        recommended_action["action"] = rule["action"]
                        # return recommended_action
                    recommended_action["action"] = "hold"
            #         # return recommended_action

            if recommended_action["action"] == "buy":
                if self.sim.current_holdings[ticker_code] > 0:continue # @hardcode Setting arbitrary rule that it can't hold more than 1 at a time. TODO don't do this. at least implement it as a rule
                self.sim.buy(ticker_code=ticker_code, date = self.date,
                             buying_price = recommended_action["stock_price"],
                             quantity = recommended_action["quantity"])
            if recommended_action["action"] == "sell":
                self.sim.sell(ticker_code=ticker_code, date = self.date,
                         selling_price = recommended_action["stock_price"],
                         quantity = recommended_action["quantity"])













    def calculate_returns(self, date):
        """
        Go through all the logs keep calculating the returns and measure against inflation, also get the logged returns.
        This can and should be a function of the simulator.
        :param date:
        :return:
        """