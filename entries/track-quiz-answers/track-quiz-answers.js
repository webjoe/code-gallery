var _learnq = _learnq || [];

var continueButton = document.querySelector("#ProfileContinue");
var finishButton = document.querySelector("#SurveyDone");

var local = JSON.parse(localStorage.getItem("surveyStatus"));

function sendIdentify() {
  var local = JSON.parse(localStorage.getItem("surveyStatus"));
  var emailAddress = document.querySelector(
    "#SurveyProfileContent input[type='email']"
  ).value;
  var first_name = document.querySelector(
    "#SurveyProfileContent input[name='first_name']"
  ).value;
  var last_name = document.querySelector(
    "#SurveyProfileContent input[name='last_name']"
  ).value;
  var sex = document.querySelector("#SurveyProfileContent input[name='sex']")
    .value;
  var diet = document.querySelector(
    "#SurveyProfileContent input[name='dietary_restrictions']"
  ).value;

  var item = {
    $email: emailAddress || "",
    $first_name: first_name || "",
    $last_name: last_name || "",
    sex: sex || "",
    dietary_restrictions: diet || "",
    interests: local.interests,
  };
  _learnq.push(["identify", item]);
  console.log("Identify Call:", item);
}

function sendQuizResults() {
  var local = JSON.parse(localStorage.getItem("surveyStatus"));
  var quiz = local.quizSections;

  var item = {
    coffee_intake: quiz.energy[0][0],
    energy_levels: quiz.energy[1][0],
    struggle_to_relax: quiz.energy[2][0],
    digestive_issues: quiz["gut-health"][0],
    bathroom_habits: quiz["gut-health"][1][0],
    fermented_foods: quiz["gut-health"][2][0],
    skin_concerns: quiz.skin[0],
    skin_hormonal: quiz.skin[1][0],
    skin_supplements_yes_or_no: quiz.skin[2][0],
    skin_supplements_list: quiz.skin[3] || "",
  };

  _learnq.push(["identify", item]);
  console.log("Adding Props to Klaviyo: ", item);
}

function sendEvent(eventName, properties) {
  _learnq.push(["track", eventName, properties]);
  console.log("Sent Event Named: ", eventName);
}

window.onload = function () {
  var email = document.querySelector(
    "#SurveyProfileContent input[type='email']"
  );
  email.addEventListener("blur", sendIdentify, true);
  continueButton.addEventListener("click", sendIdentify, false);
  continueButton.addEventListener(
    "click",
    sendEvent("Started Quiz", { finished: false }),
    false
  );
  finishButton.addEventListener("click", sendQuizResults, false);
  finishButton.addEventListener(
    "click",
    sendEvent("Finished Quiz", { finished: true }),
    false
  );
};
