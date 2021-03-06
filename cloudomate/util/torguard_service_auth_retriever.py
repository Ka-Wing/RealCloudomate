#If any issuess occur: please try to run this file without "sudo" or as a user other than the root user

import os
import re
from selenium import webdriver
import time

class torguardServiceRetriever():

    c_userpass_dir =  os.path.expanduser("~") + '/.config/torguard_open_vpn_userpass'

    userpass_file_name = 'torguard_openvpn_service_auth.txt'

    #username en passw for open vpn: NOTE these are NOT THE SAME as vpnac-web login credentials
    vpnusern_ = None
    vpnpassw_ = None

    vpn_config_password_to_be_set = 'Test_12345'

    #arguments username and password are required by openvpn service
    def __init__(self,wlogin_user = None,wlogin_passw = None):

        # Sets up Selenium
        self._driver_setup()

        if wlogin_user != None and wlogin_passw != None:
            self.extractOpenVpnUserInfo(wlogin_user, wlogin_passw)
            return
            pass

        web_login_file =  os.path.expanduser("~") + '/.config/torguard_login.txt'
        if os.path.isfile(web_login_file):
            file = open(web_login_file,"r")
            lines = file.readlines()
            weblogin_user = lines[0].replace('\n', '').replace('\r', '')
            weblogin_passw = lines[1].replace('\n', '').replace('\r', '')
            print("--web-login user found: " + weblogin_user)
            print("--web-login passw found: " + weblogin_passw)
            self.extractOpenVpnUserInfo(weblogin_user, weblogin_passw)
            pass
        else:
            print("NO Weblogin credentials (not the same as openvpn service credentials) were provided: please run purchase torguard script, "
                            "or provide them directly as parameters to this script")
        pass

    def extractOpenVpnUserInfo(self,login_username,login_password):
        print("Retrieving username and password.")
        self._login(login_username, login_password)
        self._manage_credentials_of_active_service()
        self.vpnusern_ = self._get_username()
        self._change_password(self.vpn_config_password_to_be_set)
        print(self.vpnusern_ + ", " + self.vpnpassw_)
        if os.path.isdir(self.c_userpass_dir) == False:
            os.popen('mkdir ' + self.c_userpass_dir).read()
            pass
        file_test = self.c_userpass_dir + '/' + self.userpass_file_name
       # self.saveTofile(self.vpnusern_ + "\n" + self.vpnpassw_,file_test)
        pass

    def saveTofile(self, file_contents, full_file_path):
        tempfile = open(full_file_path, 'w')
        tempfile.write(file_contents)
        tempfile.close()
        pass

    def _login(self, login_username, login_password):
        if self.driver is None:
            print("Selenium Chromedriver not set")

        self.driver.get("https://torguard.net/clientarea.php")

        # Waiting for Cloudfare page to pass.
        while(True):
            time.sleep(2)
            try:
                self.driver.find_element_by_id("username")
                break
            except Exception:
                pass

        # Fills in form and logs in.
        self.driver.find_element_by_id("username").send_keys(login_username)
        self.driver.find_element_by_id("password").send_keys(login_password)
        self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/form/fieldset/div[3]/div/input[1]").click()

        try:
            error_message = self.driver.find_element_by_class_name("alert-danger").text
            print("Website returned an error during login: \"" + error_message + "\"")
            exit(0)
        except Exception:
            pass


    def _driver_setup(self):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('disable-gpu')
        options.add_argument('window-size=1920,1080')
        #TODO fix hardcoded executable_path
        self.driver = webdriver.Chrome(executable_path="/home/kw/chromedriver_linux64/chromedriver",
                                       chrome_options=options)
        self.driver.maximize_window()

    def if_active_service(self):
        self.driver.get("https://torguard.net/clientarea.php?action=products")


    # Goes to the credentials pages of an active service
    def _manage_credentials_of_active_service(self):
        if(self.driver.current_url != "https://torguard.net/clientarea.php?action=products"):
            self.driver.get("https://torguard.net/clientarea.php?action=products")

        if not self._get_logged_in():
            #TODO Needs fix.
            self._login()
            self.driver.get("https://torguard.net/clientarea.php?action=products")

        self.driver.find_element_by_xpath("//select[@name='itemlimit']/option[text()='100']").click()

        # Find an active service, then click on manage credentials.
        service_index = 1
        while True:
            try:
                # If this element is found, it means there is only one service.
                element = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div[4]/table/tbody/tr[" +
                                                            str(service_index) + "]/td[5]/span")

                if element.text == "Active":
                    self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div[4]/table/tbody/tr[" +
                                                      str(service_index) + "]/td[6]/div/a").click()
                    self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div[4]/table/tbody/tr[" +
                                                      str(service_index) + "]/td[6]/div/ul/li[3]/a").click()

                    return True
                service_index = service_index + 1
            except Exception:
                return False  # Could not find an active service

            time.sleep(3)

            a = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/table/tbody/tr/td[4]")
            a.find_element_by_class_name("btn").click()


            self.driver.switch_to.alert().accept()
            self.driver.find_element_by_xpath()

            #TODO What is this?
            tries = 0
            info = ""
            while tries < 5:
                time.sleep(2)
                try:
                    info = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/table/tbody/tr/td[4]/div")
                except Exception:
                    tries = tries + 1


    #Returns if logged in
    def _get_logged_in(self):
        try:
            text = self.driver.find_element_by_class_name("user-info").text
            if text.split(" ")[0] == "Hello":
                return True
            else:
                return False
        except Exception:
            return False

    def _get_username(self):
        self.driver.switch_to.window(self.driver.window_handles[-1])
        if self.driver.current_url != "https://torguard.net/managecredentials.php":
            self._manage_credentials_of_active_service
            self.driver.switch_to.window(self.driver.window_handles[-1])

        self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/table/tbody/tr/td[4]")\
            .find_element_by_class_name("btn").click()

        time.sleep(1)
        self.driver.switch_to.alert.accept()
        self.driver.switch_to.window(self.driver.window_handles[-1])

        try:
            time.sleep(5)
            info = self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div/table/tbody/tr/td[4]')
            info = info.find_element_by_tag_name("div")
            info = str(info.text).lstrip().rstrip()
            match = re.findall("Username: (.*?)    Password:", info)
            return str(match[0])
        except Exception:
            pass

    def getValidUntil(self):
        if(self.driver.current_url != "https://torguard.net/clientarea.php?action=products"):
            self.driver.get("https://torguard.net/clientarea.php?action=products")

        if not self._get_logged_in():
            #TODO Needs fix
            self._login()
            self.driver.get("https://torguard.net/clientarea.php?action=products")

        self.driver.find_element_by_xpath("//select[@name='itemlimit']/option[text()='100']").click()

        # Find an active service, then scrape the due date.
        service_index = 1
        while True:
            try:
                element = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div[4]/table/tbody/tr[" +
                                                            str(service_index) + "]/td[5]/span")

                if element.text == "Active":
                    return self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/div[4]/table/tbody/tr[" +
                                                            str(service_index) + "]/td[4]").text
                service_index = service_index + 1
            except Exception:
                return "00/00/0000"

    def _change_password(self, password):
        if self.driver.current_url != "https://torguard.net/managecredentials.php":
            print("Driver did not detect the manage credentials page.")
            exit(0)

        # Finding the cell containing password management
        password_cell = self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/table/tbody/tr/td[3]")
        password_cell.find_element_by_tag_name("a").click()

        # Changes the password
        self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/table/tbody/tr/td[3]/span/div/form"
                                          "/div/div[1]/div[1]/input").send_keys(password)
        self.driver.find_element_by_xpath("/html/body/div[2]/div[2]/div/table/tbody/tr/td[3]/span/div/form/"
                                          "div/div[1]/div[2]/button[1]").click()

        # Checking if password has been changed.
        tries = 0
        while tries < 5:
            if password_cell.text == "[hidden]":
                self.vpnpassw_ = self.vpn_config_password_to_be_set
                return True # Password has been changed
            time.sleep(3)

        print("Something went wrong.")
        return False

if __name__ == '__main__':
    vpntoruguardretriever = torguardServiceRetriever()
    print(vpntoruguardretriever.getValidUntil())
    vpntoruguardretriever._manage_credentials_of_active_service()
    #test with existing web (non purchased trough script) credentials: vpntoruguardretriever = torguardServiceRetriever("mohamed.amine.legheraba@gmail.com", "djamel75018")
