const api = require('./api.js');

function TimeTable(){
    // 13*2 half an hour blocks starting at 8am, for 5 days a week
    // main function
    this.populateTimetableWithURL = function(url){
      return this.queryAPI(url, (err, userTimetable) => {
        for (let mod in userTimetable) {
          let moduleLessons = userTimetable[mod];
          for (var i = 0; i < moduleLessons.length; i++){
            let lesson = moduleLessons[i];
            this.addToTimetableArray(lesson);
          }
        }
      });
    }

    this.addToTimetableArray = function(event){
        if (event["EndTime"] % 100 != 0){
            event["EndTime"]  += 20; // super hacky to make it 50
        }
        indexesToAddTo = this.calculateIndexes(event);
        for (var i = 0; i < indexesToAddTo.length; i++){
            indexToAddTo = indexesToAddTo[i];
            currentTime = this.timetableArray[indexToAddTo[1]][indexToAddTo[0]]["CurrentTime"];
            currentDay = this.timetableArray[indexToAddTo[1]][indexToAddTo[0]]["CurrentDay"];
            event["CurrentTime"] = currentTime;
            event["CurrentDay"] = currentDay;
            this.timetableArray[indexToAddTo[1]][indexToAddTo[0]] = event;
        }
        return true;
    }

    this.calculateIndexes = function(event){
        xIndexStart = (event["StartTime"] - this.beginningTime) / 50;
        yIndexStart = this.dayOfWeekAsInteger(event["DayText"]);

        xIndexEnd = (event["EndTime"] - this.beginningTime) / 50;
        xIndexEnd -= 1; //offset.
        yIndexEnd = yIndexStart;

        const difference = xIndexEnd - xIndexStart;
        array = new Array(difference + 1);

        var counter = 0;
        for (var i = xIndexStart; i <= xIndexEnd; i++){
            array[counter] = [i,yIndexEnd];
            counter += 1;
        }
        return array;
    }

    this.queryAPI = function(url, cb){
        api.parse(url, (err, obj) => {
          if (err) {
            return cb(err);
          }
          return cb(err, obj);
        });
    }

    this.createArray = function(x,y) {
        var currentTime = this.beginningTime;
        var arr = new Array(y);
        for (var i = 0; i < y; i++) {
          arr[i] = new Array(x);
          for (var j = 0; j < x; j++){
            arr[i][j] = {"CurrentTime":currentTime,
                         "CurrentDay":this.dayOfWeekAsDay(i)};
            currentTime += 50;
          }
          currentTime = this.beginningTime;
        }
        return arr;
    }

    this.findFreeSlots = function(){
        var freeSlots = [];
        counter = 0;
        for (var day = 0; day < this.timetableArray.length; day++) {
            for (var timeslot = 0; timeslot < this.timetableArray[0].length; timeslot++){
                currentTimeSlot = this.timetableArray[day][timeslot];
                if (currentTimeSlot["TimeStart"] == undefined){
                    freeSlots[counter] = [currentTimeSlot["CurrentTime"],currentTimeSlot["CurrentDay"]];
                    counter += 1;
                }
            }
        }

        return freeSlots;
    }

    this.dayOfWeekAsInteger = function (day) {
        return ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"].indexOf(day);
    }

    this.dayOfWeekAsDay = function(dayInteger){
        hash = {0:"Monday",
                1:"Tuesday",
                2:"Wednesday",
                3:"Thursday",
                4:"Friday",
                5:"Saturday",
                6:"Sunday"}
        return hash[dayInteger];
    }

    this.xAxisBlocks = 13*2;
    this.yAxisBlocks = 5;
    this.beginningTime = 0800;
    this.endingTime = this.beginningTime + (this.xAxisBlocks * 50);
    this.timetableArray = this.createArray(this.xAxisBlocks,this.yAxisBlocks);
}

z = new TimeTable();
z.populateTimetableWithURL("https://nusmods.com/timetable/2016-2017/sem2?BT4211[LEC]=1&BT4221[LEC]=1&BT4222[LEC]=1");
console.log(z.findFreeSlots());
