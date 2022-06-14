from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import requests
from os.path import basename
import os
import pandas as pd
from src import printcolors as pc


class VkDownloader:

    def __init__(self) -> None:
        self.conversion_dict = {"original_url": [], "thumb_url": [], "img_name": []}

    @staticmethod
    def load_links(full_path_to_list: str) -> [list, str]:
        url_list = []
        with open(full_path_to_list, "r") as handle:
            text = handle.read()
            for url in text.split(","):
                url_list.append(url.strip())
            return url_list, basename(full_path_to_list).split(".")[0]

    def thumbnail_url(self, url_list: list) -> list:
        thumbnail_url_list = []
        for url in url_list:
            options = Options()
            options.add_argument("--headless")
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=options)
            driver.get(url)
            html = driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            thumbnail = soup.find("a", {"class": "page_post_thumb_wrap"})
            thumbnail_url = thumbnail["style"].split("(")[-1].split(")")[0]
            thumbnail_url_list.append(thumbnail_url)
            self.conversion_dict["original_url"].append(url)
            self.conversion_dict["thumb_url"].append(thumbnail_url)
        return thumbnail_url_list

    def save_images(self, thumbnail_url_list: list, name: str) -> None:
        try:
            os.mkdir("./outputs/{}".format(name))
        except FileExistsError:
            pass
        counter = 0
        for thumbnail_url in thumbnail_url_list:
            response = requests.get(thumbnail_url)
            filename = "{}_{}".format(name, str(counter))
            with open("./outputs/{}/{}".format(name, filename), "wb") as handle:
                handle.write(response.content)
            self.conversion_dict["img_name"].append(filename)
            counter += 1
        conversion_df = pd.DataFrame.from_dict(self.conversion_dict)
        conversion_df.to_csv("./outputs/{}/{}_conversion.csv".format(name, name), index=False)


    def download_media(self) -> None:
        pc.printout("Please, insert full path of txt file containing all the post urls\n", pc.YELLOW)
        pc.printout("Remember, they should be comma separated for this to work: \n", pc.YELLOW)
        full_path = input()
        url_list, name = self.load_links(full_path)
        thumb_list = self.thumbnail_url(url_list)
        self.save_images(thumb_list, name)
