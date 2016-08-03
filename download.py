from bs4 import BeautifulSoup
from urllib.request import urlopen
from pandas import DataFrame
import os
import pickle
import logging

log = logging.getLogger(__name__)

default_url = "http://www.baseball-reference.com/players/gl.cgi?id=murphda08&t=b&year=2016"

def get_gamelog(source_url=default_url):
    with urlopen(source_url) as webobj:
        soup = BeautifulSoup(webobj.read(), 'lxml')
        batting_log = soup.find(id="batting_gamelogs")
        headers = [ elem.text for elem in batting_log.find('thead').findAll('th') ]
        rows = batting_log.findAll('tr')
        return DataFrame([[elem.text for elem in row.findAll('td')] for row in rows],
            columns=headers).dropna()

def get_gamelog_cached(force=False, source_url=default_url, cache_file="cache.pickle"):
    if force:
        log.info("Forcing gamelog rebuild.")
    elif os.path.exists(cache_file):
        try:
            with open(cache_file, 'rb') as fobj:
                return pickle.load(fobj)
        except:
            log.error("Cache file load failed. Rebuilding.")

    gamedata = get_gamelog()
    with open(cache_file, 'wb') as fobj:
        pickle.dump(gamedata, fobj)
    return gamedata

if __name__ == "__main__":
    gamedata = get_gamelog_cached()
    print(gamedata)