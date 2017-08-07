<html>
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Select Language</title>
    <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css" integrity="sha384-BVYiiSIFeK1dGmJRAkycuHAHRg32OmUcww7on3RYdg4Va+PmSTsz/K68vbdEjh4u" crossorigin="anonymous">
    <style>
        body {
            margin: 1em;
        }
    </style>
  </head>
  <body>
    <h4>Selected Languages</h4>
    <ul>
    % for lang in languages:
        <li>{{lang.name}}</li>
    % end
    </ul>
    <p>Please close if you like this selection. Or you can <a href="{{ url('setting_lang', uidenc=uidenc) }}">reselect</a>.</p>
  </body>
</html>
