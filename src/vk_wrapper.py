import vk
from src import printcolors as pc
from datetime import datetime
import pandas as pd


class VkApiWrapper:

    def __init__(self, targets: object) -> None:
        self.targets = targets
        self.start_date = None
        self.end_date = None
        self.read_credentials()
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

    def set_dates(self) -> None:
        pc.printout("Please insert starting date (dd/mm/yyyy format): \n", pc.YELLOW)
        start_date = input()
        if start_date:
            self.start_date = datetime.timestamp(datetime.strptime(start_date, "%d/%m/%Y"))
        else:
            self.start_date = None

        pc.printout("Please insert end date or press enter (dd/mm/yyyy format): \n", pc.YELLOW)
        end_date = input()
        if end_date:
            self.end_date = datetime.timestamp(datetime.strptime(end_date, "%d/%m/%Y"))
            if self.start_date >= self.end_date:
                pc.printout("WARNING: Your end date is earlier than the start date, this will result in an empty output\n",
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

    def start_session(self) -> None:
        self.session = vk.Session(access_token=self.token)
        self.api = vk.API(self.session, v=5.131)

    def date_filter(self, df:pd.DataFrame) -> pd.DataFrame:
        try:
            df = df.loc[df["date"] >= self.start_date].copy()
        except AttributeError:
            pass
        try:
            df = df.loc[df["date"] >= self.end_date].copy()
        except AttributeError:
            pass
        df.loc[:,"date"] = pd.to_datetime(df["date"], unit="s")
        return df

    def retrieve_target_posts(self, target) -> None:
        posts = {"date": [], "text": [], "likes": [], "href": []}
        wall = self.api.wall.get(domain=target)
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
        posts_df = self.date_filter(posts_df)
        posts_df.to_csv("./outputs/{}.csv".format(target), index=False, encoding='utf-8-sig')

    def retrieve_targets_posts(self) -> None:
        self.start_session()
        if isinstance(self.targets, str):
            self.retrieve_target_posts(self.targets)
        else:
            for target in self.targets:
                self.retrieve_target_posts(target)
