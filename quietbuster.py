'''
This program aims to be a subdomain, directory, & file bruteforcer utilizing webdrivers emulating real human behavior.
The goal of this project is to be able to circumvent the most detection mechanisms possible while remaining as versitile and
website agnostic as possible.

Features:

@todo:
- Create a class that spawns headless webdrivers in a threadpool w/ sessions, unique proxies, & random UAs.
	- Load directories and subdomains from a file.
	- Load proxies from a file or an external API, as well as test them for usability.
- Implement human based movement, behavior, and interaction with webapps.
	- Add random scroll.
	- Add random mouse movement.
	- Add window resize to common size.
	- Add slight window resize.
	- Add randomized time delay typing.
	- Add CAPTCHA solving (almost certainly using an API... $)
- Add possible browser extensions that might aid in privacy while browsing (research required).
- Need to either fork seleniumwire, swap to Chromedriver + DevTools, or find a better maintained fork.
	- Because seleniumwire is not being maintained anymore, must use blinker 1.7.0 (pip install blinker==1.7.0)
	- Swap to Chromedriver + ChromeDevTools for now (it's native and won't require seleniumwire) [x]
'''
import utils
import json
import random
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

LOG_DIR = "./files/log"

LOG_FILE = "qb.log"

TEST_URL = "https://google.com"
UA_URL = "https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt"

SEARCH_XPATH = "//textarea[contains(@title, 'Search')]"


class QuietBuster:

	def __init__(self, logger) -> None:
		self.log = logger
		self.ua_url = UA_URL
		self.home_urls = ["https://google.com"]
		self.seed = random.choice(self.home_urls)
		self.agents = list()
		self.update_user_agents()
		
	def update_user_agents(self) -> None:
		with open('./files/useragents.txt', 'r') as file:
			lines = file.readlines()
			if len(lines) <= 0:
				self.agents = requests.get(self.ua_url).text.splitlines()
			else:
				self.agents = [line.strip() for line in lines if line.strip()] # Only non empty stripped

	def build(self) -> None:
		'''
		Spawns a Chromedriver.  Currently chromedriver is the only webdriver with performance logging AFAIK.
		# Add: spawn webdrivers with custom options, specifically proxies / UA / window sizing.
		'''
		chrome_options = Options()
		chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
		chrome_options.page_load_strategy = 'normal'
		agent = random.choice(self.agents)
		chrome_options.add_argument(f"user-agent={agent}")
		self.log.debug(f"Using {agent}...")

		self.drive = webdriver.Chrome(options=chrome_options)
		self.log.debug("Chromedriver booted...")

	def check_url(self, url: str) -> None:
		'''
		Checks a given URL for it's response status code.
		'''
		self.drive.get(url)
		logs = self.drive.get_log('performance') # Grabbing performance logs
		for log in logs:
		    message = json.loads(log['message'])['message'] # https://chromedevtools.github.io/devtools-protocol/tot/Network/#type-Response
		    if 'Network.responseReceived' in message['method'] and 'response' in message['params']: # Parse responseReceived for response data
		        status_code = message['params']['response']['status']
		        url = message['params']['response']['url']
		        self.log.debug(f"URL: {url}, Status Code: {status_code}")

	def humanize_init(self) -> None:
		'''
		'Humanizes' the browser by going to a seed url (typically a search engine).
		'''
		self.go_to_home()

	def go_to_home(self) -> None:
		'''
		Initial URL to navigate to during spawning of browser.
		'''
		self.set_random_seed_uri()
		self.drive.get(self.seed)
		self.google_nav_humanize()

	def set_random_seed_uri(self) -> None:
		self.seed = random.choice(self.home_urls)

	def google_nav_humanize(self) -> None:
		'''
		Serves as a function to navigate from home to another page, via search bar or links on the page.
		** HLB - indicates function utilizes human like behavior.
		'''
		search_xpath = self.xpath_nav()
		if search_xpath is None:
			self.log.debug("Search box not found. Exiting function.")
			return  # Exit if the element is not found
		if not self.agents:
			return
		amount = random.randint(2, 8)
		for _ in range(amount):
			search_xpath.send_keys(random.choice(self.agents)[random.randint(0, 6)])
			time.sleep(random.uniform(3,10))
		search_xpath.send_keys(Keys.ENTER)
		time.sleep(random.uniform(10,15))

	def xpath_nav(self) -> None:
	    element = WebDriverWait(self.drive, random.uniform(7, 14)).until(EC.visibility_of_element_located((By.XPATH, "//input[@name='q']")))
	    print(element)
	    return element  # This will return None if the element was not found



def driver():
	utils.create_path(LOG_DIR)
	logger = utils.build_logger(LOG_DIR, LOG_FILE)
	qb = QuietBuster(logger)
	qb.build()
	qb.humanize_init()
	qb.check_url(TEST_URL)


if __name__ == "__main__":
	driver()