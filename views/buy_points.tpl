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
        * {
            margin: 0;
            padding: 0;
        }

        .container-fluid {
            padding: 0;
            margin: 0;
        }

        html, body {
            overflow-x: hidden;
        }

        body {
            background-color: #F3F0ED;
            font-family: 'Open Sans', sans-serif;
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

        .header-title {
        }

        #desc1 {
            padding-top: 25px;
            padding-bottom: 25px;
            background-color: #ffffff;
        }

        p {
            margin: 0;
        }

        .my-points-label {
            font-size: 16px;
            color: #8A8A8A;
            margin: 0;
        }

        .my-points {
            margin-top: 12px;
            margin-left: 7px;
            font-size: 35px;
            font-weight: 700;
            color: #f05a69;
        }

        .label-pt {
            font-size: 16px;
            color: #f05a69;
        }

        .points {
            font-size: 16px;
            font-weight: 500;
            color: #1E1E1E;
        }

        .price {
            font-size: 16px;
            font-weight: 500;
            color: #f05a69;
            margin-top: 9px;
        }

        .price-without-dispute {
            font-size: 16px;
            font-weight: 500;
            color: #f05a69;
        }

        .dispute {
            font-size: 12px;
            margin-top: 2px;
            color: #8c8782;
        }

        hr {
            margin: 0;
            padding: 0;
            margin-top: 10px;
            margin-bottom: 10px;
            width: 100%;
        }

        .discription {
            color: #888888;
            font-size: 12px;
            padding-left: 16px;
            padding-right: 16px;
        }

        .label-list-group {
            padding: 8px 15px;
            font-size: 12px;
            color: #888888;
        }

        .list-group {
            margin-bottom: 16px;
        }

        .list-group-item:first-child {
            border-top: transparent;
            border-top-left-radius: 0;
            border-top-right-radius: 0;
        }

        .list-group-item:last-child {
            border-bottom-left-radius: 0;
            border-bottom-right-radius: 0;
            border-bottom: transparent;
        }

        .list-group-item {
            border-left: transparent;
            border-right: transparent;
            padding-left: 16px;
            padding-right: 16px;
            height: 62px;
            cursor: pointer;
        }

        .item-without-dispute {
            padding-top: 9px;
        }


        .invisible-part{
            display: none;
        }
        #loader-container{
            display: none;
        }
        .loader {
            border: 8px solid #f3f3f3; /* Light grey */
            border-top: 8px solid #3498db; /* Blue */
            border-radius: 50%;
            width: 60px;
            height: 60px;
            margin-top: 60px;
            animation: spin 2s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        #processing-label{
font-size: 18px;
    margin-top: 40px;
    font-weight: 500;
    color: #1E1E1E;
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
<div id="menus" class="container-fluid">
    <div class="row">
        <div class="col-xs-12">
            <div id="nav">
                <span class="header header-title">Points</span>
            </div>
            <div id="desc1">
                <p class="my-points-label text-center">{{ userc._('My Points') }}</p>
                <div class="text-center"><span id="my-points" class="my-points ">{{ userc.user.points }}</span><span class="label-pt">pt</span></div>
            </div>
        </div>
    </div>
    <p class="label-list-group">
    {{ userc._('Purchase') }}
    </p>
    <ul class="list-group">
        % for menu in menus:
        <li class="list-group-item" onclick="handlePurchase({{ menu.points }}, {{ menu.price }}, '{{ menu.currency }}')">
            <div class="{{ 'item-without-dispute' if menu.dispute_label == '' else '' }} ">
                <span class="points">{{ menu.points }} points</span>
                <span class="{{ 'price-without-dispute' if menu.dispute_label == '' else 'price' }} pull-right">
                    {{ currency_symbol }}{{ menu.price/100.0 }}
                </span>
                % if menu.dispute_label != '':
                    <p class="dispute">{{ menu.dispute_label }}</p>
                % end

            </div>
        </li>
        % end
    </ul>
    <div>
        <p class="discription">
        {{ userc._('By purchasing points, you can select the gender of the people you want to talk with.') }}
        </p>
    </div>

</div>
    <div id="loader-container" class="col-12 col-md-0 pull-md-3 bd-content">
        <p id="processing-label" class="center-block text-center">Processing...</p>
        <div id="spin-loader" class="center-block loader"></div>
    </div>
    <script src="https://checkout.stripe.com/checkout.js"></script>
    <script src="/public/js/buy_points.js?public_key={{ public_key }}&access_token={{ access_token }}&uid={{ uidenc }}">

    </script>
  </body>
</html>
