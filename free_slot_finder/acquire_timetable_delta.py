#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 15:33:46 2017

@author: waffleboy
"""
#TODO: Refactor this and acquire modules json to one big module
import os
import logging
import shutil
import requests
import urllib.request
from bs4 import BeautifulSoup
from dateutil.parser import parse
from data_formatting_module import load_json
from acquire_modules_json import get_our_last_update,write_last_updated,write_to_json,year_generator

logger = logging.getLogger(__name__)
#
#def download_and_split_timetable_delta(filepath = "data/timetabledelta.json"):
#    get_or_update_timetable_delta(filepath)
#    result = split_to_different_modules('ModuleCode',\
#                                    "data/timetabledelta.json",\
#                                    "data/timetable_info")
#    if result:
#        logger.info("Successfully split")
#    logger.error("Could not split timetabledelta.json into component modules")
#    return
    
def download_and_format_timetable(timetable_filepath = "data/timetable.json",\
                                  storage_filepath = "data/timetable/"):
    update_timetable(timetable_filepath,storage_filepath)
    format_timetable(storage_filepath)
    logging.info("Successfully formatted timetabledelta")
    return
    
def update_timetable(timetable_filepath,storage_filepath,force=False):
    website_last_updated_time = get_website_last_updated_time("a",{"href":"1/"})
    if os.path.exists(timetable_filepath):
        our_last_update = get_our_last_update("data/last_timetable_update.txt")
        if our_last_update and (website_last_updated_time <  our_last_update):
            logging.info("No updates to timetabledeltaraw since last run - quitting.")
            return
    result = download_timetable_from_nusmods("timetable.json",storage_filepath)
    if result:
        logging.info("Successfully updated timetabledelta")
        write_last_updated(website_last_updated_time,"data/last_timetable_update.txt")
        return
    return 
    
#TODO: Fix possible overwriting of years after sem over
def download_timetable_from_nusmods(filename,storage_filepath = "data/timetable/"):
    if os.path.exists(storage_filepath):
        shutil.rmtree(storage_filepath)
    os.mkdir(storage_filepath)
    try:
        for i in range(1,3): #only sem 1 and 2
            link = "http://api.nusmods.com/{}/{}/{}".format(year_generator(),i,filename)
            folder_path = storage_filepath + '/' + str(i)
            os.mkdir(folder_path)
            download_file(link,folder_path + '/' + filename)
    except Exception as e:
        logger.error(e)
        return False
    return True
    
def download_file(url,file_name):
    urllib.request.urlretrieve(url, file_name)
    
    
def get_website_last_updated_time(elem_type,attrs):
    req = requests.get("http://api.nusmods.com/{}/".format(year_generator()))
    soup = BeautifulSoup(req.text,'html.parser')
    element = soup.find(elem_type,attrs)
    date_elem = element.next.next
    date_elem_stripped = date_elem.strip().rstrip().split()[:2]
    date = parse(' '.join(date_elem_stripped))
    return date

#TODO: Dont hardcode this
def format_timetable(filepath):
    #timetable filepaths
    timetables_path = [filepath+'{}/timetable.json'.format(i) for i in range(1,3)]
    # Load every timetable
    timetables = [load_json(x) for x in timetables_path]
    # For each timetable, reorganize it onto only the {code:timetable}
    master_dic = {}
    for i in range(len(timetables)):
        curr_timetable = timetables[i]
        dic = {}
        for j in range(len(curr_timetable)):
            entry = curr_timetable[j]
            if entry.get("Timetable"):
                dic[entry["ModuleCode"]] = entry["Timetable"]
                continue
            dic[entry["ModuleCode"]] = {}
        master_dic[i+1] = dic #offset for semester
    write_to_json(master_dic,filepath+'timetable_formatted.json')
    return
    
if __name__ == '__main__':
    download_and_format_timetable()