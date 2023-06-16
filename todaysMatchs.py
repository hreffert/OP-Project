from results import makeRequest, bets
from datetime import datetime
import json
import html
import time
import concurrent.futures
from configparser import ConfigParser
from common import getValue

config_object = ConfigParser()
config_object.read("config.ini")


site = 'https://www.oddsportal.com'

games = ['football', 'basketball', 'baseball', 'hockey', 'tennis', 'american-football', 'aussie-rules', 'badminton', 'beach-soccer', 'beach-volleyball', 'boxing', 'cricket', 'darts', 'esports', 'futsal', 'mma', 'pesapallo', 'rugby-league', 'rugby-union', 'table-tennis', 'volleyball', 'water-polo']
  
#m = f"{site}/feed/match-event/1-2-pYBByukP-3-2-yjd8d.dat?_={round(datetime.now().timestamp())}"
#print(makeRequest(m, "https://www.oddsportal.com/tennis/usa/itf-w60-sumter-sc-women/mateas-maria-urhobo-akasha-pYBByukP").text)
#print(bets('https://www.oddsportal.com/basketball/brazil/lbf-women/santo-andre-vera-cruz-campinas-fB7NJwds/'))
#exit()


def scrap(game):
  print("SCRAPING FROM:", game)
  r = makeRequest(f'https://www.oddsportal.com/matches/{game}')
  htmlData = r.text
  ajax = getValue('<next-matches-wrapper :data-next="(.*?)">', htmlData)
  if ajax == None:
    return False
  urlRe = getValue('/(\d+)./"\s*,\s*"hash"\s*:\s*"(.*?)"', html.unescape(ajax))
  url = f"https://www.oddsportal.com/ajax-nextgames/{urlRe[0]}/5.5/1/{datetime.today().strftime('%Y%m%d')}/yjfd0.dat?_={round(datetime.now().timestamp())}"
  data = makeRequest(url, 'https://www.oddsportal.com/matches/tennis').json()
  slugs = [site + x['url'] for x in data['d']['rows']]

  ''' #testing
  for x in slugs:
    print(bets(x))
    break #testing
  ''' #live
  with concurrent.futures.ThreadPoolExecutor() as executor:
    future_to_url = {executor.submit(bets, x): x for x in slugs}
    for future in concurrent.futures.as_completed(future_to_url):
      try:
        print(future.result())
      except Exception as ex:
        print("EX:", ex)
  #'''
if __name__ == "__main__":
  with concurrent.futures.ThreadPoolExecutor() as executor:
    executor.map(scrap, games)
