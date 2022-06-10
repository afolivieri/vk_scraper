from src import printcolors as pc
import bs4
import pandas as pd
from bs4 import BeautifulSoup
# from pyvirtualdisplay import Display removed for multi OS operability
import time
from datetime import datetime
from datetime import timedelta
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from ast import literal_eval
from os import listdir
from tqdm import tqdm
import deepl


class VkScraper:

    def __init__(self, targets: object) -> None:
        self.key = None
        self.targets = targets
        self.start_date = datetime.timestamp(datetime.strptime("10/10/2006", "%d/%m/%Y"))
        self.end_date = None
        # API discarded, credentials not needed
        # self.read_credentials()
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
    def extract_correct_last_date(soup: bs4.BeautifulSoup.find_all) -> str:
        dates = []
        for post in soup:
            dates_soup = post.find("a", {"class": "post_link"})  # .find("span", {"class": "rel_date"})
            if dates_soup:
                date = dates_soup.find("span", {"class": "rel_date"})
                try:
                    dates.append(date["abs_time"])
                except KeyError:
                    dates.append(date.text)
        return dates[-1]

    def retrieve_target_posts(self, target_url: str, start_date: float) -> list:
        # removed for multi OS operability
        # display = Display(visible=False, size=(800, 600))
        # display.start()
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=options)
        scroll_pause_time = 0.5
        driver.get(target_url)
        last_height = driver.execute_script("return document.body.scrollHeight")
        converted_time = datetime.timestamp(datetime.now())
        _posts = []
        while converted_time > start_date:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            posts = soup.find_all("div", {"class": "_post"})
            try:
                date = self.extract_correct_last_date(posts)
                converted_time = self.scraped_dates_transformer(date)
            except IndexError:
                converted_time = converted_time
            _posts = posts
            time.sleep(scroll_pause_time)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        return _posts

    def extract_clean_data(self, unclean_posts: list):  # -> pd.DataFrame:
        data_dict = {"date": [], "text": [], "likes": [], "href": []}
        for post in unclean_posts:
            data_href = post.find("a", {"class": "post_link"})
            if data_href:
                data_dict["href"].append("https://vk.com{}".format(data_href["href"]))
                try:
                    date = data_href.find("span", {"class": "rel_date"})["abs_time"]
                    date = self.scraped_dates_transformer(date)
                    data_dict["date"].append(date)
                    pc.printout(str(datetime.fromtimestamp(date)) + "\n", pc.BLUE)
                except KeyError:
                    date = data_href.find("span", {"class": "rel_date"}).text
                    date = self.scraped_dates_transformer(date)
                    data_dict["date"].append(date)
                    pc.printout(str(datetime.fromtimestamp(date)) + "\n", pc.BLUE)
            text = post.find("div", {"class": "wall_post_cont"})
            if text:
                text = text.find("div", {"class": "wall_post_text"})
                if text:
                    data_dict["text"].append(text.text)
                else:
                    data_dict["text"].append(None)
            likes = post.find_all("div", {"class": "PostButtonReactions__title"})
            if likes:
                data_dict["likes"].append(likes[0].text)
        return pd.DataFrame.from_dict(data_dict)

    def date_filter(self, target_df: pd.DataFrame) -> pd.DataFrame:
        # more intelligent way than just copying a df to avoid pandas error
        filtered_df = target_df[target_df["date"] > self.start_date].copy()
        if self.end_date:
            filtered_df = filtered_df.loc[filtered_df["date"] <= self.end_date].copy()
        else:
            pass
        filtered_df["date"] = pd.to_datetime(filtered_df["date"], unit="s", utc=True)
        filtered_df["date"] = filtered_df["date"].dt.tz_convert(tz="Europe/Amsterdam")
        return filtered_df

    def retrieve_targets_posts(self) -> None:
        for target in self.targets:
            pc.printout(target, pc.RED)
            url_target = "https://vk.com/{}".format(target)
            target_posts = self.retrieve_target_posts(url_target, self.start_date)
            target_df = self.extract_clean_data(target_posts)
            clean_target_df = self.date_filter(target_df)
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
            pc.printout("-" * 80)
            pc.printout("\nStarting {} Translation\n".format(target), pc.YELLOW)
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


"""
vk API isn't working as needed, only top 100 posts max return
    def store_credentials(self) -> None:
        pc.printout("Please insert VK token: \n", pc.YELLOW)
        self.token = input()
        with open("./config/credentials", "w") as handler:
            handler.write("token: {}\n".format(self.token))

    def read_credentials(self) -> None:
        with open("./config/credentials", "r") as handler:
            credentials = handler.readlines()
        if len(credentials[0].split()) != 2:
            pass
        else:
            self.token = credentials[0].split()[1]

    def start_session(self) -> None:
        self.session = vk.Session(access_token=self.token)
        self.api = vk.API(self.session, v=5.131)

    def retrieve_target_posts(self, target) -> None:
        posts = {"date": [], "text": [], "likes": [], "href": []}
        wall = self.api.wall.get(domain=target, count = 100)
        for post in wall["items"]:
            posts["date"].append(post["date"])
            posts["likes"].append(post["likes"]["count"])
            try:
                posts["text"].append(post["text"])
            except KeyError:
                pass
            o_id = post["owner_id"]
            p_id = post["id"]
            posts["href"].append("https://vk.com/wall{}_{}".format(o_id, p_id))
        posts_df = pd.DataFrame.from_dict(posts)
        #posts_df = self.date_filter(posts_df)
        posts_df.to_csv("./outputs/{}.csv".format(target), index=False, encoding='utf-8-sig')

    def retrieve_targets_posts(self) -> None:
        self.start_session()
        if isinstance(self.targets, str):
            self.retrieve_target_posts(self.targets)
        else:
            for target in self.targets:
                self.retrieve_target_posts(target)
"""
