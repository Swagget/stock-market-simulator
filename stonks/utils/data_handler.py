import pandas as pd
import quandl
import pathlib
from tqdm import tqdm
import os
import pandas_ta as ta

class data_handler:
    @classmethod
    def get_stock_data(cls, source="quandl", dataset="BSE", ticker_code = "BOM523395", date = None):
        to_return = data_disk_interface.get_stock_data(source=source, dataset = dataset,
                                                       ticker_code = ticker_code,
                                                       date = date)
        to_return = preprocessor.basic_preprocessing(to_return)
        to_return = indicator_handler().attach_basic_indicators(to_return)
        return to_return

    @classmethod
    def get_ticker_code_list(cls, source="quandl", dataset="BSE"):
        cls.stocks_df = data_disk_interface.get_stocks_metadata(source = source, dataset = dataset)
        return list(cls.stocks_df["CODE"].values)

class data_disk_interface:
    """
    Standardising nomenclature:
    source : The website/place where the dataset came from, like "quandl"
    dataset : The name of the dataset itself, like "BSE" (from quandl)
    ticker_code : The ticker code of the stock, like "BOM523395"
    """
    def __init__(self):
        quandl.ApiConfig.api_key = "please enter your quandl api key"
        return

    @classmethod
    def download_data(cls):
        return "No"

    @classmethod
    def download_data_please(cls, source = "quandl", dataset = "BSE"):
        cls.stocks_df = cls.get_stocks_metadata(source = source, dataset = dataset)
        for _, row in tqdm(cls.stocks_df.iterrows()):
            if cls.check_if_downloaded(ticker_code = row["CODE"], source = source, dataset = dataset):
                continue
            try:
                if source == "quandl":
                    cls.download_single_quandl_data_and_save(dataset=dataset, ticker_code=row["CODE"])
            except KeyboardInterrupt:
                print('Interrupted')
                break
            except:
                print("Something failed. Code is :", row["CODE"])  # Append to text file
                cls.append_broken_code_to_failed_download_text_file(source=source,
                                                                ticker_code=row["CODE"])
            # break

    @classmethod
    def get_stocks_metadata(cls, source="quandl", dataset="BSE"):
        appropriate_directory = "/".join([source, dataset])
        cls.stocks_df = pd.read_table("./data/" + appropriate_directory + "/metadata/all_tickerIds.txt", delimiter="|")
        return cls.stocks_df

    @classmethod
    def get_file_path(cls, source="quandl", dataset="BSE", ticker_code = "BOM523395"):
        return "./data/" + "/".join([source, dataset, ticker_code]) + ".csv"

    @classmethod
    def get_stock_data(cls, source="quandl", dataset="BSE", ticker_code = "BOM523395", date = None):
        path_to_df = cls.get_file_path(source=source, dataset=dataset, ticker_code = ticker_code)
        df = pd.read_csv(path_to_df)
        if date is not None:
            df = df[df["Date"] == date]
        return df

    @classmethod
    def check_if_downloaded(cls, ticker_code, source = "quandl", dataset = "BSE"):
        path_to_df = cls.get_file_path(source=source, dataset=dataset, ticker_code = ticker_code)
        if os.path.isfile(path_to_df):
            return True
        return False

    # import os
    @classmethod
    def delete_file(cls, ticker_code, source = "quandl", dataset = "BSE"):
        path_to_df = cls.get_file_path(source=source, dataset=dataset, ticker_code = ticker_code)
        if os.path.isfile(path_to_df):
            os.remove(path_to_df)
            return
        else:
            print(f"This file does not exist. Path : {path_to_df}")
            return

    @classmethod
    def download_single_quandl_data_and_save(cls, dataset, ticker_code):
        quandl_location = dataset + "/" + ticker_code
        downloaded_data = quandl.get(quandl_location)
        path_to_save_data = pathlib.Path("./data/quandl/" + quandl_location + ".csv")
        path_to_save_data.parent.mkdir(parents=True, exist_ok=True)
        downloaded_data.to_csv(path_to_save_data)
        # print("Sucessfully downloaded and saved : ", quandl_location)

    @classmethod
    def append_broken_code_to_failed_download_text_file(cls, source, ticker_code):
        actual_text_file_path = "./data/" + source + "/failed_downloads.txt"
        with open(actual_text_file_path, "a+") as file_object:
            file_object.seek(0)
            # If file is not empty then append '\n'
            data = file_object.read(100)
            if len(data) > 0:
                file_object.write("\n")
            # Append text at the end of file
            file_object.write(ticker_code)

class preprocessor:
    """
    list_of_indicators needs to be clarified better.
    """
    def __init__(self, list_of_indicators):
        return

    @classmethod
    def attach_median(cls, df):
        new_df = df.copy()
        new_df["median"] = (new_df["High"] + new_df["Low"]) / 2
        return new_df

    @classmethod
    def basic_preprocessing(cls, df):
        df = cls.attach_median(df)
        return df


class indicator_handler:
    """
    This is where the names of the indicator's nomenclature needs to be specified.
    format : "key:{value},key:{value}..."
    """
    def __init__(self, list_of_indicators = None):
        if list_of_indicators is not None:
            self.list_of_indicators = list_of_indicators # This should be a list of wanted indicators
        else:
            self.list_of_indicators = [{"indicator" : "SMA", "length" : 20, "offset" : 0}]

    @classmethod
    def generate_indicator(cls, time_series, indicator = "SMA", length = 20, offset = 0):
    # def generate_indicator(self, time_series, **kwargs):
        if indicator == "SMA":
            # print("time_series : ", time_series)
            return ta.sma(time_series, length=length, offset = offset)

    def attach_basic_indicators(self, df, list_of_indicators = None):
        # if len(df) == 1:
        # try:
        #     print(f"shape of the df is {df.shape}")
        # except:
        #     print(df)
        if list_of_indicators is None:
            list_of_indicators = self.list_of_indicators
        for indicator in list_of_indicators:
            col_name = ",".join([f"{key}:{value}" for key, value in indicator.items()])
            df[col_name] = indicator_handler.generate_indicator(df["Close"], **indicator) # @hardcode Make sure "Close" is adjustable
        return df