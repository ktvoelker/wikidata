#!/usr/bin/env python3

import csv
import requests

URL = 'http://www.wikidata.org/w/api.php'

PARAMS = {
    'action': 'query',
    'list': 'backlinks',
    'bltitle': 'Property:P298',
    'bllimit': '50'
}

def get(params):
    params = params.copy()
    params['format'] = 'json'
    result = requests.get(URL, params=params)
    result.raise_for_status()
    return result.json()

def get_entities():
    def add_params(d):
        result = PARAMS.copy()
        for k in d:
            result[k] = d[k]
        return result
    result = get(add_params({'continue': ''}))
    for x in result['query']['backlinks']:
        yield x['title']
    while 'continue' in result:
        result = get(add_params(result['continue']))
        for x in result['query']['backlinks']:
            yield x['title']

def get_code(e):
    result = get({
        'action': 'wbgetclaims',
        'entity': e,
        'property': 'P298'
    })
    if 'claims' in result:
        result = result['claims']
    else:
        return None
    if 'P298' in result:
        result = result['P298']
    else:
        return None
    if len(result) > 0:
        return result[0]['mainsnak']['datavalue']['value']
    else:
        return None

def get_label(e):
    result = get({
        'action': 'wbgetentities',
        'ids': e,
        'props': 'labels',
        'languages': 'en'
    })
    if 'entities' in result:
        result = result['entities']
    else:
        return None
    if e in result:
        return result[e]['labels']['en']['value']
    else:
        return None

def get_code_mapping():
    for e in get_entities():
        code = get_code(e)
        if code is None:
            continue
        label = get_label(e)
        if label is None:
            continue
        yield (code, label)

with open('iso-3166-1-alpha-3.csv', 'w') as csvfile:
    writer = csv.writer(
            csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for p in get_code_mapping():
        writer.writerow(p)

