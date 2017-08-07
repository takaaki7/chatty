<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Chatty</title>
</head>
<body>
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
<h5>Sign In Completed</h5>
<script>
window.extAsyncInit=function(){
      if (MessengerExtensions.isInExtension()) {
        MessengerExtensions.requestCloseBrowser(function success() {

        }, function error(err) {
          console.log(err)
        });
      } else {
        console.log('close');
        close();
      }
}
</script>
</body>
</html>