from ast import literal_eval
from src import printcolors as pc


class GitCredentialsHandler:

    def __init__(self):
        self.check, self.PAT_dict = self.key_checker()
        if not self.check:
            pc.printout("You do not have a GitHub Personal Access Token saved, this application will not work\n", pc.RED)
            pc.printout("To obtain one Login into your GitHub, go to settings -> developer settings ->\n"
                        "personal access tokens -> generate new token\n", pc.RED)
            pc.printout("Please, provide a PAT or quit with Ctrl+C\n", pc.RED)
            self.set_github_key()

    @staticmethod
    def key_checker() -> tuple:
        with open("./credentials/github_private_key.txt", "r") as handle:
            git_key_dict = literal_eval(handle.read())
            if git_key_dict["github_pvt"]:
                return True, git_key_dict
            else:
                return False, git_key_dict

    def set_github_key(self):
        pc.printout("Please insert your PAT: \n")
        self.PAT = input()
        self.PAT_dict['github_pvt'] = self.PAT
        with open("./credentials/github_private_key.txt", "w") as handle:
            handle.write(str(self.PAT_dict))

    def retrieve_key(self):
        return str(self.PAT_dict['github_pvt'])