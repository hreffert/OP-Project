import common 
from datetime import datetime
import json
import html
import time

proxyObj = common.ProxyServer()
site = 'https://www.oddsportal.com'

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
  
def bets(url):
  slug = [x for x in url.split('-') if x != ''][-1]
  slug = slug.replace('/', '')
  
  proxyObj.user_agent['Referer'] = url
  proxyObj.user_agent['accept'] = 'application/json, text/plain, */*'
  proxyObj.user_agent['authority'] = 'www.oddsportal.com'
  proxyObj.user_agent['Accept-Language'] = 'en-US,en;q=0.5'
  proxyObj.user_agent['X-Requested-With'] = 'XMLHttpRequest'
  #proxyObj.user_agent['authority'] = 'www.oddsportal.com'
  siteHtml = proxyObj.get_request(url)
  oddsId = html.unescape(common.getValue('<Event :data="(.*?)"', siteHtml.text)).replace('&nbsp;', ' ')
  oddsId = json.loads(oddsId)['eventBody']['providersNames']
  
  newobj = {'1X2':{}, 'Over/Under':{}, 'Asian Handicap':{}, 'BTTS':{}}
  
  #1X2
  fulltime = getOdds(slug, oddsId, 2, 1, '1X2') 
  fHalf = getOdds(slug, oddsId, 3, 1, '1X2')
  sHalf = getOdds(slug, oddsId, 4, 1, '1X2')
  newobj['1X2'] = setData(oddsId, fulltime, fHalf, sHalf)

  #over/under
  fulltime = getOdds(slug, oddsId, 2, 2, 'over/under')
  fHalf = getOdds(slug, oddsId, 3, 2, 'over/under')
  sHalf = getOdds(slug, oddsId, 4, 2, 'over/under')
  newobj['Over/Under'] = setData(oddsId, fulltime, fHalf, sHalf, "yes")

  #asianHandicap
  fulltime = getOdds(slug, oddsId, 2, 5, 'Asian Handicap')
  fHalf = getOdds(slug, oddsId, 3, 5, 'Asian Handicap')
  sHalf = getOdds(slug, oddsId, 4, 5, 'Asian Handicap')
  newobj['Asian Handicap'] = setData(oddsId, fulltime, fHalf, sHalf, "yes")
  
  #bothteamscore
  fulltime = getOdds(slug, oddsId, 2, 13, 'BTTS')
  fHalf = getOdds(slug, oddsId, 3, 13, 'BTTS')
  sHalf = getOdds(slug, oddsId, 4, 13, 'BTTS')
  newobj['BTTS'] = setData(oddsId, fulltime, fHalf, sHalf)

  return newobj
      
def getOdds(slug, oddsId, gTime, gType, dType):
  #print("KAKAKAK", slug, oddsId, gTime, gType)
  link = f'https://www.oddsportal.com/feed/match-event/1-1-{slug}-{gType}-{gTime}-yja83.dat'
  for _ in range(5):
    try:
      oddsJson = proxyObj.get_request(link)
      if 'Forbidden.' in oddsJson.text:
        exit('Forbidden.')
      oddsJson = oddsJson.json()
      break
    except Exception as ex:
      print(ex)
      time.sleep(5)
      pass
  
  
  
  if dType in ['1X2', 'BTTS']:
    obj = {}
    oddsData = oddsJson['d']['oddsdata']['back'][f'E-{gType}-{gTime}-0-0-0']['odds']
    for key, value in oddsId.items():
      if key in oddsData:
        obj[value] = oddsData[key]
    return obj
    
  if dType in ['Asian Handicap', 'over/under']:
    obj = {}
    for x in ['0.5', 1.5, 2.5, 3.5]:
      obj[x] = {}
      if f'E-{gType}-{gTime}-0-{x}-0' in oddsJson['d']['oddsdata']['back']:
        oddsData = oddsJson['d']['oddsdata']['back'][f'E-{gType}-{gTime}-0-{x}-0']['odds']
        for key, value in oddsId.items():
          if key in oddsData:
            obj[x][value] = oddsData[key]
    return obj
  
  
def setData(oddsId, fulltime, fHalf, sHalf, objC='No'):
  obj = {}
  for key in list(oddsId.values()):
    obj[key] = {'fulltime': {}, 'firstHalf': {}, 'secondHalf': {}}
    if objC == "yes":
      for x in ['0.5', 1.5, 2.5, 3.5]:
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
  return obj
      
  
#eachResults("https://www.oddsportal.com/football/albania/albanian-cup/results/")
#eachYear("https://www.oddsportal.com/football/africa/africa-cup-of-nations/results/")
a = bets('https://www.oddsportal.com/football/africa/africa-cup-of-nations/rwanda-benin-AXWn6ma0/')
print(a)
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
    
