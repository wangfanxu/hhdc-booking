#!/usr/bin/env python

import time
import helper
import mail
from selenium import webdriver
from pyvirtualdisplay import Display
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options


CHROME_PATH = "chrome_path"
BBDC_MAINFRAME = 'https://www.bbdc.sg/bbdc/b-mainframe.asp'
BBDC_WEBSITE = 'https://www.bbdc.sg'
DEFAULT_TIMEOUT = 5

# config keys
BBDC = "bbdc"
USERNAME = "username"
PASSWORD = "password"
GMAIL = "gmail"
EMAIL = "email"
WANT_MONTHS = "want_months"
WANT_SESSIONS = "want_sessions"
WANT_DAYS = "want_days"
# EXCLUDE_DAYS = "exclude_days"

def init_driver(path):
    chrome_options = Options()
    # argument to switch off suid sandBox and no sandBox in Chrome
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-setuid-sandbox")

    chrome_driver = webdriver.Chrome(executable_path=path)
    chrome_driver.wait = WebDriverWait(chrome_driver, DEFAULT_TIMEOUT)
    return chrome_driver

class BBDCClass:

    driver = []
    display = []



    def verify_access(self):
        print('try direct access without re-login')
        self.driver.get(BBDC_MAINFRAME)

        time.sleep(0.1)

        expired = self.driver.find_elements_by_xpath("//*[contains(text(), 'Session Expired')]")

        if len(expired) == 0:
            return True # not expired
        else:
            return False

    def login(self, username, password):
        
        print("start login")
        self.driver.get(BBDC_WEBSITE)

        # switch to frame
        time.sleep(0.1)
        frame = self.driver.find_element_by_id("login_style").find_element_by_tag_name("iframe")
        self.driver.switch_to_frame(frame)

        # key in username & password to login
        form = self.driver.find_element_by_tag_name("form")
        nric = form.find_element_by_name("txtNRIC")
        pwd = form.find_element_by_name("txtPassword")
        login_btn = form.find_element_by_name("btnLogin")

        nric.clear()
        nric.send_keys(username)
        pwd.clear()
        pwd.send_keys(password)
        login_btn.click()
        print("complete login")


    def to_practical_test(self):
        print("to practical test")
        # switch to left frame
        self.driver.switch_to_frame("leftFrame")

        # go to terms and conditions page
        time.sleep(0.1)
        a = self.driver.find_element_by_xpath("/html/body/table/tbody/tr/td/table/tbody/tr[9]/td[3]/a")
        print(a.get_attribute('innerHTML'))
        a.click()
        self.driver.switch_to_default_content()


    def agree_terms(self):
        print("agree terms")
        # switch to main frame
        self.driver.switch_to_frame("mainFrame")

        # agree
        time.sleep(0.1)
        button = self.driver.find_element_by_xpath("/html/body/table/tbody/tr[4]/td[1]/input")
        print(button.get_attribute('value'))
        button.click()
        self.driver.switch_to_default_content()


    def select_filer(self, want_months, want_sessions, want_days):
        print("select months: " + str(want_months))
        print("select sessions: " + str(want_sessions))
        print("select days: " + str(want_days))
        # switch to main frame
        self.driver.switch_to_frame("mainFrame")

        # select all months, all sessions, all days
        time.sleep(0.1)

        month_boxes = self.driver.find_elements_by_name("Month")
        session_boxes = self.driver.find_elements_by_name("Session")
        days_boxes = self.driver.find_elements_by_name("Day")

        for month_box in month_boxes:
            if month_box.get_attribute("value") in want_months:
                month_box.click()
        
        for session_box in session_boxes:
            if session_box.get_attribute("value") in want_sessions:
                session_box.click()
        
        for days_box in days_boxes:
            if days_box.get_attribute("value") in want_days:
                days_box.click()

        time.sleep(0.1)

        search_btn = self.driver.find_element_by_name("btnSearch")
        search_btn.click()

        # check if alert pop up

        try:
            self.driver.wait.until(EC.alert_is_present(),'Time out waiting for alert pop up')
            alert = self.driver.switch_to_alert()
            alert.accept()
            print("alert accepted")
        except TimeoutException:
            print("no alert")

        self.driver.switch_to_default_content()


    def find_available_slots(self):
        print("find available slots")
        times = []

        # switch to main frame
        self.driver.switch_to_frame("mainFrame")

        # find slots
        time.sleep(0.1)
        radios = self.driver.find_elements_by_xpath("//input[@type='checkbox']")
        print('Length of radios = ' + str(len(radios)) )
        for radio in radios:
            td = radio.find_element_by_xpath('..')
            text = td.get_attribute("onmouseover")
            parts = text.split(",")
            session = parts[3]
            session = session.replace('"', '')
            # if session in want_sessions:
            #     # only allows monday to friday
            #     if not parts[2].endswith(tuple(exclude_days)):
            current = helper.format_session(session, parts)
            times.append(current)

        return times

    def startDisplay(self):
        self.display = Display(visible=1, size=(800, 600))
        self.display.start()

        self.driver = init_driver('chromedriver')

    def stopDisplay(self):
        self.display.stop()
        self.driver.quit()

    def check_bbdc(self):

        config = helper.read_config()
        email = config[GMAIL][EMAIL]
        pwd = config[GMAIL][PASSWORD]

        msg = "NIL"
        slots = []

        try:

            login_valid = self.verify_access()

            if login_valid == True:
                print('login still valid')
            else:
                print('login expired')
                self.login(config[BBDC][USERNAME], config[BBDC][PASSWORD])

            self.to_practical_test()

            self.agree_terms()

            self.select_filer(config[WANT_MONTHS], config[WANT_SESSIONS], config[WANT_DAYS])

            time.sleep(1)

            slots = self.find_available_slots()

            # browser.quit()

            if len(slots) > 0:
                subject = "Book BBDC Practical Session"
                msg = "all available sessions: \n"
                for slot in slots:
                    msg += slot + "\n"
                # mail.send(email, pwd, email, subject, msg)
            else:
                msg = "No wanted session"
                
        except Exception as e:
            print(e)
            subject = "BBDC Auto Booking Error"
            msg = str(e)
            # mail.send(email, pwd, email, subject, msg)

        print(msg)
        return (len(slots), msg)

# if __name__ == "__main__":
#     check_bbdc()