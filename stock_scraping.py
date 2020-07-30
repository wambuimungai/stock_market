import requests,json, re, csv, os
from config  import username, password
from lxml import html
from bs4 import BeautifulSoup

#open a session 
session_request = requests.session()

#build the url and request for authentication
login_url = "https://abacus.co.ke/auth/login"
result = session_request.get(login_url)

tree = html.fromstring(result.text)
#get the sessions login token
authenticating_token = list(set(tree.xpath("//input[@name='_token']/@value")))[0]
print(authenticating_token)


#create payload
payload = {'username': config.username,
           'password': config.password,
           '_token':authenticating_token   }

result = session_request.post(
    login_url,
    data = payload,
    headers = dict(referer = login_url)   
)
print(result.ok)
print(result.status_code)

#builds url and request JSON data from it
url = "https://abacus.co.ke/live/company/SCOM/charts"
result = session_request.get(
    url,
    headers = dict(referer=url)
)

soup = BeautifulSoup(result.content, 'html.parser')
script = soup.find('script', text=re.compile('Performance = ({.*?});'))
json_text = re.search(r'Performance = ({.*?});',script.string, flags=re.DOTALL |re.MULTILINE).group(1)
data = json.loads(json_text)
#print(data)
stock_details = data['data']

# check if path to file exists
if not os.path.exists('./output_files'):
	os.makedirs('./output_files')

#write  data to file
with open('./output_files/SCom_stocks.csv', 'w') as file:
	# create the csv writer object
	csvwriter = csv.writer(file)

	stock_row = 0

	for stock in stock_details:
    	if stock_row == 0:
        	header = stock.keys()
        	csvwriter.writerow(header)
        	stock_row += 1

    	csvwriter.writerow(stock.values())

