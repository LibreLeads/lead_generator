import os 
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
API_KEY = os.getenv("RAPID_API")
def get_rental_market(search_query, bedroom_type, home_type):
    url = "https://zillow-working-api.p.rapidapi.com/rental_market"
    querystring = {"search_query":search_query,"bedrooom_type":bedroom_type,"home_type":home_type}
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "zillow-working-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

def get_ownerinfo(byzpid, byurl, byaddress):
    url = "https://zillow-working-api.p.rapidapi.com/ownerinfo"
    querystring = {"byzpid":byzpid,"byurl":byurl,"byaddress":byaddress}
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "zillow-working-api.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers, params=querystring)
    return response.json()

def main():
    rental_market = get_rental_market("Austin, TX", "All_Bedrooms", "All_Property_Types")
    ownerinfo = get_ownerinfo("2095970110", "https://www.zillow.com/homedetails/700-Bergenline-Ave-APT-6-Union-City-NJ-07087/2095970110_zpid/", "712 6th St APT 1R, Union City, NJ 07087")
    print(rental_market)
    print(ownerinfo)

main()