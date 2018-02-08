# If unforseen problems occur: make sure you are running this script with a user OTHER than root or WITHOUT "sudo"

import time
import re
import os
import requests
from selenium import webdriver
import sys

from selenium.common.exceptions import NoSuchElementException

from cloudomate.util.captcha_account_manager import captchaAccountManager
from abc import ABC, abstractmethod, abstractproperty
from cloudomate.bitcoin_wallet import Wallet as BitcoinWallet
# from cloudomate.litcoin_wallet import Wallet as LitcoinWallet
from cloudomate.ethereum_wallet import Wallet as EthereumWallet
from cloudomate import bitcoin_wallet as B_wallet_util
# from cloudomate import litcoin_wallet as L_wallet_util
from cloudomate import ethereum_wallet as E_wallet_util


class coinpaymentsVpnProvider(ABC):

    @abstractmethod
    def PURCHASE_URL(self):
        pass

    @abstractmethod
    def COINPAYMENTS_URL(self):
        pass

    @abstractmethod
    def saveUserLoginFile(self):
        pass

    @abstractmethod
    def vpnProviderName(self):
        pass

    @abstractmethod
    def vpnProviderBaseUrl(self):
        pass

    driver = None

    # Creates an invoice that for a vpn service that requires Bitcoin payment (Returns the "BTC amount" and the "BTC address" to which the "BTC amount" needs to be send).
    def retrieve_bitcoin(self, user_settings):
        try:
            return self._retrieve_payment_info(["bitcoin", "BTC"], user_settings)
        except Exception as e:
            print(self._error_message(e))

    #TODO DOES NOT ACCEPT LITECOIN.
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

        connection_reset = True
        while connection_reset:
            connection_reset = False
            try:
                self.driver = webdriver.Chrome(executable_path=driver_loc, chrome_options=options)
                pass
            except Exception as e:
                if e.errno == 104:
                    connection_reset = True
                    print("\nResetting connection...\n")
                    pass
                else:
                    raise Exception(e)
            pass
        # self.driver = webdriver.Chrome()
        self.driver.maximize_window()


    @abstractmethod
    def goToCoinPaymentsPage(self):
        pass

    # Don't invoke this method directly.
    def _retrieve_payment_info(self, currency, user_settings):

        self.goToCoinPaymentsPage()

        print("Placing an order.")
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

        try:
            self.driver.find_element_by_id("coins_" + currency[1]).click()
            pass
        except NoSuchElementException:
            print("The service provider does not accept " + currency[1] + " (anymore).")
            sys.exit(0)

        self.driver.find_element_by_id("dbtnCheckout").click()

        # See if any error messages are returned.
        error_available = False
        try:
            error_message = self.driver.find_element_by_xpath('//*[@id="coform"]/div[1]/div').text
            error_available = True
        except NoSuchElementException:
            pass # No error found

        if error_available:
            print("Error message returned from coinpayments.net: \"" + error_message + "\"")
            sys.exit(0)


        tries = 0
        while not (self.driver.current_url == self.COINPAYMENTS_URL):
            try:
                error_message = self.driver.find_element_by_xpath("/html/body/div/div/div[2]").text
                if "3 unfinished" in error_message:
                    print("You already have 3 unfinished transfers with coinpayments.net from within the last "
                      "24 hours and therefore you cannot create anymore orders..")
                    exit(0)
            except NoSuchElementException:
                pass

            tries = tries + 1
            time.sleep(2)
            if tries > 10:
                #TODO do timeout.
                sys.exit(0)

        time.sleep(2)

        amount = ""
        address = ""

        try:
            address = self.driver.find_element_by_xpath('//*[@id="email-form"]/div[2]/div[1]/div[3]/div[2]').text
            print("address: " + address)
        except NoSuchElementException:
            pass

        try:
            amount = self.driver.find_element_by_xpath('//*[@id="email-form"]/div[2]/div[1]/div[1]').text
        except NoSuchElementException:
            pass

        # Using page source to find address and amount because elements will not be found.
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
        full_file_path = self.saveUserLoginFile
        file_contents = username + "\n" + password
        tempfile = open(full_file_path, 'w')
        tempfile.write(file_contents)
        tempfile.close()
        pass