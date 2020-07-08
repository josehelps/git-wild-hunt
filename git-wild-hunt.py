#!/usr/bin/python

import argparse
import requests
import json
import re
import os
import sys
import datetime
from pathlib import Path
from modules.CustomConfigParser import CustomConfigParser
from modules import logger

VERSION = 1

def load_regexes(regexes_path):
    reg = dict()
    with open(os.path.join(os.path.dirname(__file__), regexes_path), 'r') as f:
        regexes = json.loads(f.read())

    return regexes

def search_github(github_token, search):
    results = []
    h = {"Authorization":"token "+ github_token}
    url = "https://api.github.com/search/code?per_page=100&q=" + search
    #extension:yml+path:.circleci+filename:config+language:YAML
    r = requests.get( url, headers=h, timeout=30)
    result = r.json()
    if result['total_count'] > 0
        log.info("total results: {}".format(result['total_count']))
    else:
        log.error("no results found for the search: {}".format(search))
        sys.exit(1)
    
    # first check for rate limit
    if 'documentation_url' in result:
        if result['documentation_url'] == "https://developer.github.com/v3/#abuse-rate-limits":
            r = requests.get('https://api.github.com/rate_limit', headers=h, timeout=30)
            log.error("we have hit githubs rate limit, cool off, return on: {}..exiting".format(r.headers.get('X-RateLimit-Reset')))
            sys.exit(1)

    if 'items' in result:
        for i in result['items']:
            results.append(i)

    # check if there is pagination
    link = r.headers.get('link')
    if link is None:
        log.info("all done processing results")
        return result
    next_url = find_next(r.headers['link'])
    # process pagination of results
    if next_url is None:
        log.info("all done processing results")
        return results
    else:
        results = process_pages(github_token, next_url, results)
        log.info("all done processing results")
        return results

def process_pages(github_token, url, results):
    log.info("processing page: {0}".format(url[-1]))
    # limiting for testing
    if int(url[-1]) >= 4:
        return results

    h = {"Authorization":"token "+ github_token}
    r = requests.get( url, headers=h, timeout=30)
    result = r.json()
    
    # first check for rate limit
    if 'documentation_url' in result:
        if result['documentation_url'] == "https://developer.github.com/v3/#abuse-rate-limits":
            log.error("we have git githubs rate limit, cool off, return on: {} ..exiting".format(r.headers.get('X-RateLimit-Reset')))
            sys.exit(1)
    # process results if we haven't hit any
    if 'items' in result:
        for i in result['items']:
            results.append(i)

    # check if there is pagination
    link = r.headers.get('link')
    if link is None:
        return result
    next_url = find_next(r.headers['link'])
    # process pagination of results
    if next_url is None:
        log.info("all done processing results")
        return results
    return process_pages(github_token, next_url, results)
        


# given a link header from github, find the link for the next url which they use for pagination
def find_next(link):
    for l in link.split(','):
        a, b = l.split(';')
        if b.strip() == 'rel="next"':
            return a.strip()[1:-1]

def rawurl( result ):
    if 'html_url' in result:
        raw_url = result['html_url'];
        raw_url = raw_url.replace( 'https://github.com/', 'https://raw.githubusercontent.com/' )
        raw_url = raw_url.replace( '/blob/', '/' )
        return raw_url
    else:
        raw_url = None
        return raw_url

def getcode( url ):
    # print( url )
    try:
        r = requests.get( url, timeout=10 )
        return r.text
    except: 
        log.error("timeout requesting url: {0} .. continuing".format(url))
        code = None
        return code 

def findleaks(conf, regexes):
    match_creds = []
    match_details = dict()
    url = rawurl(conf)
    if url:
        code = getcode(url)
    else:
        log.error("could not get raw content for {}".format(json.dumps(conf, indent=2)))
        code = None
    if code:
        for check, regex in regexes.items():
            matches = re.findall(regex, code)
            if matches:
                match_details['url'] = url
                match_details['check'] = check
                match_details['matches']  = matches
                match_details['timestamp']  = str(datetime.datetime.utcnow().isoformat())
                match_creds.append(match_details)
                log.warning("url: {0}\ncheck: {1} matches: {2}".format(url, check, matches))
    return match_creds

def write_leaks(leaks, output_path):
    try:
        with open(output_path, 'a') as outfile:
            json.dump(leaks, outfile)
    except Exection as e:
        log.error("writing result file: {0}".format(str(e)))

if __name__ == "__main__":
    # grab oarguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", required=True, default="", help="search to execute")
    parser.add_argument("-c", "--config", required=False, default="git-wild-hunt.conf", help="config file path")
    parser.add_argument("-v", "--version", default=False, action="store_true", required=False,
                        help="shows current git-wild-hunt version")

    # parse them
    args = parser.parse_args()
    ARG_VERSION = args.version
    config = args.config
    search = args.search
    
    # needs config parser here
    tool_config = Path(config)
    if tool_config.is_file():
        print("git-wild-hunt is using config at path {0}".format(tool_config))
        configpath = str(tool_config)
    else:
        print("ERROR: git-wild-hunt failed to find a config file at {0} or {1}..exiting".format(tool_config))
        sys.exit(1)

    # Parse config
    parser = CustomConfigParser()
    config = parser.load_conf(configpath)

    log = logger.setup_logging(config['log_path'], config['log_level']
)
    log.info("INIT - git-wild-hunt v" + str(VERSION))

    if ARG_VERSION:
        log.info("version: {0}".format(VERSION))
        sys.exit(0)

    regexes = load_regexes(config['regexes'])

    github_token = config['github_token']

    if github_token == "TOKENHERE":
        print("ERROR: git-wild-hunt failed to find a github_token in the config file at {0}..exiting".format(tool_config))
        sys.exit(1)
    else:
        s = search.replace(" ", "+")
        results = search_github(github_token, s)
    
    # lets process the search results
    count = 0 
    all_leaks = []
    for conf in results:
        count += 1
        if 'html_url' in conf:
            log.info("processing potential leak #{0} on {1}".format(count, conf['html_url']))
            leaks = findleaks(conf, regexes)
        else:
            continue
        for l in leaks:
            all_leaks.append(l)

    # write output of all leaks
    write_leaks(all_leaks, config['output'])
        






