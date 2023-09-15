import datetime
import time

from selenium import webdriver
from selenium.webdriver.common.by import By

from utils.config import BASE_PATH


class LyraCrawler(object):

    URL = "https://app.lyra.finance/?utm_source=www#/trade/arbitrum/eth-usdc"

    def __init__(self):
        self.driver = self._init_driver()
        time.sleep(5)

    def _init_driver(self):
        op = webdriver.ChromeOptions()
        op.add_argument('headless')
        op.add_argument('--window-size=1920,1080')
        driver = webdriver.Chrome(options=op)
        driver.get(self.URL)
        return driver

    def _str_to_float(self, data_str):
        return float(data_str.replace(',', ''))

    def get_option_data(self):
        table = self.driver.find_element(By.CLASS_NAME, "css-xxfrxm")
        rows = table.find_elements(By.TAG_NAME, "tr")

        option_list = []
        current_price = None
        for row in rows:
            row_str = row.text
            if "ETH Price" in row_str:
                current_price = self._str_to_float(row_str[12:])
                continue
            if row_str and row_str[0] == '$':
                temp_list = row_str.split("\n")
                option_list.append((self._str_to_float(temp_list[0].strip("$")),
                                    self._str_to_float(temp_list[-1].strip("$"))))
        return option_list, current_price

    def traverse_option(self):
        buy_button = self.driver.find_element(By.XPATH, '//button[normalize-space()="Buy"]')
        sell_button = self.driver.find_element(By.XPATH, '//button[normalize-space()="Sell"]')
        call_button = self.driver.find_element(By.XPATH, '//button[normalize-space()="Call"]')
        put_button = self.driver.find_element(By.XPATH, '//button[normalize-space()="Put"]')

        option_dict = {}

        buy_button.click()
        call_button.click()
        option_list, current_price = self.get_option_data()
        option_dict["buy_call"] = option_list
        option_dict["buy_call_price"] = current_price

        buy_button.click()
        put_button.click()
        option_list, current_price = self.get_option_data()
        option_dict["buy_put"] = option_list
        option_dict["buy_put_price"] = current_price

        sell_button.click()
        call_button.click()
        option_list, current_price = self.get_option_data()
        option_dict["sell_call"] = option_list
        option_dict["sell_call_price"] = current_price

        sell_button.click()
        put_button.click()
        option_list, current_price = self.get_option_data()
        option_dict["sell_put"] = option_list
        option_dict["sell_put_price"] = current_price
        return option_dict

    def _convert_date(self, date_str):
        date = datetime.datetime.strptime(date_str, '%b %d')
        date = date.replace(year=2023)
        return date

    def get_option_date_list(self, start_date):
        option_date_list = []
        for i in range(4):
            option_date = start_date + datetime.timedelta(days=7 * i)
            option_date_list.append(option_date.strftime("%b %-d"))
        return option_date_list

    def _get_date_button(self):
        date_button = None
        all_button = self.driver.find_elements(By.CSS_SELECTOR, 'button')

        for button in all_button:
            if "Expires" in button.text:
                date_button = button
                break
        return date_button

    def traverse_date(self):
        # date_button = self._get_date_button()
        # date_button.click()
        # all_lis = self.driver.find_elements(By.CSS_SELECTOR, 'li')
        # result_dict = {}
        # for li in all_lis:
        #     li.click()
        #     date_str = li.text.split(",")[0]
        #     option_result = self.traverse_option()
        #     print(date_str, option_result)

        date_button = self._get_date_button()
        most_recent_date = self._convert_date(date_button.text.split(",")[0][8:])
        option_date_list = self.get_option_date_list(most_recent_date)

        result_dict = {}
        for date_str in option_date_list:
            date_button = self._get_date_button()
            date_button.click()
            time.sleep(2) # may reduce time
            all_lis = self.driver.find_elements(By.CSS_SELECTOR, 'li')
            for li in all_lis:
                if date_str in li.text:
                    li.click()
                    result_dict[date_str] = self.traverse_option()
                    break

        self.driver.close()
        return result_dict

    def main(self):
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        result_dict = self.traverse_date()

        file_path = BASE_PATH + "/data/lyra_option_data.json"
        with open(file_path, "a") as wf:
            wf.write(current_time + "\n")
            wf.write(str(result_dict) + "\n")


if __name__ == "__main__":
    lyra_crawler = LyraCrawler()
    lyra_crawler.main()
