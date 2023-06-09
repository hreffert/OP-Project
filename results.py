import common 


proxyObj = common.ProxyServer()


def eachYear(url):
  print(url)

def eachResults(url):
  league = proxyObj.get_request(url)
  yearsSelect = common.getValue('<select class="int-select(.*?)</select', league.text)
  if yearsSelect is not None:
    years =   common.getValue('value="(.*?)"', league.text, "yes")
    if years is not None:
      for year in years:
        if url != year:
          eachYear(year, league.text)
        else:
          eachYear(year)
    else:
      print("Years not found")      
  else:
    print("Years Select not found")

#eachResults("https://www.oddsportal.com/football/albania/albanian-cup/results/")
#eachYear("https://www.oddsportal.com/football/albania/albanian-cup-2021-2022/results/")
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
    
