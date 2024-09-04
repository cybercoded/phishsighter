import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
from urllib.parse import urlparse
import whois


url = "http://google.com/"
domain = urlparse(url).netloc
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful
soup = BeautifulSoup(response.text, 'html.parser')
whois_response = whois.whois(domain)


def PageRank():
    try:
        prank_checker_response = requests.post("https://www.checkpagerank.net/index.php", {"name": domain})

        global_rank = int(re.findall(r"Global Rank: ([0-9]+)", prank_checker_response.text)[0])
        print(global_rank)
        if global_rank > 0 and global_rank < 100000:
            return 1
        return -1
    except:
        return -1

# Example usage assuming url and whois_response are defined
print(PageRank())

