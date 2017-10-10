# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 15:54:03 2016

@author: waffleboy
"""
from flask import Flask, render_template,request,url_for,redirect
from data_formatting_module import parse_nusmods_link,nusmods_adapter
from timetable import TimeTable
import logging

app = Flask(__name__) #initialize app
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/")
def main():
    logging.info("Got a new GET request for homepage")
    return render_template('index.html')

@app.route("/timetable", methods=['POST'])
def timetable():
    if request.method == 'POST':
        logging.info("Got a new POST request with params {}".format(request.form))
        timetabledata = request.form['message']
        timetabledata = timetabledata.split()
        if very_quick_verification(timetabledata):
            logging.info("Passed verification")
            timetable_dic = find_free_slots(timetabledata)
            return render_template('timetable.html',timetable_dic=timetable_dic)
            #return redirect(url_for('foo',timetable_dic=timetable_dic))
        logging.warn("Error: Invalid URLS found")
        return "Error: Invalid URLs. Have you ensured:\n1)each URL is a valid NUSMods URL and\n2)tEach is on their own line?"
    return "Nothing here"

def find_free_slots(urls):
    timetable = TimeTable()
    for url in urls:
        formatted_lst = nusmods_adapter(url)
        timetable.fit_new_timetable(formatted_lst)
    slots = timetable.find_free_slots()
    normal_hour_slots = timetable.filter_normal_hours(slots)
    ranges = timetable.convert_to_ranges(normal_hour_slots,True)
    ranges = timetable.convert_ranges_to_flask_slots(ranges)
    return ranges
    
# V0 Doesnt need much security. If this proves to have demand, can beef up later
def very_quick_verification(urls):
    logging.info("Performing verification of URLS")
    for url in urls:
        if (url[:url.find('/timetable')] != "https://nusmods.com") or (parse_nusmods_link(url) == False):
            return False
    return True
    
if __name__ == "__main__":
	app.run(port=5000,debug=True)