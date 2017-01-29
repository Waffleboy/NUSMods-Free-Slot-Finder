const api = require ('api');

function TimeTable(){
    // 13*2 half an hour blocks starting at 8am, for 5 days a week
    // main function
    this.populateTimetableWithURL = function(url){
        
        var result = this.queryAPI(url);
        for (var module in result){
            // Iterate through the components of each module
            var moduleComponents = result[module];
            for (var i = 0; i < moduleComponents.length; i++){
                var event = moduleComponents[i];
                this.addToTimetableArray(event);
            }
        }
    }

    this.addToTimetableArray = function(event){
        if (event["TimeEnd"] % 100 != 0){
            event["TimeEnd"]  += 20; // super hacky to make it 50
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
        xIndexStart = (event["timestart"] - this.beginningTime) / 50;
        yIndexStart = this.dayOfWeekAsInteger(event["DayText"]);

        xIndexEnd = (event["timeend"] - this.beginningTime) / 50;
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

    this.queryAPI = function(url){
        // returns the hash
        testCase = {'CS2100':[{'type': "lecture",
                        'timestart': 1900,
                        'timeend': 2000,
                        'Venue':'potatoland',
                        'WeekText':'every week',
                        'DayText':"Monday"
                        },
                        {'type': "tutorial",
                        'timestart': 0900,
                        'timeend': 1000,
                        'Venue':'potatoland2',
                        'WeekText':'every week',
                        'DayText':"Tuesday"
                        },
                        {'type': "lab",
                        'timestart': 1300,
                        'timeend': 1530,
                        'Venue':'potatoland2',
                        'WeekText':'alternate week',
                        'DayText':"Wednesday"
                        }],
                    'ACC1002X':[{'type': "lecture",
                        'timestart': 1200,
                        'timeend': 1300,
                        'Venue':'potatoland',
                        'WeekText':'every week',
                        'DayText':"Thursday"
                        },
                        {'type': "seminar",
                        'timestart': 0900,
                        'timeend': 1000,
                        'Venue':'potatoland2',
                        'WeekText':'every week',
                        'DayText':"Friday"
                        }]
                    };
        return(testCase);
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
/*
z = new TimeTable();
z.populateTimetableWithURL("url");
console.log(z.findFreeSlots());*/