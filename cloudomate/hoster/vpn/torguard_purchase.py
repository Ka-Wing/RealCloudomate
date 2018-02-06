# If unforseen problems occur: make sure you are running this script with a user OTHER than root or WITHOUT "sudo"

import time
import re
import os
import requests
from selenium import webdriver
import sys
from cloudomate.util.captcha_account_manager import captchaAccountManager

from cloudomate.bitcoin_wallet import Wallet as BitcoinWallet
# from cloudomate.litcoin_wallet import Wallet as LitcoinWallet
from cloudomate.ethereum_wallet import Wallet as EthereumWallet

from cloudomate import bitcoin_wallet as B_wallet_util
# from cloudomate import litcoin_wallet as L_wallet_util
from cloudomate import ethereum_wallet as E_wallet_util


class torguard:
    PURCHASE_URL = "https://torguard.net/cart.php?gid=2"
    COINPAYMENTS_URL = "https://www.coinpayments.net/index.php?cmd=checkout"
    driver = None

    @staticmethod
    def get_metadata():
        return "TorGuard", "https://www.torguard.net/"

    @staticmethod
    def get_gateway():
        return None

    @staticmethod
    def get_required_settings():
        return {"user": ["username", "password"]}

    # Use this method for purchasing with Bitcoin.
    def retrieve_bitcoin(self, user_settings):
        try:
            return self._retrieve_payment_info(["bitcoin", "BTC"], user_settings)
        except Exception as e:
            print(self._error_message(e))

    # Use this method for purchasing with Litecoin.
    def retrieve_litecoin(self, user_settings):
        try:
            return self._retrieve_payment_info(["litecoin", "LTC"], user_settings)
        except Exception as e:
            print(self._error_message(e))

    # Use this method for purchasing with Ethereum.
    # Retrieving Ethereum at the final page is different than for the other currencies.
    def retrieve_ethereum(self, user_settings):
        try:
            return self._retrieve_payment_info(["ethereum", "ETH"], user_settings)
        except Exception as e:
            print(self._error_message(e))

    # Used for generating error message.
    def _error_message(self, message):
        return "Error " + str(message) + "\nTry again. It it still does not work," \
                                         "website might have been updated, update script."

    def __init__(self):

        # Download the appropriate executable chromedirver and place this in the folder for the script to access
        res = requests.get('https://chromedriver.storage.googleapis.com/2.35/chromedriver_linux64.zip')
        file_test = os.path.dirname(os.path.realpath(__file__)) + '/chromedriver_linux64.zip'
        with open(file_test, 'wb') as output:
            output.write(res.content)
            pass
        # extract the downloaded file
        unzip_command = 'unzip -o ' + file_test + ' -d ' + os.path.dirname(os.path.realpath(__file__)) + '/'
        test_ = os.popen(unzip_command).read()
        print(test_)
        # remove the zip file after extraction
        os.popen('rm ' + file_test).read()
        # get the file path to pass to the chromdriver
        driver_loc = os.path.dirname(os.path.realpath(__file__)) + '/chromedriver'
        print("driver location: " + driver_loc)

        # Selenium setup: headless Chrome, Window size needs to be big enough, otherwise elements will not be found.
        options = webdriver.ChromeOptions()
        #options.add_argument('headless')
        #options.add_argument('disable-gpu');
        #options.add_argument('window-size=1920,1080');
        try:
            self.driver = webdriver.Chrome(executable_path=driver_loc, chrome_options=options)
            pass
        except Exception as e:
            print(e)
            raise Exception(e) 
            pass
        # self.driver = webdriver.Chrome()
        self.driver.maximize_window()

    # Don't invoke this method directly.
    def _retrieve_payment_info(self, currency, user_settings):

        print("Placing an order.")

        # Puts VPN in cart and checks out.
        self.driver.get(self.PURCHASE_URL)

        self.driver.find_element_by_css_selector("button[type='button'][value='Order Now']").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector("button[type='submit'][value='add to cart & checkout »']").click()
        time.sleep(1)
        self.driver.find_element_by_css_selector("button.btn.btn-success").click()
        time.sleep(1)

        # Filing in order form.
        self.driver.find_element_by_css_selector("input[type='radio'][value='coinpayments']").click()
        time.sleep(1)

        # Logs in if already registered, else register.
        if user_settings.get("registered") == "1":
            self.driver.find_element_by_css_selector("a[href='/cart.php?a=login']").click()
            time.sleep(1)
            self.driver.find_element_by_xpath('//*[@id="loginfrm"]/div[1]/div/input'). \
                send_keys(user_settings.get("email"))
            self.driver.find_element_by_xpath('//*[@id="loginfrm"]/div[2]/div/input'). \
                send_keys(user_settings.get("password"))
        else:
            self.driver.find_element_by_xpath('//*[@id="signupfrm"]/div[1]/div/input'). \
                send_keys(user_settings.get("email"))
            self.driver.find_element_by_xpath('//*[@id="newpw"]'). \
                send_keys(user_settings.get("password"))
            self.driver.find_element_by_xpath('//*[@id="signupfrm"]/div[4]/div/input'). \
                send_keys(user_settings.get("password"))
            self.driver.find_element_by_xpath('//*[@id="signupfrm"]/div[6]/div/input'). \
                send_keys("Blockchain life")

        self.driver.find_element_by_id("accepttos").click()
        self.driver.find_element_by_css_selector("input[type='submit'][value='Complete Order »']").click()
        time.sleep(1)

        # Set registered to 1 so during any purchase in the future, the script will log in instead of registering.
        if user_settings.get("registered") == "0":
            pass

        print("Retrieving the amount and address.")

        # Continue to the final page.
        try:
            self.driver.find_element_by_id("cpsform").click()
        except:
            print("\n\n*************************************************************************************\n")
            print("\nError: Perhaps you are using an E-mail that is already registered? ")
            print(
                "\n\n(You can specify whether the given  email is already registered as a parameter in the user settings for the script) \n")
            print("\nTry again with the approproate settings")
            print("\n\n*************************************************************************************\n")
        self.driver.find_element_by_id("coins_" + currency[1]).click()
        self.driver.find_element_by_id("dbtnCheckout").click()

        tries = 0
        while not (self.driver.current_url == self.COINPAYMENTS_URL):
            tries = tries + 1
            time.sleep(2)
            if tries > 10:
                raise Exception("You probably already have 3 unfinished transfers with coinpayments.net from within "
                                "the last 24 hours and you therefore cannot create anymore.")

        time.sleep(2)

        amount = ""
        address = ""

        page = self.driver.page_source
        address_re = ""
        amount_re = ""
        if currency[0] == "ethereum":
            address_re = '<div class="address">(.*?)</div>'
            amount_re = "<div>(.*?) ETH</div>"
        else:
            address_re = '<div><a href="' + currency[0] + ':(.*?)\?amount=(.*?)">(.*?)</a></div>'

        # Get address and amount
        if currency[0] == "ethereum":
            for line in page.split('\n'):
                line = line.lstrip().rstrip()
                match_amount = re.findall(amount_re, line)
                match_address = re.findall(address_re, line)
                if len(match_amount) > 0:
                    amount = match_amount[0]
                if len(match_address) > 0:
                    address = match_address[0]
        else:
            for line in page.split('\n'):
                line = line.lstrip().rstrip()
                match = re.findall(address_re, line)
                if len(match) > 0:
                    address = match[0][0]
                    amount = match[0][1]

        time.sleep(2)
        return {'amount': str(amount), 'address': str(address)}

    def pay(self, amount, address, coin_type, wallet):
        # Pay amount using specified COIN wallet, if their is not enough balance available print "Not enough balance for the specified COIN-payment"

        print("\nPayment process of " + str(amount) + " of " + str(coin_type) + " to " + str(address) + " started")
        if (coin_type == 'BTC'):
            print("\nConnecting to bitcoin wallet")
            print("\nChecking Balance...")
            fee = B_wallet_util.get_network_fee()
        elif (coin_type == 'ETH'):
            print("\nConnecting to Ethereum Wallet...")
            print("\nChecking Balance...")
            fee = E_wallet_util.get_network_fee()
        print(('Calculated fee: %s' % fee))
        if (wallet.get_balance() >= fee + float(amount)):
            transaction_hash = wallet.pay(address, amount, fee)
            print('Done purchasing')
            return transaction_hash
        else:
            print(" Not enough " + str(coin_type))

    def saveLoginAfterPurchase(self, username, password):

        # save the login parameter so these can be used by the VPN instalaton script in the Utilities
        full_file_path = os.path.dirname(os.path.realpath(__file__)) + '/../../util/torguard_login.txt'
        file_contents = username + "\n" + password
        tempfile = open(full_file_path, 'w')
        tempfile.write(file_contents)
        tempfile.close()
        pass


if __name__ == '__main__':
    tg = torguard()
    user_settings = {"email": "ralphie_ozxcd@hotmail.com", "password": "Chicker1$", "registered": "1"}
    dict = tg.retrieve_ethereum(user_settings)
    print(dict['amount'])
    print(dict['address'])
    # walletTest = LitcoinWallet()
    # tg.pay(dict['amount'],dict['address'],'LTC',walletTest)
    walletTest = EthereumWallet()
    print(str(walletTest.get_balance()))
    tg.pay(dict['amount'], dict['address'], 'ETH', walletTest)

    # wait for the site to deliver the service after payment
    time.sleep(70)
    tg.saveLoginAfterPurchase(user_settings['email'], user_settings['password'])
