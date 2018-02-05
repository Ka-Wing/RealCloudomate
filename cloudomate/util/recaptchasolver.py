
import json, requests
from time import sleep

class reCaptchaSolver:

    __clientKey = "not set"

    def __init__(self, cKey):
        self.__clientKey = cKey

    def getBalance(self):
        r = requests.post('https://api.anti-captcha.com/getBalance',
                          json={"clientKey": self.__clientKey})

        if(r.status_code == requests.codes.ok):
            j = json.loads(r.text)
            if(j["errorId"] == 0):
                print("OK")
                return j["balance"]
            else:
                print(r.text)
                #handle api error
        else:
            print(r.status_code)
            #handle request error

    def __getTaskResult(self, taskId):
        r = requests.post('https://api.anti-captcha.com/getTaskResult',
                          json={"clientKey": self.__clientKey,
                                "taskId": taskId})

        if (r.status_code == requests.codes.ok):
            j = json.loads(r.text)
            if (j["errorId"] == 0):
                print("googleReCaptcha solved:")
                print(r.text)
                return j["solution"]
            else:
                print(r.text)
                # handle api error
        else:
            print(r.status_code)
            # handle request error



    def __getTaskStatus(self, taskId):
        r = requests.post('https://api.anti-captcha.com/getTaskResult',
                          json={"clientKey": self.__clientKey,
                                "taskId": taskId})

        if (r.status_code == requests.codes.ok):
            j = json.loads(r.text)
            if (j["errorId"] == 0):
                print("OK")
                return j["status"]
            else:
                print(r.text)
                # handle api error
        else:
            print(r.status_code)
            # handle request error

    def __createTaskGoogleReCaptcha(self,websiteURL,websiteKey):
        r = requests.post('https://api.anti-captcha.com/createTask',
                          json={"clientKey": self.__clientKey, "task":
                              {
                                  "type": "NoCaptchaTaskProxyless",
                                  "websiteURL": websiteURL,
                                  "websiteKey": websiteKey
                              },
                                "softId": 0,
                                "languagePool": "en"
                                })
        if (r.status_code == requests.codes.ok):
            j = json.loads(r.text)
            if (j["errorId"] == 0):
                print("OK" + r.text)
                return j["taskId"]
            elif(j["errorCode"] == "ERROR_NO_SLOT_AVAILABLE"):
                sleep(15)
                return self.__createTaskGoogleReCaptcha(websiteURL,websiteKey)
            else:
                print(r.text)
                # handle api error
        else:
            print(r.status_code)
            #handle request error

    def solveGoogleReCaptcha(self,websiteURL,websiteKey):
        taskId = self.__createTaskGoogleReCaptcha(websiteURL, websiteKey)
        print("sleeping 15 sec")
        sleep(15)
        currentStatus = self.__getTaskStatus(taskId)
        while currentStatus == "processing":
            print("current status: " + str(currentStatus))
            print("sleeping 5 sec")
            sleep(5)
            currentStatus = self.__getTaskStatus(taskId)
            print("current status: " + str(currentStatus))

        solution = self.__getTaskResult(taskId)
        return solution["gRecaptchaResponse"]

    def getCurrentKey(self):
        return self.__clientKey


