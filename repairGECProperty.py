#!/usr/bin/python
# -*- coding: utf-8 -*-

import requests
import pywikibot
from pywikibot import pagegenerators as pg
import functools

QUERY = 'SELECT DISTINCT ?item WHERE { ?item wdt:P1296 ?link. MINUS {?item wdt:P12385 ?value.} } ORDER BY ASC(?item)'
PATTERN = 'https://www.enciclopedia.cat/ec-gec-{0}.xml'
NEW_GEC_PATTERN = 'https://www.enciclopedia.cat/gran-enciclopedia-catalana/'
FORMER_GEC_PROPERTY = 'P1296'
NEW_GEC_PROPERTY = 'P12385'

try:
	ferror = open('errorGECValues.txt', 'a+', encoding='utf8')
except (OSError, IOError) as e:
    print('Problemes per obrir l\'arxiu')
    sys.exit(0)

def set_obsolet_rank(elem):
	print('Rank: {0}'.format(elem.getRank()))
	if(elem.getRank() != 'obsolete'):
		elem.changeRank('obsolete')
		#TODO: Afegir MOTIU
	else:
		print('Element ja obsolet.')

def repair_wikidata_element(item, new_uri):
	new_gec_value = new_uri.replace(NEW_GEC_PATTERN, "")
	print('Nou valor GEC: {0}'.format(new_gec_value))
	claim = pywikibot.page.Claim(repo, NEW_GEC_PROPERTY, datatype=u'string')
	claim.setTarget(new_gec_value)
	item.addClaim(claim)

def write_error(item, gec_value):
	print("Enllaç trencat: {0}{1}".format(item, gec_value))
	ferror.write(u'{0}:{1}'.format(item, gec_value))

def check_URI(uri):
	r = requests.get(uri)
	if r.status_code == 200 and uri != r.url and len(r.history) == 1 and r.history[0].url == uri:
		return r.url, 301
	elif r.status_code == 404:
		print('404: No s\'ha trobat l\'article')
		return None, 404
	return None, r.status_code

def process_claim(item, elem):
	gec_value = elem.getTarget()

	if NEW_GEC_PROPERTY not in item.claims:
		if gec_value.isnumeric():	
			uri = PATTERN.format(gec_value) 
		else:
			uri = NEW_GEC_PATTERN+gec_value
		print(uri)
		new_uri, status_code = check_URI(uri)
		print(status_code)
		print(new_uri)
		if status_code == 301:
			repair_wikidata_element(item, new_uri)
			#set_obsolet_old_elem(elem)
		elif status_code == 404:
			write_error(item, gec_value)

def main():
	global repo

	wd_site = pywikibot.Site("wikidata", "wikidata")
	gen = pg.WikidataSPARQLPageGenerator(QUERY, site=wd_site)
	repo = wd_site.data_repository()

	num = 0
	for item in gen:
		item_dict = item.get()
		#title = item_dict[u'labels'][u'ca']
		print('Num: {0}, item {1}, Title: '.format(num, item))
		for elem in item.claims[FORMER_GEC_PROPERTY]:
			process_claim(item, elem)
		num += 1


if __name__ == '__main__':
	main()