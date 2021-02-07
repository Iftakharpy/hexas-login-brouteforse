import requests
import re
import time
import random


class LoginError(Exception):
    message = "You aren't logged in!"
    def __init__(self, message=None):
        if message:
            self.message = message

    def __str__(self):
        return self.message


class Login:
    LOGIN_URL = "http://appsznd.hexaszindabazar.com/index.php"
    REQUEST_HEADERS = {'User-Agent': 'Mozilla/5.0'}

    PAGE_TITLE = b""
    LOGIN_PAGE_TITLE = b"HEXA'S ZINDABAZAR "
    HOME_PAGE_TITLE = b"HEXA'S Student Management System"

    # regular expresions
    PAGE_TITLE_REXP = re.compile(br"<title>(.*)</title>")
    USER_NAME_REXP = re.compile(br"<p style=\"font-width:bold; color:white;\"> Welcome,  (.*) </p>")
    ALERT_REXP = re.compile(br"alert\('(.*)'\)")

    #data
    USER_NAME = b""
    ALERT_MESSAGE = b""
    WRONG_USER_NAME_ERROR_MESSAGE = b"Username doesnot exists"
    WRONG_PASSWORD_ERROR_MESSAGE = b"Incorrect username/password combination"
    MIN_REQUEST_INTERVAL = 1 # wait for N seconds
    MAX_REQUEST_INTERVAL = 3 # wait for N seconds

    def __init__(self, user_id, password, tries = 1):
        self.credentials = {
            "user_name": user_id,
            "password": password
            }
        try:
            self.RESPONSE = requests.post( # post reqeust to the hexas login page
                url = self.LOGIN_URL,
                headers = self.REQUEST_HEADERS,
                data = self.credentials
                )

            if self.is_logged_in():
                self.get_user_name()
        except requests.exceptions.ConnectionError:
            random_interval = random.uniform(self.MIN_REQUEST_INTERVAL, self.MAX_REQUEST_INTERVAL)
            time.sleep(random_interval)
            print(f"requests.exceptions.ConnectionError raised on ID: {self.credentials['user_name']} current retry: {tries}")
            self.__init__(user_id, password, tries+1)
    
    def __repr__(self):
        return self.__str__()
    
    def __str__(self):
        return f"{self.__class__.__name__}({self.credentials})"

    def is_logged_in(self):
        #making sure the page title is updated
        self.get_page_title()

        if self.PAGE_TITLE == self.LOGIN_PAGE_TITLE:
            return False
        elif self.PAGE_TITLE == self.HOME_PAGE_TITLE:
            return True
        return False
    
    def is_username_possible(self):
        """Return the possibility of the username being correct"""
        self.get_alert_message()
        return self.ALERT_MESSAGE != self.WRONG_USER_NAME_ERROR_MESSAGE
        
    def get_page_title(self):
        if self.PAGE_TITLE:
            return self.PAGE_TITLE

        #extracting the page title from self.RESPONSE obj
        match_obj = self.PAGE_TITLE_REXP.search(self.RESPONSE.content)
        if match_obj:
            self.PAGE_TITLE = match_obj.group(1)
        else:
            self.PAGE_TITLE = "Coudn't find any page title!"

        return self.PAGE_TITLE
        
    def get_user_name(self):
        if not self.is_logged_in():
            raise LoginError

        if self.USER_NAME:
            return self.USER_NAME.decode('utf-8').strip()

        #extracting the user name from self.RESPONSE obj
        match_obj = self.USER_NAME_REXP.search(self.RESPONSE.content)
        if match_obj:
            self.USER_NAME = match_obj.group(1)
        else:
            self.USER_NAME = "Coudn't find any username!"
            return self.USER_NAME

        return self.USER_NAME.decode('utf-8').strip()
    
    def get_alert_message(self):
        if self.ALERT_MESSAGE:
            return self.ALERT_MESSAGE

        #extracting the alert message from self.RESPONSE obj        
        match_obj = self.ALERT_REXP.search(self.RESPONSE.content)
        if match_obj:
            self.ALERT_MESSAGE = match_obj.group(1)
        else:
            self.ALERT_MESSAGE = b"Couldn't find any Alert Message!"

        return self.ALERT_MESSAGE
    
    