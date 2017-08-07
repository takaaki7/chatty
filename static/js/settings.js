function handleSubmit() {
    var uid = location.pathname.split('/')[1];
    var req = superagent.post('/' + uid + '/settings').type('form');
    var languages = document.getElementsByName("languages");
    var langBody = [];
    for (var i = 0, len = languages.length; i < len; i++) {
        var lang = languages.item(i);
        if (lang.checked) {
            langBody.push(lang.value);
        }
    }

    var genders = document.getElementsByName("genders");
    var genderBody = [];
    for (var i = 0, len = genders.length; i < len; i++) {
        var g = genders.item(i);
        if (g.checked) {
            genderBody.push(g.value);
        }
    }

    var locationEnabled = document.getElementsByName("location_enabled")[0].checked;

    req.send({
        languages: langBody,
        genders: genderBody,
        location_enabled: locationEnabled
    });

    req.end(function (err, res) {
        if (!err) {
            if (MessengerExtensions.isInExtension()) {
                MessengerExtensions.requestCloseBrowser(function success() {

                }, function error(err) {
                    console.log(err)
                });
            } else {
                close();
            }
        } else {
            alert('Failed to update settings.');
        }
    });
    return false;
}


window.onload = function () {
    var mySlider = new Slider("input#distance-slider", {});
    mySlider.on("slide", function (value) {
        var distance = document.getElementById("distance-value");
        distance.innerText = value + "km";
        distance.dataset.distance = value;
    });
};
