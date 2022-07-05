from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import requests
from os.path import basename
import os
import pandas as pd
from src import printcolors as pc
from tqdm import tqdm
from src.git_credentials import GitCredentialsHandler


class VkDownloader:

    def __init__(self) -> None:
        self.conversion_dict = {"original_url": [], "thumb_url": [], "img_name": []}

    @staticmethod
    def load_links(full_path_to_list: str) -> [list, str]:
        url_list = []
        with open(full_path_to_list, "r", encoding='utf-8-sig') as handle:
            text = handle.read()
            for url in text.split(", "):
                url_list.append(url.strip())
            return url_list, basename(full_path_to_list).split(".")[0]

    def thumbnail_url(self, url_list: list) -> list:
        thumbnail_url_list = []
        os.environ["GH_TOKEN"] = GitCredentialsHandler().retrieve_key()
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        options.add_argument("--incognito")
        service = FirefoxService(executable_path=GeckoDriverManager().install())
        profile = FirefoxProfile()
        profile.set_preference('browser.cache.disk.enable', False)
        profile.set_preference('browser.cache.memory.enable', False)
        profile.set_preference('browser.cache.offline.enable', False)
        profile.set_preference('network.cookie.cookieBehavior', 2)
        driver = webdriver.Firefox(service=service, options=options, firefox_profile=profile)
        pc.printout("-" * 80 + "\n", pc.BLUE)
        pc.printout("Saving urls...\n", pc.BLUE)
        for url in tqdm(url_list, bar_format='{l_bar}{bar:40}{r_bar}{bar:-10b}'):
            """
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=options)
            """
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            post_head = soup.find("div", {"class": "wall_text"})
            if not post_head:
                pc.printout("Something went wrong! Probably too many requests, try deleting the cache while using a VPN or take a look at the response: \n", pc.RED)
                print(soup)
                quit(0)
            thumbnail = post_head.find("a", {"class": "page_post_thumb_wrap"})
            media_link = post_head.find("img", {"class": "media_link__photo"})
            if thumbnail:
                thumbnail_url = thumbnail["style"].split("(")[-1].split(")")[0]
            else:
                thumbnail_url = media_link["src"]
            thumbnail_url_list.append(thumbnail_url)
            self.conversion_dict["original_url"].append(url)
            self.conversion_dict["thumb_url"].append(thumbnail_url)
        driver.close()
        return thumbnail_url_list

    def save_images(self, thumbnail_url_list: list, name: str) -> None:
        try:
            os.mkdir("./outputs/{}".format(name))
        except FileExistsError:
            pass
        counter = 0
        pc.printout("Saving images...\n", pc.BLUE)
        for thumbnail_url in tqdm(thumbnail_url_list, bar_format='{l_bar}{bar:40}{r_bar}{bar:-10b}'):
            response = requests.get(thumbnail_url)
            filename = "{}_{}".format(name, str(counter))
            with open("./outputs/{}/{}.jpg".format(name, filename), "wb") as handle:
                handle.write(response.content)
            self.conversion_dict["img_name"].append(filename)
            counter += 1
        pc.printout("All images saved!\n", pc.BLUE)
        pc.printout("-" * 80 + "\n", pc.BLUE)
        conversion_df = pd.DataFrame.from_dict(self.conversion_dict)
        conversion_df.to_csv("./outputs/{}/{}_conversion.csv".format(name, name), index=False)

    def download_media(self) -> None:
        pc.printout("Please, insert full path of txt file containing all the post urls\n", pc.YELLOW)
        pc.printout("Remember, they should be comma separated for this to work: \n", pc.YELLOW)
        full_path = input()
        url_list, name = self.load_links(full_path)
        thumb_list = self.thumbnail_url(url_list)
        self.save_images(thumb_list, name)
