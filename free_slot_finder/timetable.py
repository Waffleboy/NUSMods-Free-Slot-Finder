#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 23:35:41 2017

@author: waffleboy
"""
import logging
import calendar
import datetime

logger = logging.getLogger(__name__)

class TimeTable():
    def __init__(self,day_range = (1,8),hour_range = 24,minute_range = 60):
        self.day_range = day_range
        self.hour_range = hour_range
        self.minute_range = minute_range
        self.occupied_indices = []
        self.timetable = self.initialize_timetable()
        return
    
    # Fit new data of slots to block your timetable.
    # Input: <List> input_data: List of {begin_time,end_time,day_num} where day_num: Monday = 1, Sunday = 7
    def fit_new_timetable(self,input_data):
        logging.info("Fitting new timetable with input data {}".format(input_data))
        for entry in input_data:
            other_details = entry.get("other_details") or {}
            self.fit_timetable_slot(entry["start_time"],entry["end_time"],(entry["day"]),other_details)
        logging.info("Successfully fit new timetable")
        return
    
        
    def fit_timetable_slot(self,start_time,end_time,day_num,other_details):
        if day_num - 1 > len(self.timetable):
            logging.error("Could not load complete timetable - day specified that's not in timetable")
        start_time = datetime.datetime.strptime(start_time, '%H%M')
        end_time = datetime.datetime.strptime(end_time, '%H%M')
        current_time = start_time
        while current_time < end_time:
            current_component = self.timetable[day_num][current_time.hour][current_time.minute]
            current_component.set_occupied(current_time,other_details) ##TODO: handle multiple times that this runs (each one overwrites.)
            self.occupied_indices.append([day_num,current_time.hour,current_time.minute])
            current_time += datetime.timedelta(minutes = 1)
        return True
        
    def find_occupied_slots(self):
        return self.occupied_indices
        
    ## TODO: Improve this shitty logic. SLOW
    # Returns: dictionary of list of datetimes objects, indicating the free time.
    #  eg, {day_num: [datetime.time,datetime.time]}
    def find_free_slots(self):
        free_slot_dic = {}
        for i in range(self.day_range[0],self.day_range[1]):
            curr_day = i
            free_slot_dic[i] = []
            for j in range(self.hour_range):
                curr_hour = j
                for k in range(self.minute_range):
                    curr_min = k
                    current_component = self.timetable[curr_day][curr_hour][curr_min]
                    if current_component.get_occupied() == False:
                        curr_time = datetime.datetime.strptime("{}:{}".format(curr_hour,curr_min),'%H:%M')
                        free_slot_dic[i].append(curr_time)
        return free_slot_dic
        
    def initialize_timetable(self):
        # day_of_week : Hour : Min:
        dic = {}
        for i in range(self.day_range[0],self.day_range[1]):
            dic[i] = {}
            for j in range(self.hour_range):
                dic[i][j] = {}
                for k in range(self.minute_range):
                    dic[i][j][k] = TimeTableComponent()
        return dic
        
    # Convert a number to its day. eg, 1 --> Monday
    def day_converter(self,number):
        return list(calendar.day_name)[number]
    
    # Filter the 24 hours to between 7am and 12 midnight
    def filter_normal_hours(self,free_slots):
        logging.debug("Filtering to normal hours")
        filtered_free_slots = {}
        for day in free_slots:
            filtered = [x for x in free_slots[day] if (x.hour >= 7)] #filter afer 7am to 12 midnight
            filtered_free_slots[day] = filtered
        logging.debug("Finished filtering to normal hours")
        return filtered_free_slots
              
    ## should really be its own layer
    # Convert the individual free slots to ranges. 
    # eg, [datetime.datetime(hour = 7,1 minute = 1),datetime.datetime(7,2).. datetime.datetime[9,0]
    # becomes [datetime.datetime(7,1),datetime.datetime(9,0)]
    # Input: <dic> free_slots: {day_num: [datetime.datetime(hour=7,minute = 1)...]}
    # Output: <dic> slots: {day_num: [begin_time,end_time],..}
    def convert_to_ranges(self,free_slots,english_keys = False):
        logging.debug("Converting to human understandable ranges")
        slots = {}
        for day_num in free_slots:
            if english_keys:
                day = self.day_converter(day_num - 1)
            else:
                day = day_num
            slots[day] = []
            hour_and_minute_datetime_list = free_slots[day_num]
            begin_time = hour_and_minute_datetime_list[0]
            for i in range(1,len(hour_and_minute_datetime_list)):
                current_time,previous_time = hour_and_minute_datetime_list[i],hour_and_minute_datetime_list[i-1]
                #check if last element / end of day --> append 
                if i == (len(hour_and_minute_datetime_list) - 1):
                    slots[day].append([begin_time,current_time])
                    continue
                # If the next time only differs by a minute
                if (current_time - previous_time) == datetime.timedelta(seconds=60):
                    continue
                else:
                    end_time = previous_time
                    #rare case - ignore and continue
                    if begin_time == end_time: 
                        begin_time = current_time
                        continue
                    # append the begin and end times, then reset and continue
                    slots[day].append([begin_time,end_time])
                    begin_time = current_time
        logging.debug("Completed converting to human understandable ranges")
        return slots
        
    def convert_ranges_to_human_slots(self,ranges):
        converted_dic = []
        for day in ranges:
            day_english = self.day_converter(day - 1)
            for each_range in ranges[day]:
                converted_dic.append("{}: {}:{} - {}:{}".format(day_english,\
                                                                each_range[0].hour,\
                                                                each_range[0].minute,\
                                                                each_range[1].hour,\
                                                                each_range[1].minute))
            
        return converted_dic
        
    def convert_ranges_to_flask_slots(self,ranges):
        for day in ranges:
            all_slots = ranges[day]
            for i in range(len(all_slots)):
                curr_slot_pair = all_slots[i]
                for j in range(len(curr_slot_pair)):
                    slot = curr_slot_pair[j]
                    slot = {"year":slot.year,"month":slot.month,"day":slot.day,
                            "hour":slot.hour,"minute":slot.minute}
                    curr_slot_pair[j] = slot
        return ranges
        
        
class TimeTableComponent():
    def __init__(self):#,begin_time,end_time,resolution):
        self.time = None
        self.occupied = False
        self.occupied_details = {}
        return
        
    def __str__(self):
        return "Begin: {} End: {}".format(self.begin_time,self.end_time)
        
    def get_occupied(self):
        return self.occupied
        
    def set_occupied(self,time,occupied_details = {}):
        self.occupied = True
        self.time = time
        self.occupied_details = occupied_details
        return True
#        
### TESTS
#tt = TimeTable()
#url = "https://nusmods.com/timetable/2017-2018/sem1?DSC3215[SEC]=P2&BT3101[LEC]=1&BT3103[TUT]=1&BT3103[LEC]=1&BT4221[LEC]=1&CS5242[LEC]=1"
#url2 = "https://nusmods.com/timetable/2017-2018/sem1?ACC1002[LEC]=V2&ACC1002[TUT]=V09&ACC2002[SEC]=B10&BSP1702X[SEC]=Y1&BMA5314[SEC]=F1"
#url3 = "https://nusmods.com/timetable/2017-2018/sem1?CM4242[LEC]=SL1&CM4242[TUT]=T02&CM4282=&CM4199A=&CM4227[LEC]=SL1&CM4227[TUT]=T03"
##tt.fit_new_timetable(nusmods_adapter(url))
#tt.fit_new_timetable(nusmods_adapter(url3))
#slots = tt.find_free_slots()
#s = tt.filter_normal_hours(slots)
#ranges = tt.convert_to_ranges(s)
#human_interpretable = tt.convert_ranges_to_human_slots(ranges)
