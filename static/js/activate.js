window.onload = function () {
  console.log("onload");
  var closebtn = $("#close_button");
  closebtn.click(function () {
    closeWebView();
  });
  log("onloaded");
  customSurveyNotAvailable();
};
function pollishReady() {
  showQuestionnaireIfRemainedTime();
}
function customSurveyClosed() {
}

function customUserNotEligible() {
  log("customUserNotEligible");
  $.post("/" + getUid() + "/activate").done(function () {
    hideQuestionnaire();
  }).fail(function () {
    alert("Failed to activate");
  })
}
function customCloseAndNoShow() {
}
function customSurveyFinished() {
  log("customSurveyFinished");
  setTitle("title-thank-you");
  $.post("/" + getUid() + "/activate").done(function () {
    //noop. shouldn't close here because users can take some gift after finishing pollfish survey
    // closeWebView();
  }).fail(function () {
    alert("Failed to activate");
  })

}
function customSurveyAvailable(data) {
  log("customSurveyAvailable");
  showQuestionnaireIfRemainedTime();
}

function customSurveyNotAvailable() {
  $.post("/" + getUid() + "/activate").done(function () {
    hideQuestionnaire();
  }).fail(function () {
    alert("Failed to activate");
  })
}

function showQuestionnaireIfRemainedTime() {
  if (getQueryVariable("hours") == 0 && getQueryVariable("minutes") == 0) {
    hideQuestionnaire();
    return;
  }
  console.log("questionnaire");
  setTitle("title-questionnaire");
  $("#close_button_row").after($("#share_buttons_row"));
  var questionnaire = $("#questionnaire_button");
  questionnaire.show();
  questionnaire.click(function () {
    var thereWasSurvey = Pollfish.showFullSurvey();
    if (!thereWasSurvey) {
      hideQuestionnaire();
    }
  });
  $("#share_buttons_table").addClass("pull-right");
  $(".row").show();
}
function hideQuestionnaire() {
  setTitle("title-available");
  $("#questionnaire_button").hide();
  $("#close_button_row").before($("#share_buttons_row"));
  $("#share_buttons_table").removeClass("pull-right");
  $(".row").show();
}

function setTitle(titleId) {
  $(".title").hide();
  $("#" + titleId).show();
}

function closeWebView() {
  if (MessengerExtensions.isInExtension()) {
    MessengerExtensions.requestCloseBrowser(function success() {

    }, function error(err) {
      console.log(err)
    });
  } else {
    close();
  }
}

function log(methodname) {
  $.ajax({
    method: "POST",
    url: "/" + getUid() + "=/log",
    data: JSON.stringify({
      category: "pollfish",
      event: methodname
    }),
    contentType: "application/json; charset=utf-8"
  });
}

function isDebug() {
  return getQueryVariable("debug") === "True";
}

function getUid() {
  //oh my god, uid encrypted has '='
  return getQueryVariable("uid") + "=";
}

function getQueryVariable(variable) {
  var scripts = document.getElementsByTagName('script');
  var query;
// get your current script;
  for (var i = 0, l = scripts.length; i < l; i++) {
    if (scripts[i].src.indexOf('activate.js') !== -1) { // or your script name
      query = scripts[i].src.substr(scripts[i].src.indexOf('?') + 1);
    }
  }
  var vars = query.split('&');
  for (var i = 0; i < vars.length; i++) {
    var pair = vars[i].split('=');
    if (decodeURIComponent(pair[0]) == variable) {
      return decodeURIComponent(pair[1]);
    }
  }
  console.log('Query variable %s not found', variable);
}