from cloudomate.hoster.vpn.vpn_hoster import VpnHoster
from cloudomate.hoster.vpn.vpn_hoster import VpnStatus
from cloudomate.hoster.vpn.vpn_hoster import VpnInfo
from cloudomate.gateway import bitpay
from cloudomate.util.captchasolver import captchaSolver
from cloudomate import bitcoin_wallet as wallet_util
from forex_python.converter import CurrencyRates
import sys
import datetime
import requests
import os
import zipfile
import shutil
import urllib.request
import time


class MullVad(VpnHoster):
    REGISTER_URL = "https://www.mullvad.net/en/account/create/"
    LOGIN_URL = "https://www.mullvad.net/en/account/login/"
    ORDER_URL = "https://www.mullvad.net/en/account"
    OPTIONS_URL = "https://www.mullvad.net/en"
    CONFIGURATION_URL = "https://mullvad.net/en/download/config/"
    TESTING_URL = "https://am.i.mullvad.net/json"
    INFO_URL = "https://mullvad.net/en/guides/linux-openvpn-installation/"

    required_settings = [
        'accountnumber',
        'captchaaccount',
    ]

    def __init__(self):
        super().__init__()

        self.name = "MullVad"
        self.website = "https://www.mullvad.net"
        self.protocol = "OpenVPN"
        self.bandwidth = sys.maxsize
        self.speed = sys.maxsize

        self.gateway = bitpay

    def options(self):
        self.br.open(self.OPTIONS_URL)
        soup = self.br.get_current_page()
        p = soup.select("p.hero-description")
        string = p[1].get_text()
        eur = float(string[string.index("€")+1 : string.index("/")])

        c = CurrencyRates()
        usd = c.convert("EUR", "USD", eur)
        usd = round(usd, 2)
        self.price = usd

        return super().options()

    def purchase(self, user_settings, wallet):
        # Prepare for the purchase on the MullVad website
        self._register(user_settings)
        (amount,address) = self._order(user_settings, wallet)

        # Make the payment
        print("Purchasing MullVad instance")
        print(('Paying %s BTC to %s' % (amount, address)))
        fee = wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        transaction_hash = wallet.pay(address, amount, fee)
        print('Done purchasing')
        return transaction_hash

    def info(self, user_settings):
        # Displays the account number and the OpenVPN guide for linux
        self.br.open(self.INFO_URL)
        ovpn = self.br.get_current_page().get_text()
        return VpnInfo(user_settings.get("accountnumber"), None, ovpn)

    def status(self, user_settings):
        self._login(user_settings)

        # Retrieve days left until expiration
        now = datetime.datetime.now(datetime.timezone.utc)
        (online,expiration) = self._checkVPNDate()
        expiration = datetime.timedelta(days=int(expiration))
        # Add the remaining days to the current date to get expiratetion date
        return VpnStatus(online, now+expiration)

    def _register(self, user_settings):
        self.br.open(self.REGISTER_URL)
        form = self.br.select_form()
        soup = self.br.get_current_page()

        # Get captcha needed for registration
        img = soup.select("img.captcha")[0]['src']
        urllib.request.urlretrieve("https://www.mullvad.net"+img, "captcha.png")
         
        # Solve captcha 
        c_solver = captchaSolver(user_settings.get("captchaaccount"))
        solution = c_solver.solveCaptchaTextCaseSensitive("./captcha.png")
        form['captcha_1'] = solution
        
        page = self.br.submit_selected()
        new_accountnumber = 0
        
        # Parse page to get new account number
        newpage = str(self.br.get_current_page())
        for line in newpage.split("\n"):
            if "Your account number:" in line:
                new_accountnumber = line.split(":")[1]
                new_accountnumber = new_accountnumber.split("<")[0].strip(" ")
                break
        user_settings.put("accountnumber",new_accountnumber)
        self._setAccount(new_accountnumber)

        if page.url == self.REGISTER_URL:
            # An error occurred
            print("The captcha was wrong")
            sys.exit(2)

        return page

    def _login(self, user_settings):
        self.br.open(self.LOGIN_URL)
        form = self.br.select_form()
        
        # Use account number to login
        form["account_number"] = user_settings.get("accountnumber")
        page = self.br.submit_selected()

        if page.url == self.LOGIN_URL:
            print("The account number is wrong")
            sys.exit(2)

        return page

    def _order(self, user_settings, wallet):
        self.br.open(self.ORDER_URL)
        form = self.br.select_form()
        
        # Order one month
        form['months'] = "1"
        self.br.submit_selected()
        month_price = ""
        bitcoin_address = ""
        payment_info_page = str(self.br.get_current_page())
        
        # Parse page to get bitcoin ammount and address
        for line in payment_info_page.split("\n"):
            if "1 month = " in line:
                month_price = line.strip().split(" ")[3]
            if 'input readonly' in line:
                bitcoin_address_line = line.strip().split(" ")[3].split("=")[1]
                bitcoin_address = bitcoin_address_line.partition('"')[-1].rpartition('"')[0]
        return (month_price, bitcoin_address)




    def _setAccount(self, new_accountnumber):
        self.accountnumber = new_accountnumber


    def _checkVPNDate(self):
        # Checks if vpn expired, should be called after login
        expire_date = self.br.get_current_page().select(".balance-header")[0].get_text()
        expire_date = expire_date.split('\n')[2]
        temp1 = expire_date.index('in')
        temp2 = expire_date.index('days')
        expire_date = expire_date[temp1+3:temp2-1]
        
        if (expire_date <= '0'):
            return (False, expire_date)
        else:
            return (True, expire_date)


    def _checkVPN(self, setup=False):
        # Check if VPN is active
        res = requests.get(TESTING_URL)
        print(res.json())
        # Check if IP's country is Sweden
        if res.json()['country'] == "Sweden":
            print("VPN is active!")
        else:
            if setup:
                print("Error: VPN was not installed!")
            else:
                self.setupVPN() 

    def setupVPN(self):
        # Setup the VPN
        print("Time to setup the vpn!")
        self._downloadFiles()
        # Update and install openvpn
        test = os.popen("sudo apt-get install openvpn").read()
        print(test)
        # Copy files to openvpn folder
        test = os.popen("sudo cp -a ./config-files/. /etc/openvpn/").read()
        print(test)
        os.chdir("/etc/openvpn/")
        # Start openvpn service
        test = os.popen("sudo service openvpn start").read()
        print(test)
        # Sleep for 5 seconds, so that vpn connection can be established in the mean time
        time.sleep(10)
        self._checkVPN(True)

    # Download config files for setting up VPN and extract them
    def _downloadFiles(self):
	# Fill information on website to get right config files for openvpn 
        self.br.open(CONFIGURATION_URL)
        form = self.br.select_form()
        form['account_token'] = user_setting.get("accountnumber")
        form['platform'] = "Linux"
        form['region'] = "se-sto"
        form['port'] = "0"
        response = self.br.submit_selected()
        content = response.content
        # Download the zip file to the right location
        files_path = "./config-files/config.zip"
        with open(files_path, "wb") as output:
            output.write(content)

        # Unzip files
        zip_file = zipfile.ZipFile(files_path, 'r')
        for member in zip_file.namelist():
            filename = os.path.basename(member)
        # Skip directories
            if not filename:
                continue

        # Copy file (taken from zipfile's extract)
        source = zip_file.open(member)
        target = open(os.path.join("./config-files/", filename), "wb")
        with source, target:
            shutil.copyfileobj(source, target)
            # Delete zip file
            os.remove(files_path)

