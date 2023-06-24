import common 
from datetime import datetime
import json
import html
import time
import concurrent.futures
from configparser import ConfigParser


config_object = ConfigParser()
config_object.read("config.ini")

#threadcounts
threadCounts = config_object['ThreadCounts']
eachResultsT_count = int(threadCounts['eachResult'])
eachYearT_count = int(threadCounts['eachYear'])

#Credentials
credentails = config_object['Credentials']
mongoUri = credentails['mongo']

#proxy
proxy = config_object['Proxy']
proxy = proxy['useProxy']
if proxy.lower() == 'false':
  proxy = False
else:
  proxy = True

proxyObj = common.ProxyServer(enableProxies=proxy)

headers = {
  'accept': 'application/json, text/plain, */*',
  'authority': 'www.oddsportal.com',
  'Accept-Language': 'en-US,en;q=0.5',
  'X-Requested-With': 'XMLHttpRequest',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36'
}


site = 'https://www.oddsportal.com'
yearArr = []

def makeRequest(url, referer=False):
  nHeders = headers.copy()
  if referer:
    nHeders['Referer'] = referer
  
  for i in range(5):
    try:
      print(f"Try No: {i+1} on url: {url}")
      r = proxyObj.get_request(url, nHeders)
      #print(r)
      if r.text == "Forbidden.":
        time.sleep(3)
        continue
      return r
    except Exception as ex:
      print(f"EX in request: {ex}, datetime: {datetime.now()}")
  #exit("NO DATA")
  
def eachYear(url, out=None):
  ye = url[1]
  url = url[0]
  global yearArr
  if url in yearArr:
    print("THIS YEAR ALREADY EXISTS")
    return False
  yearArr.append(url)
  data = {"yearURL":url, 'races':[], 'year':ye}
  try:
    if out is None:
      yearD = makeRequest(url)
      out = yearD.text
    
    idV = common.getValue('"id":"(.*?)"', out)
    if idV is not None:
      try:
        print("Id is: ", idV)
        jsonUrl = "https://www.oddsportal.com/ajax-sport-country-tournament-archive_/1/"+str(idV)+"/X0/1/0/?_="+str(round(datetime.now().timestamp()))
        jsonVal = makeRequest(jsonUrl, url)
        jsonDec = jsonVal.text
        if jsonDec != "Forbidden.":
          jsonDec = json.loads(jsonDec)
          allurls = []
          for one in jsonDec["d"]["rows"]:
            try:
              url = site + one['url']
              if url in allurls:
                continue
              allurls.append(url)
              '''
              print("Url:", url)
              print("Odds:", bets(url))
              print("Time:", one['date-start-base'])
              print("Home:", one['home-name'])
              print("Away:", one['away-name'])
              print("H Score:", one['homeResult'])
              print("A Score:", one['awayResult'])
              '''
              print("\n-------------------------------------------------------------------\n")
              data['races'].append({'raceURL':url, 'country':common.getValue('oddsportal.*?/.*?/(.*?)/', url), "league": common.getValue('oddsportal.*?/.*?/.*?/(.*?)/', url), 'game':common.getValue('oddsportal.*?/(.*?)/', url), 'Odds':bets(url), 'Time':one['date-start-base'], 'Home':one['home-name'], 'Away': one['away-name'], 'H Score':one['homeResult'], 'A Score':one['awayResult']})
              #break #testing
            except:
              pass
        else:
          print("Error: ", jsonDec)
      except Exception as ex:
        print(f"EX: {ex}, eachYear inside tryExcept")
        
      if collection.find_one({'yearURL':data['yearURL']}) == None:
        collection.insert_one(data)
        print("INSERTING INTO DB")
      else:
        collection.update_one({'yearURL':data['yearURL']}, {'$set':data})
        print("UPDATEING INTO DB")
    else:
      print("Id not found")  
  except Exception as ex:
    print(f"EX: {ex} in eachYear, url: {url}, datetime: {datetime.now()}")
  

def eachResults(url):
  try:
    league = makeRequest(url)
    yearsSelect = common.getValue('<select class="int-select(.*?)</select', league.text)
    if yearsSelect is not None:
      years = common.getValue('value="(.*?)".*?>\s*(\d+)\s*</op', league.text, "yes")
      if years is not None:
        with concurrent.futures.ThreadPoolExecutor(max_workers=eachYearT_count) as executor:
          for year in years:  
            if url == year:
              executor.submit(eachYear, year, league.text)
            else:
              executor.submit(eachYear, year)
            #break #testing
      else:
        print("Years not found")      
    else:
      print("Years Select not found")
  except Exception as ex:
    print(f"EX: {ex} in eachResult, url: {url}, datetime: {datetime.now()}")
  
def bets(url):
  newobj = {'1X2':{}, 'Over/Under':{}, 'Asian Handicap':{}, 'BTTS':{}}
  try:
    slug = [x for x in url.split('-') if x != ''][-1]
    slug = slug.replace('/', '')
    
    siteHtml = makeRequest(url)
    oddsId = html.unescape(common.getValue('<Event :data="(.*?)"', siteHtml.text)).replace('&nbsp;', ' ')
    cusUrl =  common.getValue('match-event./1-(\d+)-', oddsId)
    if cusUrl == None:
      cusUrl = 1
    oddsId = json.loads(oddsId)['eventBody']['providersNames']
    
    try:
      #1X2
      fulltime = getOdds(slug, oddsId, 2, 1, '1X2', url, cusUrl) 
      fHalf = getOdds(slug, oddsId, 3, 1, '1X2', url, cusUrl)
      sHalf = getOdds(slug, oddsId, 4, 1, '1X2', url, cusUrl)
      newobj['1X2'] = setData(oddsId, fulltime, fHalf, sHalf)
    except Exception as ex:
      print(f"EX: {ex} in 1X2, url: {url}, datetime: {datetime.now()}")

    try:
      #over/under
      fulltime = getOdds(slug, oddsId, 2, 2, 'over/under', url, cusUrl)
      fHalf = getOdds(slug, oddsId, 3, 2, 'over/under', url, cusUrl)
      sHalf = getOdds(slug, oddsId, 4, 2, 'over/under', url, cusUrl)
      newobj['Over/Under'] = setData(oddsId, fulltime, fHalf, sHalf, "yes")
    except Exception as ex:
      print(f"EX: {ex} in over/under, url: {url}, datetime: {datetime.now()}")

    try:
      #asianHandicap
      fulltime = getOdds(slug, oddsId, 2, 5, 'Asian Handicap', url, cusUrl)
      fHalf = getOdds(slug, oddsId, 3, 5, 'Asian Handicap', url, cusUrl)
      sHalf = getOdds(slug, oddsId, 4, 5, 'Asian Handicap', url, cusUrl)
      newobj['Asian Handicap'] = setData(oddsId, fulltime, fHalf, sHalf, "yes")
    except Exception as ex:
      print(f"EX: {ex} in asianHandicap, url: {url}, datetime: {datetime.now()}")
    
    try:
      #bothteamscore
      fulltime = getOdds(slug, oddsId, 2, 13, 'BTTS', url, cusUrl)
      fHalf = getOdds(slug, oddsId, 3, 13, 'BTTS', url, cusUrl)
      sHalf = getOdds(slug, oddsId, 4, 13, 'BTTS', url, cusUrl)
      newobj['BTTS'] = setData(oddsId, fulltime, fHalf, sHalf)
    except Exception as ex:
      print(f"EX: {ex} in bothteamscore, url: {url}, datetime: {datetime.now()}")

  except Exception as ex:
    print(f"EX: {ex}, FUNCTION: bets, URL: {url}, datetime: {datetime.now()}")
    
  return newobj
      
def getOdds(slug, oddsId, gTime, gType, dType, referer, cusUrl):
  try:
    link = f'https://www.oddsportal.com/feed/match-event/1-{cusUrl}-{slug}-{gType}-{gTime}-yja83.dat'
    oddsJson = makeRequest(link, referer)
    oddsJson = oddsJson.json()
      
    if dType in ['1X2', 'BTTS']:
      obj = {}
      oddsData = oddsJson['d']['oddsdata']['back'][f'E-{gType}-{gTime}-0-0-0']['odds']
      for key, value in oddsId.items():
        if key in oddsData:
          obj[value] = oddsData[key]
      return obj
      
    if dType in ['Asian Handicap', 'over/under']:
      obj = {}
      for x in ['0.5', '1.5', '2.5', '3.5']:
        obj[x] = {}
        if f'E-{gType}-{gTime}-0-{x}-0' in oddsJson['d']['oddsdata']['back']:
          oddsData = oddsJson['d']['oddsdata']['back'][f'E-{gType}-{gTime}-0-{x}-0']['odds']
          for key, value in oddsId.items():
            if key in oddsData:
              obj[x][value] = oddsData[key]
      return obj
  except Exception as ex:
    print(f"EX: {ex}, FUNCTION: getOdds, datetime: {datetime.now()}")
  return {}
  
def setData(oddsId, fulltime, fHalf, sHalf, objC='No'):
  obj = {}
  try:
    for key in list(oddsId.values()):
      obj[key] = {'fulltime': {}, 'firstHalf': {}, 'secondHalf': {}}
      if objC == "yes":
        for x in ['0.5', '1.5', '2.5', '3.5']:
          if key in fulltime[x]:
            obj[key]['fulltime'][x] = fulltime[x][key]
          if key in fHalf[x]:
            obj[key]['firstHalf'][x] = fHalf[x][key]
          if key in sHalf[x]:
            obj[key]['secondHalf'][x] = sHalf[x][key]
      else:
        if key in fulltime:
          obj[key]['fulltime'] = fulltime[key]
        if key in fHalf:
          obj[key]['firstHalf'] = fHalf[key]
        if key in sHalf:
          obj[key]['secondHalf'] = sHalf[key]
  except Exception as ex:
    print(f"EX: {ex}, FUNCTION: setData, datetime: {datetime.now()}")
  return obj
      
def start(db):
  global collection
  collection = db.ODDS
  results = makeRequest("https://www.oddsportal.com/football/results/")
  links = common.getValue('<li class="flex items-center.*?href="(.*?)"', results.text, "yes")
  print("Total links found: ", len(links))

  #executor1 = concurrent.futures.ThreadPoolExecutor(max_workers=eachResultsT_count)
  with concurrent.futures.ThreadPoolExecutor(max_workers=eachResultsT_count) as executor:
    for one in links:
      print("Scrap match: ", one)
      validate = common.getValue('^/football/(\w+.*?)$', one)
      if validate is not None:
        executor.submit(eachResults, site + str(one))
      else:
        print("Invalid match link", one)
      #break #testing
      
if __name__ == '__main__':
  db = common.get_mongoDb(mongoUri)
  start(db)
#  k = bets('https://www.oddsportal.com/football/bolivia/division-profesional/vaca-diez-aurora-KWLo4Rge/')
#  print(k)

  
      
