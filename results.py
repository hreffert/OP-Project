import common 


proxyObj = common.ProxyServer()


def eachResults(url):
  exit()


eachResults("https://www.oddsportal.com/football/africa/africa-cup-of-nations/results/")
exit()

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
    
