from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import datetime

from future import standard_library
from mock.mock import MagicMock 

from cloudomate.hoster.vpn.mullvad import MullVad
from cloudomate.hoster.vpn.vpn_hoster import VpnOption
from cloudomate.bitcoin_wallet import Wallet

standard_library.install_aliases()


class TestMullvad(unittest.TestCase):
     
    def setUp(self):
        self.wallet = MagicMock(Wallet)
        self.option = MagicMock(VpnOption)

    def test_purchase(self):
        MullVad._register = MagicMock()
        MullVad._order = MagicMock()
        MullVad.pay = MagicMock()
 
        MullVad.purchase(MullVad, self.wallet, self.option)
        
        self.assertTrue(MullVad._register.called)
        self.assertTrue(MullVad._order.called)
        self.assertTrue(MullVad.pay.called)

    def test_get_status(self):
        MullVad._check_vpn_date = MagicMock(return_value=(True,"-5"))
        MullVad._login = MagicMock()

        expiration_date = MullVad.get_status(MullVad)[1]
        now = datetime.datetime.now(datetime.timezone.utc)
        expiration_days = datetime.timedelta(days=int("-5"))
        full_date = now + expiration_days

        self.assertEqual(expiration_date.day, full_date.day)
        self.assertEqual(expiration_date.month, full_date.month)


if __name__ == "__main__":
    unittest.main()
