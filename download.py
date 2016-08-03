import os
import logging
from bs4 import BeautifulSoup
from urllib.request import urlopen
from pandas import DataFrame, read_csv

log = logging.getLogger(__name__)

default_url = "http://www.baseball-reference.com/players/gl.cgi?id=murphda08&t=b&year=2016"

def get_gamelog(url=default_url):
    with urlopen(url) as webobj:
        soup = BeautifulSoup(webobj.read(), 'lxml')
        batting_log = soup.find(id="batting_gamelogs")
        headers = [ elem.text for elem in batting_log.find('thead').findAll('th') ]
        rows = batting_log.findAll('tr')
        return DataFrame([[elem.text for elem in row.findAll('td')] for row in rows],
            columns=headers).dropna().convert_objects(convert_numeric=True)

def get_gamelog_cached(force=False, url=default_url, cache_file="cache.csv"):
    if force:
        log.info("Forcing gamelog rebuild.")
    elif os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as fobj:
                return read_csv(fobj)
        except:
            log.error("Cache file load failed. Rebuilding.")

    gamedata = get_gamelog(url)
    with open(cache_file, 'w') as fobj:
        gamedata.to_csv(fobj)
    return gamedata

if __name__ == "__main__":
    gamedata = get_gamelog_cached()
    print(gamedata)