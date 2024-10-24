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
- Add possible browser extensions that might aid in privacy while browsing (research required).
- Need to either fork seleniumwire, swap to Chromedriver + DevTools, or find a better maintained fork.
	- Because seleniumwire is not being maintained anymore, must use blinker 1.7.0 (pip install blinker==1.7.0)
	- Swap to Chromedriver + ChromeDevTools for now (it's native and won't require seleniumwire)
'''
import utils
import json
import random
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.proxy import Proxy
from selenium.webdriver.common.proxy import ProxyType


LOG_DIR = "./files/log"
LOG_FILE = "qb.log"
TEST_URL = "https://google.com"

class QuietBuster:

	def __init__(self, logger) -> None:
		self.log = logger
		self.agents = list()
		self.update_user_agents()
		
	def update_user_agents(self) -> None:
		with open('./files/useragents.txt', 'r') as file:
			lines = file.readlines()
			if len(lines) <= 0:
				self.agents = requests.get("https://gist.githubusercontent.com/pzb/b4b6f57144aea7827ae4/raw/cf847b76a142955b1410c8bcef3aabe221a63db1/user-agents.txt").text.split('\n')
			else:
				self.agents = [line.strip() for line in lines]

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


def driver():
	utils.create_path(LOG_DIR)
	logger = utils.build_logger(LOG_DIR, LOG_FILE)
	qb = QuietBuster(logger)
	qb.build()
	qb.check_url(TEST_URL)


if __name__ == "__main__":
	driver()