import requests,json, re, csv, os, argparse
from config  import username, password
from lxml import html
from bs4 import BeautifulSoup

#open a session 
session_request = requests.session()

#build the url and request for authentication
login_url = "https://abacus.co.ke/auth/login"
result = session_request.get(login_url)

tree = html.fromstring(result.text)
authenticating_token = list(set(tree.xpath("//input[@name='_token']/@value")))[0]#get the sessions login token
#print(authenticating_token)

#create payload
payload = {'username': username,
           'password': password,
           '_token':authenticating_token   }

result = session_request.post(
    login_url,
    data = payload,
    headers = dict(referer = login_url)   
)
#print(result.ok)
#print(result.status_code)

#get companies to add to url path
def setup(code_path):
    with open(code_path) as file:
        company_codes = [x.rstrip() for x in file]

    return company_codes    


# pass the company codes to the url
def company_url(company_code):
    #builds url and request JSON data from it
    url = f"https://abacus.co.ke/live/company/{company_code}/charts"
 
    result = session_request.get(
        url,
        headers = dict(referer=url)
        )
    return result.content

#extracting JSON data from HTML
def get_json(company_code):

    result = company_url(company_code)
    if result is not None:
        soup = BeautifulSoup(result, 'html.parser')
        script = soup.find('script', text=re.compile('Performance = ({.*?});'))
        json_text = re.search(r'Performance = ({.*?});',script.string, flags=re.DOTALL |re.MULTILINE).group(1)
        data = json.loads(json_text)
        stock_data = data['data']
        

    return stock_data

#Write data to respective company files
def write_to_file(company_code, stock_data):
    # check if path to file exists
    if not os.path.exists(output_dir):
       os.makedirs(output_dir)

    #writing data to the output file
    with open(f'{output_dir}/{company_code}_stocks.csv', 'w') as file:
        # create the csv writer object
        csvwriter = csv.writer(file)

        stock_row = 0

        for stock in stock_data:
            if stock_row == 0:
                header = stock.keys()
        	    csvwriter.writerow(header)
        	    stock_row += 1

    	    csvwriter.writerow(stock.values())

#fetch the data
def get_data():
    for company_code in company_codes:
        stock_data = get_json(company_code)
        write_to_file(company_code, stock_data)

#putting it all together
if __name__== '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--company_code_path', help='Path to the file containing the list of companies to scrape, by default will use companies.txt in the same directory', default='companies.txt')
    parser.add_argument('--output_dir', help='Path to save the output files in', default='output_files/')

    args = parser.parse_args()

    output_dir = args.output_dir
    company_codes = setup(args.company_code_path)

    get_data()
