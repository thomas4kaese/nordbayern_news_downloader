from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
import time
import pathlib
import os

DEBUG_MODE = 0
EMAIL = """EMAIL"""
PASSWORD = """PASSWORD"""

# Create Browser instance
options = Options()
options.binary_location = "/usr/lib/chromium/chrome"
options.add_argument("--no-sandbox")
options.add_experimental_option("prefs", {
    "download.default_directory": str(pathlib.Path().resolve()), # Download PDF into current directory
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

if not DEBUG_MODE: options.add_argument("--headless")
# Website detects headless mode, we are thus faking a user client
if not DEBUG_MODE: options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")

# headless mode sometimes struggles with unsigned certificates, use the following in this case
# capabilities = DesiredCapabilities.CHROME.copy()
# capabilities['acceptSslCerts'] = True 
# capabilities['acceptInsecureCerts'] = True
browser = Chrome(executable_path=r'/usr/lib/chromium/chromedriver',options=options) # executable_path = r'PATH' if not in %PATH%
# browser = Chrome(options=options,desired_capabilities=capabilities) # executable_path = r'PATH' if not in %PATH%
browser.delete_all_cookies()

# Landing Page
browser.get('https://epaper.nn.de/')

###############################
#### STEP 0 Cookie Button   ### 
###############################

try:
    cookie_button = browser.find_element_by_class_name('cmpboxbtnyes')
    cookie_button.click()
    print('(Info) Step 0: Cookie accepted.')
except:
    print('(Warning) Step 0: No Cookie accepted.')
    
    
#######################
#### STEP 1 Login   ### 
#######################

try:
    loginname = browser.find_element_by_id('inputLogin')
    loginname.send_keys(EMAIL)

    loginpwd = browser.find_element_by_id('inputPass')
    loginpwd.send_keys(PASSWORD)

    loginbtn = browser.find_element_by_css_selector('#msp-login-form > p.grid_40 > input')
    loginbtn.click()
    print('(Info) Step 1: Successfully logged in.')
except:
    print('(Warning) Step 1: No Login failed.')


# Selecting "Nuernberger Nachrichten" - instead of clicking we browse its URL
# This is done by isolating 'secret' from URL
secret = browser.current_url.split("=")[-1]
browser.get('https://epaper.nn.de/titles/nnnurnbergernachrichten/12207/?secret=' + secret)


# Helping function for browsing shadow-roots
# from https://stackoverflow.com/questions/23920167/accessing-shadow-dom-tree-with-selenium
def expand_shadow_element(element):
    shadow_root = browser.execute_script('return arguments[0].shadowRoot', element)
    return shadow_root


###############################
#### STEP 2 Cookies contd.  ### 
###############################

# Accepting (all) cookies (again)

# hard sleep cos main will be instantly detected - albeit the wrong one due to splash screen
time.sleep(5)
try:
    root1 = browser.find_element_by_id('main')
    shadow_root1 = expand_shadow_element(root1)

    root2 = shadow_root1.find_element_by_css_selector('login-flow')
    shadow_root2 = expand_shadow_element(root2)

    root3 = shadow_root2.find_element_by_css_selector('gdpr-comp-consent')
    shadow_root3 = expand_shadow_element(root3)

    btn_accept = shadow_root3.find_element(By.CSS_SELECTOR, '.paper_green').click()
    print('(Info) Step 2: Cookie accepted.')
except:
    print('(Warning) Step 2: No Cookie accepted.')

    
###############################
#### STEP 3 Select issue   #### 
###############################

# hard sleep is probably needed here
time.sleep(5)

# Choosing latest issue cause yesterdays paper's telling yesterday's news
try:
    #root1 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'main')))
    root1 = browser.find_element_by_id('main')
    shadow_root1 = expand_shadow_element(root1)

    root2 = shadow_root1.find_element_by_css_selector('login-flow')
    shadow_root2 = expand_shadow_element(root2)

    root3 = shadow_root2.find_element_by_css_selector('cover-view')
    shadow_root3 = expand_shadow_element(root3)

    root4 = shadow_root3.find_element_by_css_selector('iron-image').click()
    print("""(Info) Step 3: Selected latest issue cause yesterdays paper's telling yesterday's news.""")
except:
    print('(Error) Step 3: Selecting issue failed.')

# Get issue from title; this is needed to checking the download progress since it is part of filename#
# date cant be use since sunday delivers saturday issue :-)
issue = browser.title

###############################
#### STEP 4 Download PDF   #### 
###############################

# hard sleep again
time.sleep(10)

# Accessing Button 'Download PDF'
try:
    root1 = browser.find_element_by_id('main')
    #root1 = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, 'main')))
    shadow_root1 = expand_shadow_element(root1)

    root2 = shadow_root1.find_element_by_css_selector('login-flow')
    shadow_root2 = expand_shadow_element(root2)

    root3 = shadow_root2.find_element_by_css_selector('issue-view')
    shadow_root3 = expand_shadow_element(root3)

    # we have to change into an iframe inside (root3) shadow-root
    iframe = shadow_root3.find_element_by_tag_name("iframe")
    browser.switch_to.frame(iframe)

    search = browser.find_element_by_xpath('//*[@id="pdfMenuItem"]')
    # we have to click the button by js injection since its not directly accessible
    browser.execute_script("arguments[0].click();", search);
    print('(Info) Step 4: Download started.')
except:
    print('(Warning) Step 4: Download could not start.')


def is_file_downloaded(filename, timeout=60):
    end_time = time.time() + timeout
    while not os.path.exists(filename):
        time.sleep(1)
        if time.time() > end_time:
            print("(Warning) Step 4: File not found before timeout. Check download folder or increase timeout")
            return False

    if os.path.exists(filename):
        print("(Info) Step 4: File found - exiting.")
        return True

# Filename example: 2021-06-26_Nuernberger_Nachrichten_-_2021-06-26.pdf
issue_date = issue.split(" ")[-1]
file_path = str(pathlib.Path().resolve()) + '/' + issue_date + '_Nuernberger_Nachrichten_-_' + issue_date + '.pdf'
print('(Info) Step 4: Filename is ' + file_path + '.')
if is_file_downloaded(file_path, 60):
    browser.close()
    browser.quit()
    # if not DEBUG_MODE: browser.close()
    # if not DEBUG_MODE: browser.quit()
