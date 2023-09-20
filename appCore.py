#from jobApp.jobScraperLinkedinMicroService import JobScraperLinkedinMicroService
#from jobApp.linkedinEasyApplyMicroService import easyApplyMicroService
from jobApp.loginSessionLinkedinMicroService import  LoginSessionLinkedCreator

class appCreatorLinkedin:
    def __init__(self, linkedinConfigFile) -> None:
        self.linkedSessionCreatorService = LoginSessionLinkedCreator(linkedinConfigFile, headless=False)

    def tryCredentialsLinkedin(self):
        try:
            self.linkedSessionCreatorService.attemptLogin()
        except Exception as e:
            print("error occured during login: ", e)


if __name__ == "__main__":

    loginbot = LoginSessionLinkedCreator('jobApp/secrets/linkedin.json', headless=False)
    bot = loginbot.createLoginSession(True)