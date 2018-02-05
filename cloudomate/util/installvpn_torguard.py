import os
import urllib.request
import random
import requests
import re
import time

class installVpnTorguard():

    #Config files download location
    configurl_files_url_AES_UDP = 'https://torguard.net/downloads/OpenVPN-UDP.zip'
    configurl_files_url_AES_TCP = 'https://torguard.net/downloads/OpenVPN-TCP.zip'

    #directories for saving config files
    c_logdir = os.path.dirname(os.path.realpath(__file__)) + '/torguard_log'
    c_vpn_config_dir = os.path.dirname(os.path.realpath(__file__)) + '/torguard_openvpn_config_files'
    c_userpass_dir = os.path.dirname(os.path.realpath(__file__)) + '/torguard_open_vpn_userpass'

    #config folder names (folders zip file extracts to)
    c_config_AES256TCP_folder_name = 'OpenVPN-TCP'
    c_config_AES256UDP_folder_name = 'OpenVPN-UDP'

    userpass_file_name = 'user.txt'

    #username en passw for open vpn: NOTE these are NOT THE SAME as vpnac-web login credentials
    vpnusern_ = '-'
    vpnpassw_ = '-'

    # Selenium webdriver
    driver = None

    #arguments username and password are required by openvpn service
    def __init__(self,openvpn_user = '-', openvpn_passw = '-'):

        if openvpn_user != '-' and openvpn_passw != '-':
            self.vpnusern_ = openvpn_user
            self.vpnpassw_ = openvpn_passw
            print("\nusername set to: '" + self.vpnusern_ + "'")
            print("\npassword set to: '" + self.vpnpassw_ + "'")
            return
            pass

        openvpn_auth_file = self.c_userpass_dir + '/' + self.userpass_file_name
        if os.path.isfile(openvpn_auth_file):
            file = open(openvpn_auth_file, "r")
            lines = file.readlines()
            self.vpnusern_ = lines[0].replace('\n', '').replace('\r', '')
            self.vpnpassw_ = lines[1].replace('\n', '').replace('\r', '')
            print("--opnvpnusern found : " + self.vpnusern_)
            print("--opnvpnpassw found : " + self.vpnpassw_)
            return
            pass

        web_login_file = os.path.dirname(os.path.realpath(__file__)) + '/torguard_login.txt'
        if os.path.isfile(web_login_file):
            raise Exception("Only weblogin credentials found: please run torguard_service_auth_retriever.py before calling this script to retrieve service credentials from web credentials")
            return
            pass
        elif openvpn_passw == '-' or openvpn_passw == '-':
            print("\n**************************************\n\n")
            print("\nError: No login Credentials found file: 'vpnac_login.txt' does not exist in current path")
            print("\nPlease provide web-login crdentials by purchasing a vpnac service trough the vpnac_purchase.py script ")
            print("\nOR openvpn auth credentials (not the same as web credentials) manually as paramters directly to the script")
            print("\n\n**************************************\n\n")
            raise Exception("no credentials for neither web scraping nor openvpn found")
            pass

        pass

    #start vpn with either Standard TCP or UDP
    def startVpn(self, UDP = False):

        #Either set the config dir to point to eiter the TCP or UDP folder (depending on which was specified for download)
        self.download_config_files(UDP)
        c_dir = self.c_vpn_config_dir + '/' + self.c_config_AES256TCP_folder_name
        if UDP:
            c_dir = self.c_vpn_config_dir + '/' + self.c_config_AES256UDP_folder_name
            pass

        #create a list of all the areas trough which traffic can be routed
        file_list = os.popen('ls ' + c_dir + '/').read()

        options = file_list.splitlines()

        use_ta_key = False

        #remove ca.crt and ta.key from routing options
        if 'ca.crt' in options:
            options.remove('ca.crt')
            pass
        if 'ta.key' in options:
            use_ta_key = True
            options.remove('ta.key')
            pass

        random_country = random.randint(0,len(options))
        random_vpn = options[random_country]
        file_ = c_dir + '/' + random_vpn
        userpassfile = self.c_userpass_dir + '/' + self.userpass_file_name
        print(userpassfile)

        c_config_crt = self.c_vpn_config_dir + '/' + self.c_config_AES256TCP_folder_name + '/ca.crt'
        c_config_key = self.c_vpn_config_dir + '/' + self.c_config_AES256TCP_folder_name + '/ta.key'

        if UDP:
            c_config_crt = self.c_vpn_config_dir + '/' + self.c_config_AES256UDP_folder_name + '/ca.crt'
            c_config_key = self.c_vpn_config_dir + '/' + self.c_config_AES256UDP_folder_name + '/ta.key'
            pass

        print(c_config_crt)

        startvpn_cm = 'openvpn --config ' + file_ + ' --script-security 2 --dhcp-option DNS 8.8.8.8 --up /etc/openvpn/update-resolv-conf --down /etc/openvpn/update-resolv-conf --ca ' + c_config_crt + ' --auth-user-pass ' + userpassfile
        if use_ta_key == True:
            startvpn_cm = 'openvpn --config ' + file_ + ' --script-security 2 --dhcp-option DNS 8.8.8.8 --up /etc/openvpn/update-resolv-conf --down /etc/openvpn/update-resolv-conf --ca ' + c_config_crt + ' --tls-auth ' + c_config_key + ' 1 ' + ' --auth-user-pass ' + userpassfile
            pass

        print(startvpn_cm)
        output = os.popen(startvpn_cm).read()
        print(output)

    def download_config_files(self, UDP = False):

        #variable for storing some log information
        logging_info = "\n----------\n\n"

        #create config dir if they dont exist already
        if os.path.isdir(self.c_logdir) == False:
            os.popen('mkdir ' + self.c_logdir).read()
            pass
        if os.path.isdir(self.c_vpn_config_dir) == False:
            os.popen('mkdir ' + self.c_vpn_config_dir).read()
            pass
        if os.path.isdir(self.c_userpass_dir) == False:
            os.popen('mkdir ' + self.c_userpass_dir).read()
            pass

        #full file path and file name to which we will save the vpn config zip file
        file_test = os.path.dirname(os.path.realpath(__file__)) + '/toruguardconfig.zip'

        #the name of the folder that the zip file for the specified protocol wil extract
        foldername = self.c_config_AES256TCP_folder_name

        # downoad the correct config zip file for the specified protocol
        if(UDP == True):
            res = requests.get(self.configurl_files_url_AES_UDP)
            with open(file_test, 'wb') as output:
                output.write(res.content)
                pass
            pass
        else:
            res = requests.get(self.configurl_files_url_AES_TCP)
            with open(file_test, 'wb') as output:
                output.write(res.content)
                pass
            pass

        #unzip the openvpn config files to the config openvpn dir
        unzip_command = 'unzip -o ' + file_test + ' -d ' + self.c_vpn_config_dir + '/'
        logging_info += os.popen(unzip_command).read()

        #dir containing the vpn files for the specified protocol (UDP or TCP)
        config_file_dir = self.c_vpn_config_dir + '/' + foldername

        #remove the zip file after it has been unzipped to the config dir (zip file no longer needed)
        logging_info += os.popen('rm ' + file_test).read()

        #save user info required for vpn
        contents = self.vpnusern_ + "\n" + self.vpnpassw_
        filedir = self.c_userpass_dir + '/' + self.userpass_file_name
        print(filedir)
        self.saveTofile(contents,filedir)
        pass

    def saveTofile(self, file_contents, full_file_path):
        tempfile = open(full_file_path, 'w')
        tempfile.write(file_contents)
        tempfile.close()
        pass

if __name__ == '__main__':
    vpntoruguard = installVpnTorguard()
    vpntoruguard.startVpn()
