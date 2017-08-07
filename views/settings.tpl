<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Discovery Settings</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <link href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,900" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,600,700,800" rel="stylesheet">
        <style>

        html, body {
            overflow-x: hidden;
        }

                * {
                    margin: 0;
                    padding: 0;
                }

                .container-fluid {
                    padding: 0;
                    margin: 0;
                }
        body {
            margin: 0;
            font-family: 'Open Sans', sans-serif;
        }
        .content-col{
            margin:35px 35px;
        }
                #nav {
                    padding: 8px;
                    padding-left: 16px;
                    background-color: #F3F0ED;
                    font-size: 18px;
                    color: #ffffff;
                }

                .header {
                    font-size: 16px;
                    font-weight: 400;
                    color: #777;
                }
        .part-head{
            color: #FA505D;
            font-size: 16px;
            font-weight: 600;
            padding-top: 0px;
            margin-top: 10px;
            margin-bottom:5px;
        }
        .part-subhead{
        }
        #submit-btn{
            margin-top:35px;
            margin-bottom:15px;
            cursor:pointer;
        }
        #buy-button{
            text-decoration: none;
            font-size: 12px;
            margin-left:1px;
            font-weight: 400;
            color: gray;
            cursor:pointer;

        }
        .progress {
            height: 10px;
        }
        input[type="checkbox"]{
            margin-right: 4px;
        }
        .form-check-label{
            font-size:14px;
            font-weight: 400;
        }
        .invisible-part{
            display: none;
        }
        .disabled-check{
                    color: #8c8782;

        }
.flatbutton {
    display: inline-block;
    border: none;
    padding: 0;
    vertical-align: top;
    background-color:#FA505D;
        width: 100%;
        margin: 10px 0;
        height: 46px;
        line-height: 46px;
    width: 120px;
    height: 42px;
    line-height: 41px;
    font-size: 15px;
    white-space: nowrap;
    color: #fff;
    text-align: center;
    text-transform: none;
    overflow: hidden;
    border-radius: 3px;
    -webkit-transition-property: background-color,color,border;
    -moz-transition-property: background-color,color,border;
    transition-property: background-color,color,border;
    -webkit-transition-duration: 75ms;
    -moz-transition-duration: 75ms;
    transition-duration: 75ms;
    -webkit-transition-timing-function: ease;
    -moz-transition-timing-function: ease;
    transition-timing-function: ease;
    cursor: pointer;
}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/superagent/3.3.1/superagent.min.js"></script>
  </head>
  <body>
    <script>
    (function(d, s, id){
      var js, fjs = d.getElementsByTagName(s)[0];
      if (d.getElementById(id)) {return;}
      js = d.createElement(s); js.id = id;
      js.src = "//connect.facebook.com/en_US/messenger.Extensions.js";
      fjs.parentNode.insertBefore(js, fjs);
    }(document, 'script', 'Messenger'));
    </script>
     <div class="container-fluid">
        <div class="row">
                <div class="col-xs-12">
            <div id="nav">
                <span class="header header-title">
                {{ userc._("Discovery Settings") }}
                </span>
            </div>
</div>
            <div class="content-col col-12 col-md-0 pull-md-3 bd-content">
                <form id="gender-form"  style="padding-top: 20px"  >
                    <h5 class="part-head">
                    {{ userc._("I want to find...") }}
                    </h5>
                    <div style="padding-top: 4px" class="form-checkbox">
                      <label class="form-check-label">
                        <input type="checkbox" class="form-check-input" name="genders" value="male" {{ 'checked="checked"' if "male" in settings['finding_genders'] else '' }} >
                        {{ userc._("Men") }}
                        </input>
                      </label>
                    </div>
                    <div style="padding-top: 4px" class="form-checkbox">
                      <label class="form-check-label">
                        <input type="checkbox" class="form-check-input" name="genders" value="female" {{ 'checked="checked"' if "female" in settings['finding_genders'] else '' }} >
                        {{ userc._("Women") }}</input>
                      </label>
                    </div>
                </form>

                <form id="lang-form"  style="padding-top: 18px" >
                <h5 class="part-head">{{ userc._("Languages") }}</h5>
                % for lang in languages:
                <div style="padding-top: 4px" class="form-checkbox">
                  <label class="form-check-label">
                    <input type="checkbox" class="form-check-input" name="languages" value="{{ lang.code }}" {{ 'checked="checked"' if lang.checked else '' }}
                    >{{lang.name}}</input>
                  </label>
                </div>
                % end
                </form>

                <form id="location-form" class="{{ 'invisible-part' if settings['country'] == 'undefined' else '' }}"  style="padding-top: 20px" >
                <h5 class="part-head">Location (Preference)</h5>
                <div style="padding-top: 4px" class="form-checkbox">
                  <label class="form-check-label">
                    <input type="checkbox" class="form-check-input" name="location_enabled" value='location_enabled' {{ 'checked="checked"' if settings['location_enabled'] and settings['country'] != 'undefined' else '' }}  disabled>In {{ settings['country'] }}</input>
                  </label>
                </div>
                </form>

                <button id="submit-btn" value='save' class="flatbutton" onclick="handleSubmit()">{{ userc._('Save') }}</button><br />
            </div>
        </div>
    </div>
    <script src="/public/js/settings.js">
    </script>
  </body>
</html>
