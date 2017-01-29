const url = require('url');
const request = require('request');

// dummies + sample call
const tt = 'https://nusmods.com/timetable/2016-2017/sem2?CS2107[LEC]=1&CS2107[TUT]=3&CS2102[LEC]=1&CS2102[TUT]=1&SSS1207[LEC]=SL1&CS4244[LEC]=1&CS4244[TUT]=3&ACC1002X[LEC]=X3&ACC1002X[TUT]=X05';
const currSemUrl = 'https://nusmods.com/api/2016-2017/2/modules/';
parse(tt, (err, obj) => {
  if (err) {
    console.log(err);
  }
  console.log(obj);
});

// Takes in a user's nusmods url and returns
function parse(ttUrl, cb) {
  let timetableDict = formatModuleList(url.parse(ttUrl, true).query);
  let returnObj = {};
  let count = 0;
  for (key in timetableDict) {
    let moduleCode = key;
    api_getModuleLessonTimetable(moduleCode, (err, moduleTimetable) => {
      if (err) {
        return cb(err);
      }
      let user_moduleTimetable = [];
      for (let i = 0; i < moduleTimetable.length; i++) {
        let currLesson = moduleTimetable[i];
        let module_lessonType = currLesson['LessonType'];
        let user_classNumber = timetableDict[moduleCode][module_lessonType];
        if (currLesson['ClassNo'] === user_classNumber) {
          user_moduleTimetable.push(currLesson);
        }
      }
      returnObj[moduleCode] = user_moduleTimetable;
      count++;
      if (count === Object.keys(timetableDict).length) {
        return cb(err, returnObj);
      }
    })
  }
}

// Takes in a module code and passes into a callback a dictionary of all lessons being
// conducted for the module
function api_getModuleLessonTimetable(moduleCode, cb) {
  request({
    method: 'GET',
    url: `https://nusmods.com/api/2016-2017/2/modules/${moduleCode}/timetable.json`,
    headers: {
      'Content-Type': 'application/json'
    },
  }, (err, res, body) => {
    if (err) {
      return cb(err);
    }
    return cb(err, JSON.parse(body));
  });
}


/**
  * Helper function
  * Takes in a dictionary of the url qs and returns a formatted dictionary
  * in the form of {moduleCode: [Lecture: 'ClassNo_l', Tutorial: 'ClassNo_t']};
  */
function formatModuleList(dict) {
  let formattedDict = {};
  for (blockCode in dict) {
    let blockCodeArr = blockCode.split('[');
    let moduleCode = blockCodeArr[0];
    let lessonType = formatLessonType(blockCodeArr[1].slice(0, -1));

    if (!formattedDict[moduleCode]) {
      formattedDict[moduleCode] = {};
    }
    formattedDict[moduleCode][lessonType] = dict[blockCode];
  }
  return formattedDict;
}

// Helper function to standardise terms
function formatLessonType(lessonType) {
  if (lessonType === 'LEC') {
    return 'Lecture';
  }
  else if (lessonType === 'TUT') {
    return 'Tutorial';
  }
}
