<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Chatty</title>
    <link rel="stylesheet"
          href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css"
          integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u"
          crossorigin="anonymous">
    <script>
      (function (d, s, id) {
        var js, fjs = d.getElementsByTagName(s)[0];
        if (d.getElementById(id)) {
          return;
        }
        js = d.createElement(s);
        js.id = id;
        js.src = "//connect.facebook.com/en_US/messenger.Extensions.js";
        fjs.parentNode.insertBefore(js, fjs);
      }(document, 'script', 'Messenger'));
    </script>
    <style>
        .lead {
            margin-bottom: 0;
        }

        .title {
            display: none;
        }

        #title-loading {
            display: block;
        }

        #questionnaire_button {
            margin-top: 20px;
            display: block;
            color: #FB003D;
            background-color: transparent;
            border-color: #FB003D;
        }

        #caption-ad {
            font-size:12px;
            margin-top: 20px;
        }

        #share_buttons_row {
            margin-top: 20px;
        }

        #close_button {
            margin-top: 20px;
            display: block;
        }

        #ad-iframe {
            width: 100%;
            height: 500px;
        }
        .dummy_td {
            width: 5px;
        }

        .wrap_content {
            padding: 40px 15px;
            text-align: center;
        }

        /*hide body contents at first to avoid share buttons quaking*/
        .row {
            display: none;
        }

        #share_buttons_table {
            display: inline-block;
        }
    </style>
</head>
<body>
<script src="//go.mobtrks.com/notice.php?p=1123959&interstitial=1"></script>
<script type="text/javascript" src="//go.oclaserver.com/apu.php?zoneid=1124562"></script>

<div id="fb-root"></div>
<script>(function (d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s);
  js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.8&appId=1452307184781979";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));</script>
<div id="root_container" class="container">
    <div class="wrap_content">
        <p id="title-loading" class="title lead">
            {{ user_c._("Loading...") }}
        </p>
        <p id="title-questionnaire" class="title lead">
            {{ user_c._("Thank you for using Chatty.") }}<br/>
            {{ user_c._("To start a new chat, please wait {hours} hours and {minutes} minutes, or answer a survey.").format(hours=hours, minutes=minutes) }}<br/>
            {{ user_c._("The survey should only take a couple of minutes of your time.") }}

        </p>
        <p id="title-thank-you" class="title lead">
            {{ user_c._("Thank you for answering the questionnaire.") }}<br/><br/>
            {{ user_c._("Now You can start a new chat!") }}<br/>
            {{ user_c._("If you like Chatty, please share.") }}
        </p>
        <p id="title-available" class="title lead">
            {{ user_c._("Now You can start a new chat!") }}<br/>
            {{ user_c._("If you like Chatty, please share.") }}
        </p>

        <div class="row">
            <div class="col-lg-6 col-lg-offset-3">
                <div id="questionnaire_button" class="btn btn-default">
                    {{ user_c._("Answer a Survey") }}
                </div>
            </div>
        </div>

        <div id="share_buttons_row" class="row">
            <div id="share_buttons_col" class="col-lg-6 col-lg-offset-3">
                <table id="share_buttons_table">
                    <tbody>
                    <tr>
                        <td>
                            <div class="g-plus" data-action="share"
                                 data-annotation="none" data-height="28"
                                 data-width="60"
                                 data-href="https://m.me/ChattyMessengerBot"></div>

                        </td>
                        <td class="dummy_td"></td>
                        <td>
                            <div class="fb-share-button"
                                 data-href="https://m.me/ChattyMessengerBot"
                                 data-layout="button" data-size="large"
                                 data-mobile-iframe="true">
                                <a
                                        class="fb-xfbml-parse-ignore"
                                        target="_blank"
                                        href="https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fm.me%2FChattyMessengerBot&amp;src=sdkpreparse">シェア</a>
                            </div>
                        </td>
                        <td class="dummy_td"></td>
                        <td><a href="https://twitter.com/share"
                               class="twitter-share-button"
                               data-url="https://m.me/ChattyMessengerBot"
                               data-text="Chatty: Talk to strangers, online chat, without installing app:"
                               data-size="large">Tweet</a>
                            <script>!function (d, s, id) {
                              var js, fjs = d.getElementsByTagName(s)[0], p = /^http:/.test(d.location) ? 'http' : 'https';
                              if (!d.getElementById(id)) {
                                js = d.createElement(s);
                                js.id = id;
                                js.src = p + '://platform.twitter.com/widgets.js';
                                fjs.parentNode.insertBefore(js, fjs);
                              }
                            }(document, 'script', 'twitter-wjs');</script>
                        </td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div id="close_button_row" class="row">
            <div class="col-lg-6 col-lg-offset-3">
                <div id="close_button"
                     class="btn btn-default">
                    {{ user_c._("Close") }}
                </div>
            </div>
        </div>
        <div id="native-ad" class="row">
        <p id="caption-ad" class="lead pull-left">Ad:</p>
            <iframe id="ad-iframe" src="https://go.ad2up.com/afu.php?id=1129462"></iframe>
        </div>
    </div>
</div>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.11.2/jquery.min.js"></script>
<script src="/public/js/activate.js?debug={{debug}}&hours={{hours}}&&minutes={{minutes}}&uid={{uid}}"></script>
<script src="https://apis.google.com/js/platform.js"
        async defer></script>
</body>
</html>