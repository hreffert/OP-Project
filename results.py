import common 
from datetime import datetime
import json

proxyObj = common.ProxyServer()


def eachYear(url, out=None):
  if out is None:
    yearD = proxyObj.get_request(url)
    out = yearD.text
  
  idV = common.getValue('"id":"(.*?)"', out)
  if idV is not None:
    print("Id is: ", idV)
    jsonUrl = "https://www.oddsportal.com/ajax-sport-country-tournament-archive_/1/"+str(idV)+"/X0/1/0/?_="+str(round(datetime.now().timestamp()))
    jsonVal = proxyObj.get_request(jsonUrl)
    jsonDec = jsonVal.text
    if jsonDec != "Forbidden.":
      jsonDec = json.loads(jsonDec)
      for one in jsonDec["d"]["rows"]:
        print("Time:", one['date-start-base'])
        print("Home:", one['home-name'])
        print("Away:", one['away-name'])
        print("H Score:", one['homeResult'])
        print("A Score:", one['awayResult'])
        print("\n-------------------------------------------------------------------\n")
    else:
      print("Error: ", jsonDec)
  else:
    print("Id not found")  

def eachResults(url):
  league = proxyObj.get_request(url)
  yearsSelect = common.getValue('<select class="int-select(.*?)</select', league.text)
  if yearsSelect is not None:
    years =   common.getValue('value="(.*?)"', league.text, "yes")
    if years is not None:
      for year in years:
        if url == year:
          eachYear(year, league.text)
        else:
          eachYear(year)
    else:
      print("Years not found")      
  else:
    print("Years Select not found")

#eachResults("https://www.oddsportal.com/football/albania/albanian-cup/results/")
#eachYear("https://www.oddsportal.com/football/africa/africa-cup-of-nations/results/")
#exit()

results = proxyObj.get_request("https://www.oddsportal.com/football/results/")
links = common.getValue('<li class="flex items-center.*?href="(.*?)"', results.text, "yes")
print("Total links found: ", len(links))


for one in links:
  print("Scrap match: ", one)
  validate = common.getValue('^/football/(\w+.*?)$', one)
  if validate is not None:
    eachResults("https://www.oddsportal.com"+str(one))
  else:
    print("Invalid match link", one)
    
