from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from builtins import open

import shutil
import requests
import os
import time
import zipfile

from mechanicalsoup import StatefulBrowser
from future import standard_library

from cloudomate.util.settings import Settings

standard_library.install_aliases()


class InstallMullvad(object):
    CONFIGURATION_URL = "https://mullvad.net/en/download/config/"
    TESTING_URL = "https://am.i.mullvad.net/json"

    c_vpn_config_dir = os.path.dirname(os.path.realpath(__file__)) + '/mullvad_openvpn_config_files'

    def __init__(self):
        self._browser = StatefulBrowser(user_agent="Firefox")
        self._settings = Settings()
        self._settings.read_settings()

    def _check_vpn(self, setup=False):
        # Check if VPN is active
        response = requests.get(self.TESTING_URL)
        print(response.json())

        # Check if IP's country is Sweden
        if response.json()["country"] == "Sweden":
            print("VPN is active!")
        else:
            if setup:
                print("Error: VPN was not installed!")
            else:
                try:
                    self._settings.get("user", "accountnumber")
                except Exception as e:
                    print("Error: Account not found, please purchase one!")
                    print(self._error_message(e))
                self.setup_vpn()

    # Automatically sets up VPN with settings from provider
    def setup_vpn(self):
        # Get the necessary files for connecting to the VPN service
        self._download_files()
        result = os.popen("sudo chmod -R 777 " + self.c_vpn_config_dir)

        # Copy files to OpenVPN folder
        result = os.popen("sudo cp -a " + self.c_vpn_config_dir + "/. /etc/openvpn/").read()
        print(result)

        os.chdir("/etc/openvpn/")

        # Start OpenVPN connection
        #result = os.popen("sudo nohup openvpn --config ./mullvad_se-sto.conf > /dev/null &").read()
        result = os.popen("sudo service openvpn start").read()
        print(result)

        # Sleep for 10 seconds, so that VPN connection can be established in the
        # mean time
        time.sleep(30)
        self._check_vpn(True)

    # Download configuration files for setting up VPN and extract them
    def _download_files(self):
        # Fill information on website to get right files for openVPN
        self._browser.open(self.CONFIGURATION_URL)
        form = self._browser.select_form()
        form["account_token"] = self._settings.get("user", "accountnumber")
        form["platform"] = "linux"
        form["region"] = "se-sto"
        form["port"] = "0"
        self._browser.session.headers["Referer"] = self._browser.get_url()
        response = self._browser.submit_selected()
        content = response.content

        # Create the folder that will store the configuration files
        if os.path.isdir(self.c_vpn_config_dir) == False:
            os.popen('mkdir ' + self.c_vpn_config_dir).read()

        # Download the zip file to the right location
        files_path = self.c_vpn_config_dir + "/config.zip"
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
            target = open(os.path.join(self.c_vpn_config_dir, filename), "wb")
            with source, target:
                shutil.copyfileobj(source, target)
        # Delete zip file
        os.remove(files_path)

if __name__ == '__main__':
    mullvad = InstallMullvad()
    mullvad._settings.put("user", "accountnumber", "6798499523758101")
    mullvad._settings.save_settings()
    mullvad._check_vpn()