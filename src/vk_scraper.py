import os
from src import printcolors as pc
import pandas as pd
from bs4 import BeautifulSoup
import time
from datetime import datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
from ast import literal_eval
from os import listdir
from tqdm import tqdm
import deepl
from src.git_credentials import GitCredentialsHandler


class VkScraper:

    def __init__(self, targets="no target") -> None:
        self.key = None
        self.targets = targets
        self.start_date = datetime.timestamp(datetime.strptime("10/10/2006", "%d/%m/%Y"))
        self.end_date = None
        pc.printout("\nYour targets are: \n", pc.YELLOW)
        pc.printout(str(self.targets) + "\n", pc.YELLOW)

    def set_targets(self) -> None:
        pc.printout("Please insert new targets: \n", pc.YELLOW)
        self.targets = input().split()
        pc.printout("Your targets are: \n", pc.YELLOW)
        pc.printout(str(self.targets) + "\n", pc.YELLOW)

    def show_targets(self) -> None:
        pc.printout("Your targets are: \n", pc.YELLOW)
        pc.printout(str(self.targets) + "\n", pc.YELLOW)

    def set_dates(self) -> None:
        pc.printout("Please insert starting date (dd/mm/yyyy format): \n", pc.YELLOW)
        start_date = input()
        if start_date:
            self.start_date = datetime.timestamp(datetime.strptime(start_date, "%d/%m/%Y"))
        else:
            self.start_date = None

        pc.printout("Please insert end date or press enter (dd/mm/yyyy format): \n", pc.YELLOW)
        pc.printout("NB The end date will not be included\n", pc.YELLOW)
        end_date = input()
        if end_date:
            self.end_date = datetime.timestamp(datetime.strptime(end_date, "%d/%m/%Y"))
            if self.start_date >= self.end_date:
                pc.printout("WARNING:Your end date is earlier than the start date\n",
                            pc.RED)
        else:
            self.end_date = None

    def show_dates(self) -> None:
        if isinstance(self.start_date, float):
            pc.printout("Your start date is: \n", pc.YELLOW)
            pc.printout("{}\n".format(datetime.fromtimestamp(self.start_date)), pc.YELLOW)
            if isinstance(self.end_date, float):
                pc.printout("Your end date is: \n", pc.YELLOW)
                pc.printout("{}\n".format(datetime.fromtimestamp(self.end_date)), pc.YELLOW)
        else:
            pc.printout("No dates to show\n", pc.YELLOW)

    @staticmethod
    def scraped_dates_transformer(date: str) -> datetime.timestamp:
        small_hours = ["one", "two", "three", "four"]
        days = ["today", "yesterday"]
        if "minutes" in date.split(" "):
            now = datetime.now()
            converted_time = now.replace(second=0, microsecond=0) + timedelta(hours=now.minute // 30)
        elif date.split(" ")[0] in small_hours:
            time_difference = int(small_hours.index(date.split(" ")[0])) + 1
            now = datetime.now()
            _round = now.replace(second=0, microsecond=0) + timedelta(hours=now.minute // 30)
            converted_time = _round - timedelta(hours=time_difference)
        elif date.split(" ")[0] in days:
            time_difference = int(days.index(date.split(" ")[0]))
            now = datetime.now()
            hours, minutes = date.split(" ")[-2].split(":")
            correct_time = now.replace(second=0, microsecond=0, minute=int(minutes), hour=int(hours))
            converted_time = correct_time - timedelta(days=time_difference)
        elif "at" in date:
            date = date.replace(" at", "")
            converted_time = datetime.strptime(date, "%d %b %I:%M %p")
            converted_time = converted_time.replace(year=2022)
        else:
            converted_time = datetime.strptime(date, "%d %b %Y")
        return datetime.timestamp(converted_time)

    @staticmethod
    def extract_correct_last_date(web_element: WebElement) -> str:
        dates_html = web_element.get_attribute("innerHTML")
        dates_soup = BeautifulSoup(dates_html, "html.parser")
        date = dates_soup.find("span", {"class": "rel_date"})
        try:
            return date["abs_time"]
        except KeyError:
            return date.text

    def retrieve_target_posts(self, target_url: str, start_date: float) -> webdriver:
        os.environ["GH_TOKEN"] = GitCredentialsHandler().retrieve_key()
        options = webdriver.FirefoxOptions()
        # options.add_argument("--headless")
        options.add_argument("--incognito")
        service = FirefoxService(executable_path=GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=options)
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        """
        scroll_pause_time = 0.5
        driver.get(target_url)
        time.sleep(5)
        converted_time = datetime.timestamp(datetime.now())
        iter_number = 0
        while converted_time > start_date:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            if (iter_number % 25) == 0:
                post_elements = driver.find_elements(By.CLASS_NAME, "post_link")
                try:
                    date = self.extract_correct_last_date(post_elements[-1])
                    pc.printout(date + "\n", pc.BLUE)
                    converted_time = self.scraped_dates_transformer(date)
                except IndexError:
                    converted_time = converted_time
            iter_number += 1
            time.sleep(scroll_pause_time)
        return driver

    @staticmethod
    def from_sel_to_bs(driver: webdriver) -> list:
        soup_posts = []
        post_elements = driver.find_elements(By.CLASS_NAME, "_post_content")
        pc.printout("-" * 80 + "\n", pc.BLUE)
        pc.printout("Saving posts from HTML...\n", pc.BLUE)
        for element in tqdm(post_elements, bar_format='{l_bar}{bar:40}{r_bar}{bar:-10b}'):
            html = element.get_attribute("innerHTML")
            soup = BeautifulSoup(html, "html.parser")
            soup_posts.append(soup)
        driver.close()
        return soup_posts

    def extract_clean_data(self, unclean_posts: list) -> dict:
        data_dict = {"date": [], "text": [], "likes": [], "href": []}
        pc.printout("Extracting data...\n", pc.BLUE)
        for post in tqdm(unclean_posts, bar_format='{l_bar}{bar:40}{r_bar}{bar:-10b}'):
            data_href = post.find("a", {"class": "post_link"})
            if data_href:
                data_dict["href"].append("https://vk.com{}".format(data_href["href"]))
                try:
                    date = data_href.find("span", {"class": "rel_date"})["abs_time"]
                    date = self.scraped_dates_transformer(date)
                    data_dict["date"].append(date)
                except KeyError:
                    date = data_href.find("span", {"class": "rel_date"}).text
                    date = self.scraped_dates_transformer(date)
                    data_dict["date"].append(date)
            text = post.find("div", {"class": "wall_post_cont"})
            if text:
                text = text.find("div", {"class": "wall_post_text"})
                if text:
                    data_dict["text"].append(text.text)
                else:
                    data_dict["text"].append(None)
            likes = post.find_all("div", {"class": "PostButtonReactions__title"})
            if likes:
                likes = likes[0].text
                if likes:
                    likes = int(likes.replace(",", ""))
                else:
                    likes = None
                data_dict["likes"].append(likes)
        return data_dict

    def date_filter(self, target_dict: dict) -> pd.DataFrame:
        pc.printout("Date filtering in progress\n", pc.BLUE)
        # find a more intelligent way than just copying a df to avoid pandas error
        target_df = pd.DataFrame.from_dict(target_dict)
        filtered_df = target_df[target_df["date"] > self.start_date].copy()
        if self.end_date:
            filtered_df = filtered_df.loc[filtered_df["date"] <= self.end_date].copy()
        else:
            pass
        filtered_df["date"] = pd.to_datetime(filtered_df["date"], unit="s", utc=True)
        filtered_df["date"] = filtered_df["date"].dt.tz_convert(tz="Europe/Moscow")
        pc.printout("Date filtering completed\n", pc.BLUE)
        pc.printout("-" * 80 + "\n", pc.BLUE)
        return filtered_df

    def retrieve_targets_posts(self) -> None:
        for target in self.targets:
            pc.printout(target, pc.RED)
            url_target = "https://vk.com/{}".format(target)
            driver = self.retrieve_target_posts(url_target, self.start_date)
            post_soup = self.from_sel_to_bs(driver)
            target_dict = self.extract_clean_data(post_soup)
            clean_target_df = self.date_filter(target_dict)
            clean_target_df.to_csv("./outputs/{}.csv".format(target), index=False, encoding='utf-8-sig')

    @staticmethod
    def read_check_credentials() -> tuple:
        with open("./credentials/DeepL_key.txt", "r") as handle:
            key_dict = literal_eval(handle.read())
            if key_dict['DeepL_key']:
                return True, key_dict['DeepL_key']
            else:
                return False, None

    def check_target_csv(self) -> bool:
        for target in self.targets:
            target = "{}.csv".format(target)
            if target in listdir("./outputs"):
                return True
            else:
                return False

    def update_credentials(self):
        check, self.key = self.read_check_credentials()
        if not check:
            pc.printout("No API key credentials stored\n", pc.YELLOW)
            pass
        else:
            pc.printout("Please, insert your new DeepL API key: \n", pc.YELLOW)
            self.key = input()
            with open("./credentials/DeepL_key.txt", "r") as handle:
                key_dict = literal_eval(handle.read())
            key_dict['DeepL_key'] = self.key
            with open("./credentials/DeepL_key.txt", "w") as handle:
                handle.write(str(key_dict))

    def ask_write_credentials(self) -> None:
        check, self.key = self.read_check_credentials()
        if check:
            pass
        else:
            pc.printout("Please, insert your DeepL API key: \n", pc.YELLOW)
            self.key = input()
            with open("./credentials/DeepL_key.txt", "r") as handle:
                key_dict = literal_eval(handle.read())
            key_dict['DeepL_key'] = self.key
            with open("./credentials/DeepL_key.txt", "w") as handle:
                handle.write(str(key_dict))

    def deepl_translate(self) -> None:
        for target in self.targets:
            pc.printout("-" * 80 + "\n")
            pc.printout("Starting {} Translation\n".format(target), pc.YELLOW)
            eng_text = []
            target_path = "./outputs/{}.csv".format(target)
            target_df = pd.read_csv(target_path)
            for text in tqdm(target_df["text"], bar_format='{l_bar}{bar:40}{r_bar}{bar:-10b}'):
                translator = deepl.Translator(self.key)

                result = translator.translate_text(str(text), target_lang="EN-US")
                eng_text.append(result.text)
            target_df["eng_text"] = eng_text
            target_df = target_df[["date", "text", "eng_text", "likes", "href"]]
            target_df.to_csv("./outputs/{}_translated.csv".format(target), index=False, encoding='utf-8-sig')
            pc.printout("Translation Saved!\n", pc.YELLOW)

    def translating_target_csv(self) -> None:
        self.ask_write_credentials()
        csv_check = self.check_target_csv()
        if not csv_check:
            pc.printout("One or more target CSVs are not present", pc.RED)
            return None
        else:
            self.deepl_translate()
