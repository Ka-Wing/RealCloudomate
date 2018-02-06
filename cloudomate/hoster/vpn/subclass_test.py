from abc import ABC, abstractmethod
from cloudomate.hoster.vpn.coinpayments_hoster import coinPaymentsVpn


class Sub(coinPaymentsVpn):
    def __init__(self):
        super().__init__()
        print("Sub class init.")

    COINPAYMENTS_URL = "asdasd"

    PURCHASE_URL = "asad"

    def saveUserLoginFile(self):
        pass

    def goToCoinPaymentsPage(self):
        print("goToCoinPaymentsPage()")

    def print(self):
        print("print()")

if __name__ == "__main__":
    sub = Sub()
    sub.print()