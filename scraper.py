from bs4 import BeautifulSoup
import requests
import time
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Controls
loginUrl = "https://www.kuulaportti.fi/?page=login"             # Website's login page url.
url = "https://www.kuulaportti.fi/?page=event&id=469#tickets"   # The game's kuulaportti.fi url, !!! Has to end in #tickets !!!
elementNmbr = 2                                                 # Faction number in the factions bar, I.e. 1 = first faction, 2 = second, 3 = third etc.
paymentMethod = 4                                               # Payment method option,  0 = no payment window, 1 = first option, 2 = second, etc.
checkbox = 1                                                    # Possible checkbox's index in Custom-control-input class list, 0 = no checkbox, 1 = first element in the list, 2 = second, etc.
interval = 5                                                    # Refresh rate in seconds

emails = []                                                     # Emails of the accounts to get tickets for
passwords = []                                                  # Passwords of the accounts in order
tickets = 3                                                     # How many tickets to buy
driverPath = "C:\chromedriver\chromedriver.exe"                 # Path to Chrome WebDriver exe file

# Pew-Pew's Game preset settings:
# elementNmbr = 2
# paymentMethod = 4 
# checkbox = 1   

# Others preset settings:
# elementNmbr = 1
# paymentMethod = 0 
# checkbox = 0   

# TODO: ADD YOUR OWN COOKIE !!!!
cookies = {
    '_ga': 'GA1.1.54546288.1648319799',
    'PHPSESSID': 'ja32s8alk44dp3p4tpghsn7sqt',
    'kuulaportti_cookie': '<ADD YOUR OWN COOKIE HERE>',
    '_ga_FT0P5VGHWF': 'GS1.1.1659660509.64.1.1659661013.0',
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:104.0) Gecko/20100101 Firefox/104.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://www.kuulaportti.fi/index.php',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
}
params = {
    'page': 'event',
    'id': url[url.index('id=')+3:url.index('#')],
}

# Initialize iterators
elementNmbr -= 1
checkbox -= 1
l = 0
i = 0


# Check if there is room in a game
def scan(elementNmbr, params, cookies, headers, interval, i, l, emails):
    while True:
        # Get the webpage
        response = requests.get('https://www.kuulaportti.fi/index.php', params=params, cookies=cookies, headers=headers)

        # get tags
        soup = BeautifulSoup(response.content, 'html.parser')
        tags = soup.find_all("p", { "class" : "inbox-item-text" })
        length = len(tags) - 1

        # Get the text in the specified element
        element = tags[elementNmbr].getText()
        element = element[0:element.index(" ")]

        # Set current amount of players signed up, and max amount of players signed up
        cpc = element[0:element.index("/")]
        mpc = element[element.index("/")+1:len(element)]
        i += 1

        # Print status
        print("Tickets reserved %s, Current account: %s, %s players, Iteration #%i @ %s" % (l, emails[l], element, i, datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")))

        # If there's a slot available take it
        if(int(cpc) < int(mpc)):
            return [length, i]

        # Otherwise wait for set amount of time
        time.sleep(interval)


# Login to the website
def driverLogin(driver, email, password, sleepInterval, loginUrl):
    # Get login page and wait for a set amount of time before the next action
    driver.get(loginUrl)
    time.sleep(sleepInterval)

    # Get email field and type email
    emailfield = driver.find_element(By.ID, "email")
    emailfield.send_keys(email)

    # Get password field and type password, then hit enter to log in
    passfield = driver.find_element(By.ID, "password")
    passfield.send_keys(password)
    passfield.send_keys(Keys.ENTER)

    # Wait for a set amount of time before the next action
    time.sleep(sleepInterval)

# get the website
def driverGetPage(driver, url, sleepInterval):
    driver.get(url)
    time.sleep(sleepInterval)


# Click somewhere
 # driver = Webdriver
 # className = classname to differentiate the element with i.e. "class1"
 # elementNmbr = Number of the element in the list of similar elements
 # waitInterval = How long to wait at maximum for a step to complete
 # sleepInterval =  How long to wait before doing anything after the click
def driverClick(driver, className, elementNmbr, waitInterval, sleepInterval):
    # Get defined element
    button = driver.find_elements(By.CLASS_NAME, className)[elementNmbr]

    # Wait at max for waitInterval for event to complete
    driver.implicitly_wait(waitInterval)

    # Move the mouse to and click the specified element
    ActionChains(driver).move_to_element(button).click(button).perform()

    # Wait for a set amount of time before the next action
    time.sleep(sleepInterval)


# Initialize the webdriver
def driverInit(driverPath):
    driver = webdriver.Chrome(executable_path=driverPath)
    driver.maximize_window()
    return driver


while l < len(emails):
    if(l >= tickets):
        break
    email = emails[l]
    password = passwords[l]
    
    # scan for change
    returns = scan(elementNmbr, params, cookies, headers, interval, i, l, emails)

    # page changed, do something
    length = returns[0]
    i = returns[1]

    driver = driverInit(driverPath)                                             # Initialize webdriver
    driverLogin(driver, email, password, 1, loginUrl)                           # Login to webpage
    driverGetPage(driver, url, 1)                                               # Get wanted ewbpage

    driverClick(driver, "clickable", elementNmbr, 5, 1)                         # Select team
    if(checkbox >= 0):
        driverClick(driver, "custom-control-input", checkbox, 5, 1)             # Click checkbox if there
    if(paymentMethod > 0):
        payment = length + paymentMethod
        driverClick(driver, "clickable", payment, 5, 1)                         # Select payment method
    driver.find_element(By.ID, "buy_ticket").click()                            # Buy ticket
    time.sleep(3)
    driver.quit()
    l += 1
tic = 0
ticketed = []


# Get accounts with tickets
while tic < l:
    ticketed.append(emails[tic])
    tic += 1

# Print status
print("Number of tickets reserved %s, scan concluded at %s" % (l, datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")))

# Get total time spent
seconds = i * interval
m, s = divmod(seconds, 60)
h, m = divmod(m, 60)
d, h = divmod(h, 24)

# Print total uptime
print("Total uptime: %d days %dh %02dmin %02dsec" % (d, h, m, s))

# Print names of accounts who got tickets
print("tickets are on accounts:")
for val in ticketed:
    print(val)