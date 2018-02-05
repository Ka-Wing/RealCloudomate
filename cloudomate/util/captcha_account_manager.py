#testkey: fd58e13e22604e820052b44611d61d6c

import os

class captchaAccountManager():

    captcha_api_key_location = os.path.dirname(os.path.realpath(__file__))  + '/config_captcha_account.cfg'

    def __init__(self):
        pass

    #get the API-key needed for Anti-Captcha Api account
    def get_api_key(self):
        if os.path.isfile(self.captcha_api_key_location):
            file = open(self.captcha_api_key_location, "r")
            lines = file.readlines()
            return lines[0].replace('\n', '').replace('\r', '')
            pass
        else:
            raise Exception("missing captcha configuration file")
            pass
        pass

    #Only set the API-key for the account (wil remain the same) currently assigned to this agent
    def set_api_key(self, APIKey):
        login_temp = self.get_anticaptcha_account_login()
        tempfile = open(self.captcha_api_key_location, 'w')
        tempfile.write(APIKey + "\n" +login_temp["username"] + "\n" + login_temp["password"])
        tempfile.close()
        print("\nSuccesfully written config files....")
        pass
    
    #Get the Account login (for signing into anti-captcha) currently assigned to this agent
    def get_anticaptcha_account_login(self):
        if os.path.isfile(self.captcha_api_key_location):
            file = open(self.captcha_api_key_location, "r")
            lines = file.readlines()
            if len(lines) != 3:
                print("\n\n****************************************\n\n Error: Your captcha account configuration (captcha_account.cfg) is not in correct format\n\n****************************************\n\n")
                raise Exception("Captcha configuration file incorrect format")
            pass
            usern = lines[1].replace('\n', '').replace('\r', '')
            passw = lines[2].replace('\n', '').replace('\r', '')
            user_login = {"username": usern, "password": passw}
            return user_login
            pass
        else:
            raise Exception("missing captcha configuration file")
            pass
        pass

    #Set the API-key along with the account associated account (username/email and password) for this agent
    def set_captcha_api_account(self,APIKey,username,password):
        tempfile = open(self.captcha_api_key_location, 'w')
        contents = APIKey + "\n" + username + "\n" + password
        tempfile.write(contents)
        tempfile.close()
        print("\nCapthca account set to: ")
        pass

if __name__ == '__main__':
    key_manager = captchaAccountManager()
    keyretrieved = key_manager.get_api_key()
    print("\n-->key retrieved: " + keyretrieved)
    w_login = key_manager.get_anticaptcha_account_login()
    print("\nweb login: \n\tusername: " + w_login["username"] + "\n\tpassword: " + w_login["password"])
    test = "whuuut"
    key_manager.set_api_key(test)
    print("\nkey set to: " + test)
    keyretrieved = key_manager.get_api_key()
    print("\n-->key retrieved: " + keyretrieved)
    w_login = key_manager.get_anticaptcha_account_login()
    print("\nweb login: \n\tusername: " + w_login["username"] + "\n\tpassword: " + w_login["password"])
