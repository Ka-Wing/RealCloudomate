from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from cloudomate.util.captcha_account_manager import captchaAccountManager

import re
import random
from builtins import len
from builtins import str
from builtins import range

from future import standard_library
from mechanicalsoup import StatefulBrowser

from cloudomate.util.recaptchasolver import reCaptchaSolver
from cloudomate.util.config import UserOptions

standard_library.install_aliases()


class Infura(object):
    def __init__(self):
        self.browser = StatefulBrowser(user_agent="Firefox")
        self.user_settings = UserOptions()
        self.user_settings.read_settings()

    def random_generator(self, length=0):
        if length is 0:
            length = random.randrange(4, 15)

        possibilities = "abcdefghijklmnopqrstuvwxyz"
        random_sequence = ""

        # Generate random strings for registration form
        for i in range(0, length):
            random_sequence = random_sequence + possibilities[random.randrange(len(possibilities))]

        return random_sequence

    def register(self):
        registration = "https://form.infura.io/form/embed.php?id=11217"
        self.browser.open(registration)

        # Gets the Google Recaptcha key and the solution hash.
        soup = self.browser.get_current_page()
        datasite_key = soup.select("div.g-recaptcha")[0]["data-sitekey"]
        c_manager_ = captchaAccountManager()
        captcha_solver = reCaptchaSolver(c_manager_.get_api_key())
        solution = captcha_solver.solveGoogleReCaptcha(registration,
                                                         datasite_key)

        # Post data
        random_email = self.random_generator(0) + "@" + self.random_generator(0) + "." + self.random_generator(length=3)
        key = soup.select("input#element_4")[0]["value"]
        data = {"element_3_1": self.random_generator(0),
                "element_3_2": self.random_generator(0),
                "element_2": random_email,
                "element_4": key,
                "element_13": "",
                "element_14": "",
                "element_12": "",
                "element_7": "",
                "element_8": "",
                "element_9_other": "",
                "element_15": "",
                "element_17": "",
                "element_18_1": "1",
                "g-recaptcha-response": solution,
                "form_id": "11217",
                "submit_form": "1",
                "page_number": "1"
                }
        # Use the post method on the given link
        response = self.browser.post("https://form.infura.io/form/embed.php", data)
        # Checks if registration went wrong
        for line in response.text.split("\n"):
            if ("error_message" in line):
                raise Exception("Something went wrong during registration."
                                "Might be incorrect Captcha solution. Try again.")

        # Gets the redirection link
        link = str(response.text.split("'")[1])

        # If registration link does not match as expected
        if not re.match("https\:\/\/infura.io/setup\?key=", link):
            raise Exception("Return link does not match as expected")
        else:
            return {"Mainnet": "https://mainnet.infura.io/" + key,
                    "Ropsten": "https://ropsten.infura.io/" + key}
