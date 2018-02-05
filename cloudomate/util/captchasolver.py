
import json, requests
from time import sleep
import os
import base64


class captchaSolver:

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

    def solveCaptchaTextCaseSensitive(self, fullImageFilePath):
        encoded_image_string = ""
        if(os.path.isfile(fullImageFilePath) == True):
            with open(fullImageFilePath, "rb") as image_file:
                encoded_image_string = base64.b64encode(image_file.read())
                print("image sucessfully encoded")
        else:
            print("error file path not fo")
            return

        taskId = self.__createTaskCaptchaTextCaseSensitive(encoded_image_string)
        currentStatus = self.__getTaskStatus(taskId)
        while currentStatus == "processing":
            print("sleeping 5 sec")
            sleep(5)
            currentStatus = self.__getTaskStatus(taskId)
            print("current status: " + str(currentStatus))

        solution = self.__getTaskResult(taskId)
        return solution["text"]



    def __getTaskResult(self, taskId):
        r = requests.post('https://api.anti-captcha.com/getTaskResult',
                          json={"clientKey": self.__clientKey,
                                "taskId": taskId})

        if (r.status_code == requests.codes.ok):
            j = json.loads(r.text)
            if (j["errorId"] == 0):
                print("captcha solved:")
                #print(r.text)
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


    def __createTaskCaptchaTextCaseSensitive(self,base64_image_string):
        r = requests.post('https://api.anti-captcha.com/createTask',
                          json={"clientKey": self.__clientKey, "task":
                              {
                                  "type": "ImageToTextTask",
                                  "body": base64_image_string,
                                  "phrase": False,
                                  "case": True,
                                  "numeric": False,
                                  "math": 0,
                                  "minLength": 0,
                                  "maxLength": 0
                              }
                                })

        if (r.status_code == requests.codes.ok):
            j = json.loads(r.text)
            if (j["errorId"] == 0):
                print("OK" + r.text)
                return j["taskId"]
            elif(j["errorCode"] == "ERROR_NO_SLOT_AVAILABLE"):
                sleep(15)
                return self.__createTaskCaptchaTextCaseSensitive(base64_image_string)
            else:
                print(r.text)
                # handle api error
        else:
            print(r.status_code)
            #handle request error

    def getCurrentKey(self):
        return self.__clientKey




