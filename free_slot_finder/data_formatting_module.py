#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 19 23:15:58 2017

@author: waffleboy
"""
import json
import os
import logging
import calendar

logger = logging.getLogger(__name__)
#=======================================================================================
# Convert input from a variety of different sources into timetable understandable format
#=======================================================================================

#TODO: Adapt for given year and stuff
def nusmods_adapter(url):
    sem = get_sem_from_url(url)
    if not sem:
        ## Handle invalid url
        return
    url_dict_stripped = parse_nusmods_link(url)
    lst = get_details_for_selected_mods(url_dict_stripped,sem)
    formatted_lst = format_for_timetable_ds(lst)
    return formatted_lst

def parse_nusmods_link(url):
    try:
        url = url[url.find('?')+1:].split('&')
        url_dict = {modtitle:group for modtitle,group in [x.split('=') for x in url]}
        # Convert to {mod_code: {classno:3, type:lec}}
        url_dict_stripped = []
        for module_and_type in url_dict:
            bracket_idx = module_and_type.find('[')
            if bracket_idx != -1:
                module_code = module_and_type[:bracket_idx]
                url_dict_stripped.append({module_code:{"type":module_and_type[bracket_idx+1:-1],"ClassNo":url_dict[module_and_type]}})
            else:
                module_code = module_and_type
                url_dict_stripped.append({module_code:{"type":'',"ClassNo":url_dict[module_and_type]}})
         # sweet one liner disabled because breaks if no [       
        #url_dict_stripped = {k[:k.find('[')]:{"type":k[k.find('[')+1:-1],"ClassNo":v} for k,v in url_dict.items()}
    except Exception as e:
        logger.error("Unable to parse {}. URL may not be a valid url".format(url))
        return False
    return url_dict_stripped
    
def get_details_for_selected_mods(url_dict_stripped,sem,master_dic_filepath = "data/timetable_formatted.json"):
    master_dic = load_json(master_dic_filepath)
    lst = []
    for module_component in url_dict_stripped:
        for module_code in module_component: #only one module code. Leaving it like this because it works
            class_no = module_component[module_code]['ClassNo']
            lesson_type = convert_lessontype_to_json_version(module_component[module_code]['type'])
            # Find correct lesson type and class
            mod_details = master_dic[str(sem)][module_code]
            if mod_details == {}:
                logger.warn("WARNING: Module details empty for module: {}. This could be normal if its an honours project".format(module_code))
                continue
            for entry in mod_details:
                if entry["ClassNo"] == class_no and entry['LessonType'].lower() == lesson_type:
                    lst.append(entry)
    return lst
    
def format_for_timetable_ds(lst):
    selected_entries = [{'day':convert_day_to_int(x["DayText"]),'start_time':x["StartTime"],"end_time":x["EndTime"]} for x in lst]
    #TODO: Extract the other information into "other_details"
    return selected_entries
        
    
def get_sem_from_url(url):
    try:
        return int(url[url.find("sem")+3])
    except:
        logger.error("Invalid link given for url {}".format(url))
        return
#==============================================================================
#                                 Helpers
#==============================================================================

def convert_day_to_int(day):
        return list(calendar.day_name).index(day) + 1
        
    
def convert_lessontype_to_json_version(typ):
    if typ:
        convert = {"LEC":"lecture","TUT":"tutorial","SEC":"sectional teaching",
                   "LAB":"laboratory"}
        return convert[typ]
    return
    
def load_data_for_individual_modules(module_code,sem,filepath = "data/timetable_formatted.json"):
    module = load_json(filepath)
    if module:
        return module[sem][module_code]
    logger.error("Module {} for filepath {} does not exist".format(module_code,filepath))
        
        
def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath) as json_data:
            return json.load(json_data)
    logger.error("Loading JSON data for filepath {} not found".format(filepath))
    return False