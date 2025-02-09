from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import selenium.common.exceptions as EX
from time import sleep


CHROME_PROFILE_PATH = './CustomProfile'
WEBAPP_URL = 'https://www.easports.com/fifa/ultimate-team/web-app/'

def countdown(t):
	while t:
		mins, secs = divmod(t, 60)
		timeformat = '[WAIT] {:02d}:{:02d}'.format(mins, secs)
		print(timeformat, end='\r')
		sleep(1)
		t -= 1


class WebAppBot:
    def __init__(self, username, pw):
        self.username = username
        self.pw = pw
        self.options = webdriver.ChromeOptions()
        self.driver = None
        self.retries = 10

        self.set_options()
        self.open_chrome()


    def quit(self):
        input('Press Enter to exit')
        self.driver.quit()
        exit()


    def set_options(self):
        self.options.add_experimental_option('excludeSwitches', ['enable-logging']) # comment this line to see driver logs
        self.options.add_argument('--disable-extensions')
        self.options.add_argument('--profile-directory=Profile 1')
        self.options.add_argument('--user-data-dir=' + CHROME_PROFILE_PATH)
        self.options.add_argument('--start-maximized')
        #self.options.add_argument('--headless')
        #self.options.add_argument('--remote-debugging-port=45600')


    def open_chrome(self):
        try:
            print('[LOG] Opening Chrome...')
            self.driver = webdriver.Chrome(options=self.options)
            print('[SUCCESS] Chrome opened')
        except Exception as e:
            print('[FAIL]', e)
            exit()


    def open_webapp(self):
        print('[LOG] Opening WebApp...')
        self.driver.get(WEBAPP_URL)
        try:
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ut-fut-logo')))
            print('[SUCCESS] WebApp opened')
        except EX.TimeoutException:
            print('[FAIL] Timeout')
            raise


    def login(self):
        print('[LOG] Logging in...')
        sleep(1)

        try:
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.btn-standard.call-to-action')))
            self.driver.find_element_by_css_selector('button.btn-standard.call-to-action').click()

            print('[LOG] Trying to log in...')
            try:
                WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="email"]')))
                self.driver.find_element_by_xpath('//*[@id="email"]').clear()
                self.driver.find_element_by_xpath('//*[@id="email"]').send_keys(self.username)
                self.driver.find_element_by_xpath('//*[@id="password"]').send_keys(self.pw)
                self.driver.find_element_by_xpath('//*[@id="logInBtn"]').click()

                print('[LOG] Is there an error ?')
                try:
                    self.login_verification()

                    self.driver.find_element_by_xpath('//*[@class="general-error"]')
                    print("[FAIL] Login failed ! Wrong email or password")
                    self.quit()
                except EX.NoSuchElementException:
                    print("[SUCCESS] Logged in!")
                    WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.CLASS_NAME, 'ut-click-shield')))
            except EX.TimeoutException:
                print('[FAIL] Timeout: probably already logged in')

        except EX.TimeoutException:
            print('[SUCCESS] Already logged in')

        self.wait_webapp_loaded()


    def login_verification(self):

        print('login_verification');

        try:
            WebDriverWait(self.driver, 1).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="btnSendCode"]')))
        except EX.TimeoutException:
            print('no verif');
            return 'no verif'

        try:
            print('[VERIFICATION] Looks like it is the first time you are using this.')
            print('[VERIFICATION] EA need to verify your identity')
            print('[VERIFICATION] You will receive a code:')
            self.driver.find_element_by_xpath('//*[@id="btnSendCode"]').click()
        except Exception:
            print('[FAIL]', e)
            print('[FAIL] Try to manually enter the code, then restart the program')
            raise

        repeat = True
        while repeat:
            code = input('[VERIFICATION] Please type in the code you received: ')
            self.driver.find_element_by_xpath('//*[@id="twoFactorCode"]').send_keys(code)
            self.driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()
            sleep(1)
            try:
                status_message = self.driver.find_element_by_xpath('//*[@id="origin-tfa-container"]/div/span[3]').text
                if status_message != 'Incorrect code entered':
                    repeat = False
            except EX.NoSuchElementException:
                repeat = False


    def wait_webapp_loaded(self):
        print('[LOG] Loading WebApp...')
        try: # ? Sometimes "click-shield" intercepts the click
            WebDriverWait(self.driver, 60).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'ut-click-shield')))
            sleep(1)
            WebDriverWait(self.driver, 60).until(EC.invisibility_of_element_located((By.CLASS_NAME, 'ut-click-shield')))

            print('[SUCCESS] WebApp loaded')
        except EX.TimeoutException:
            print('[FAIL] Timeout')
            raise
        except Exception as e:
            print('[FAIL]', e)
            raise


    def click_transfers(self):
        print('[LOG] Clicking on Transfers')
        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'Transfers')]").click()
            self.wait_webapp_loaded()
        except Exception as e:
            print('[FAIL]', e)
            raise


    def click_transfer_list(self):
        print('[LOG] Clicking on Transfer List')
        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'Transfer List')]").click()
            self.wait_webapp_loaded()
        except EX.TimeoutException:
            print('[FAIL] Timeout')
            raise


    def relist_all(self):
        print('[LOG] Looking for players to relist...')

        self.click_transfers()
        self.click_transfer_list()

        try:
            self.driver.find_element_by_xpath("//*[contains(text(), 'Re-list All')]").click()
            self.wait_webapp_loaded()
            try:
                self.driver.find_element_by_xpath("//*[contains(text(), 'Yes')]").click()
                print('[SUCCESS] Players relisted')
                self.wait_webapp_loaded()
            except EX.TimeoutException as e:
                print('[FAIL] Timeout', e)
                raise
        except EX.ElementNotInteractableException:
            print('[SUCCESS] No players to relist')
            raise


    def auto_relist(self): # main loop
        try:
            while True:
                try:
                    self.open_webapp()
                    self.login()
                    self.relist_all()

                    print('[WAIT] Do not close the window! You can minimize it')
                    print('[WAIT] Press Ctrl+C to close the program')
                    countdown(3630)
                except Exception as e:
                    if (self.retries < 0):
                        self.quit()

                    self.retries -= 1
                    print('[ERROR] An Error occured, try again n 10 Minutes')
                    countdown(600)

        except KeyboardInterrupt:
            self.quit()
