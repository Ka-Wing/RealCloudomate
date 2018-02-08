from selenium.common.exceptions import NoSuchElementException

from cloudomate.hoster.vpn.coinpayments_vpn_provider import coinpaymentsVpnProvider
import time
from cloudomate.bitcoin_wallet import Wallet as BitcoinWallet
# from cloudomate.litcoin_wallet import Wallet as LitcoinWallet
from cloudomate.ethereum_wallet import Wallet as EthereumWallet
from cloudomate import bitcoin_wallet as B_wallet_util
# from cloudomate import litcoin_wallet as L_wallet_util
from cloudomate import ethereum_wallet as E_wallet_util
import os

class torguardVPNPurchaser(coinpaymentsVpnProvider):

    PURCHASE_URL = 'https://torguard.net/cart.php?gid=2'
    COINPAYMENTS_URL = 'https://www.coinpayments.net/index.php?cmd=checkout'

    saveUserLoginFile = os.path.expanduser("~") + '/.config/torguard_login.txt'

    #TODO redundant
    vpnProviderName = "Torguard"
    vpnProviderBaseUrl = "https://torguard.net"

    @staticmethod
    def get_metadata():
        return "TorGuard", "https://www.torguard.net/"

    @staticmethod
    def get_gateway():
        return None

    @staticmethod
    def get_required_settings():
        return {"user": ["username", "password"]}

    def goToCoinPaymentsPage(self):
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

        # Checks if any error message can be found on the webpage. If so, print error message.
        error_available = False
        try:
            error_message = self.driver.find_element_by_class_name("alert-danger").text
            error_available = True
        except NoSuchElementException:
            pass # No errors found
        if error_available:
            print("Website returned an error during order placing: \"" + error_message + "\"")
            exit(0)

        # Set registered to 1 so during any purchase in the future, the script will log in instead of registering.
        if user_settings.get("registered") == "0":
            pass
        pass
        print("\nBrowsing to payment page")

    def test(self):
        print("\ntest")
        pass


if __name__ == '__main__':
    tg = torguardVPNPurchaser()
    user_settings = {"email": "mohameasdasdasdheraba@gmail.com", "password": "djasdasdasd01ada_sdhTE12w", "registered": "0"}
    b = tg.retrieve_ethereum(user_settings)
    print(b['amount'])
    print(b['address'])
    # walletTest = LitcoinWallet()
    # tg.pay(dict['amount'],dict['address'],'LTC',walletTest)
    walletTest = EthereumWallet()
    print(str(walletTest.get_balance()))
    tg.pay(b['amount'], b['address'], 'ETH', walletTest)
