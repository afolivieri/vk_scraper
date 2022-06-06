import vk_api
from src import printcolors as pc

class VkApiWrapper:


    def __init__(self, targets):
        self.targets = targets
        self.read_credentials()
        pc.printout("\nYour targets are: \n", pc.YELLOW)
        pc.printout(str(self.targets)+"\n", pc.YELLOW)


    def set_targets(self):
        pc.printout("Please insert new targets: \n", pc.YELLOW)
        self.targets = input().split()
        pc.printout("Your targets are: \n", pc.YELLOW)
        pc.printout(str(self.targets)+"\n", pc.YELLOW)


    def show_targets(self):
        pc.printout("Your targets are: \n", pc.YELLOW)
        pc.printout(str(self.targets) + "\n", pc.YELLOW)


    def store_credentials(self):
        pc.printout("Please insert VK login (it's better to use a phone number"
                    " to automatically bypass security checks): \n", pc.YELLOW)
        self.login = input()
        pc.printout("Please insert VK password: \n", pc.YELLOW)
        self.password = input()
        pc.printout("Please insert VK token: \n", pc.YELLOW)
        self.token = input()
        with open("./config/credentials", "w") as handler:
            handler.write("login: {}\n".format(self.login))
            handler.write("password: {}\n".format(self.password))
            handler.write("token: {}\n".format(self.token))


    def read_credentials(self):
        with open ("./config/credentials", "r") as handler:
            credentials = handler.readlines()
        if len(credentials[0].split()) != 2:
            pass
        else:
            self.login = credentials[0].split()[1]
            self.login = credentials[1].split()[1]
            self.login = credentials[2].split()[1]


    def set_dates(self):
        print("set_date")
        pass
