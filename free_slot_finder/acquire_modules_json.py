#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 23:08:11 2017

@author: waffleboy
"""
import wget
import os
import logging
import datetime
import shutil
import requests
import json
from bs4 import BeautifulSoup
from dateutil.parser import parse
from data_formatting_module import load_json
from multiprocessing import Pool
from multiprocessing import cpu_count

logger = logging.getLogger(__name__)
#==============================================================================
#                   modules.json updating Module
#==============================================================================

## Main
def download_and_split_modules_json(filename = "data/modules.json",force=False):
    download_modules_json(filename,force)
    result = split_to_different_modules(additional_key = 'ModuleCode')
    if result:
        logger.info("Successfully split")
    logger.error("Could not split modules.json into component modules")
    
def download_modules_json(filename = "data/modules.json",force=False):
    logger.info("Attempting to download modules.json")
    if not os.path.exists("data"):
        os.mkdir("data")
    modules_json_URL = "http://api.nusmods.com/{}/modules.json".format(year_generator())
    website_last_updated = get_nusmods_last_updated_time()
    if os.path.exists(filename) and force == False:
        our_last_update = get_our_last_update()
        if our_last_update and (website_last_updated <= our_last_update):
            logger.info("Nothing new to update. Stopping..")
            return
    wget.download(modules_json_URL,out=filename)
    logger.info("Downloaded modules.json")
    write_last_updated(website_last_updated)
    return

def year_generator():
    curr_date = datetime.date.today()
    year = curr_date.year
    if curr_date.month >= 7: #set july as start of next acad year
        return '{}-{}'.format(year,year+1)
    return '{}-{}'.format(year-1,year)

# TODO: Check individual modules for updates instead of mass wiping everything
def split_to_different_modules(additional_key,modules_json_filepath="data/modules.json",\
                               indiv_modules_filepath = "data/modules"):
    if os.path.exists(indiv_modules_filepath):
        shutil.rmtree(indiv_modules_filepath)
    os.mkdir(indiv_modules_filepath)
    
    modules = load_json(modules_json_filepath)
    if modules:
        result = write_all_modules_to_disk(modules,indiv_modules_filepath,additional_key)
        return result
    logger.error("Could not load json for split_to_different_modules")
    return
    
def write_all_modules_to_disk(data,filepath,additional_key):
    try:
        formatted_data = format_for_pooling(data,filepath,additional_key)
        pool = Pool(cpu_count() * 2)
        pool.map(map_write_to_json,formatted_data)
        pool.close()
    except Exception as e:
        logger.error("Fail to write data to disk. Modules may not be updated")
        logger.error("Error: {}".format(e))
        return False
    return True
    
def format_for_pooling(data,filepath,additional_key):
    for entry in data:
        entry["filepath"] = filepath
        entry["additional_key"] = additional_key
    return data
    
def get_nusmods_last_updated_time():
    logger.info("Getting last updated time for modules json")
    web = requests.get("http://api.nusmods.com/{}".format(year_generator()))
    html = BeautifulSoup(web.text,'html.parser')
    modules_json_elem = html.find('a',attrs = {'href':'modules.json'})
    date_part = modules_json_elem.next.next.strip().rstrip()
    real_date = date_part.split()[:2]
    real_date = ' '.join(real_date)
    real_date = parse(real_date)
    return real_date
    
## TODO: Convert to datebase way instead
def get_our_last_update(filepath = "data/modules_last_updated.txt"):
    if not os.path.exists(filepath):
        logger.info("No last update file detected")
        return
    with open(filepath,'r') as f:
        data = f.read()
    date = parse(data)
    return date
    
# TODO: Find a better way of writing this while not breaking multiprocess
def map_write_to_json(data):
    try:
        filepath = data["filepath"]
        additional_key = data.get("additional_key")
        if additional_key:
            del data["additional_key"]
            filepath += '/' + data[additional_key] + '.json'
        del data["filepath"]
        with open(filepath, 'w') as outfile:
            json.dump(data, outfile)
    except:
        logging.error("Unable to write for {}".format(data))

def write_to_json(data,filepath):
    try:
        with open(filepath, 'w') as outfile:
                json.dump(data, outfile)
        return True
    except:
        logger.error("Could not save for {} and filepath {}".format(data,filepath))
        return False
    
def write_last_updated(data,filepath = "data/modules_last_updated.txt"):
    data = str(data)
    with open(filepath,'w') as f:
        f.write(data)

if __name__ == '__main__':
    download_and_split_modules_json()