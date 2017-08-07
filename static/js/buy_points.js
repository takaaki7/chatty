function getQueryVariable(variable) {
    var scripts = document.getElementsByTagName('script');
    var query;
// get your current script;
    for (var i = 0, l = scripts.length; i < l; i++) {
        if (scripts[i].src.indexOf('buy_points.js') !== -1) { // or your script name
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
var handler;

var selectedPoints;
var selectedPrice;
var selectedCurrency;
window.onload = function () {
    var uid = location.pathname.split('/')[1];
    var pubKey = getQueryVariable('public_key');
    handler = StripeCheckout.configure({
        key: pubKey,
        image: "/public/images/icon_mid.jpg",
        locale: 'auto',
        token: function (token) {
            console.log("token:" + token);
            var req = superagent.post('/' + getQueryVariable("uid") + '/payments?access_token=' + getQueryVariable('access_token'));
            document.getElementById("loader-container").style.display = "block";
            document.getElementById("menus").style.display = "none";
            req.send({
                token: token.id,
                points: selectedPoints,
                price: selectedPrice,
                currency: selectedCurrency
            });
            req.end(function (err, res) {
                document.getElementById("loader-container").style.display = "none";
                document.getElementById("menus").style.display = "block";
                if (!err) {
                    document.getElementById("my-points").innerHTML = res.body['points'];
                    alert('Payment approved!');
                    setTimeout(function () {
                        if (MessengerExtensions.isInExtension()) {
                            MessengerExtensions.requestCloseBrowser(function success() {

                            }, function error(err) {
                                console.log(err)
                            });
                        } else {
                            close();
                        }
                    }, 2000)
                } else {
                    if (err.response && err.response.body && err.response.body.text) {
                        console.log("err" + JSON.stringify(err.response));
                        alert(err.response.body.text)
                    } else {
                        alert("Your payment failed. Please try again later.\n" +
                            "If the problem persists, please contact us at here. ")
                    }
                }
            })
            // You can access the token ID with `token.id`.
            // Get the token ID to your server-side code for use.
        }
    });
// Close Checkout on page navigation:
    window.addEventListener('popstate', function () {
        handler.close();
    });
}

var handlePurchase = function (points, price, currency) {
    selectedPoints = points;
    selectedPrice = price;
    selectedCurrency = currency;
    handler.open({
        name: 'Chatty',
        description: points + 'points',
        currency: currency,
        amount: price
    });
}