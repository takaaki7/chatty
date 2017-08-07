#!/bin/sh

#
# chatty bot 初期設定
#
# 次の環境変数を使用します
# $FB_PAGE_ACCESS_TOKEN - PAGE ACCESS TOKEN
# $FB_MESSENGER_EXTENSIONS_WHITELIST - Messenger extensions whitelist
#

if [ -z "$FB_PAGE_ACCESS_TOKEN" ]; then
   echo 'You must set $FB_PAGE_ACCESS_TOKEN.'
   exit 1
fi

if [ -z "$FB_MESSENGER_EXTENSIONS_WHITELIST" ]; then
   echo 'You must set $FB_MESSENGER_EXTENSIONS_WHITELIST.'
   exit 1
fi

#
# スタートボタン追加
# cf.) https://developers.facebook.com/docs/messenger-platform/thread-settings/get-started-button
#
echo 'add start button.'
curl -X POST -H "Content-Type: application/json" -d '{
  "setting_type":"call_to_actions",
  "thread_state":"new_thread",
  "call_to_actions":[
    {
      "payload":"START"
    }
  ]
}' "https://graph.facebook.com/v2.6/me/thread_settings?access_token=$FB_PAGE_ACCESS_TOKEN"

#
# 固定メニューの追加
# cf.) https://developers.facebook.com/docs/messenger-platform/thread-settings/persistent-menu
#
echo ''
echo 'add fixed menu.'
curl -X POST -H "Content-Type: application/json" -d '{
  "setting_type" : "call_to_actions",
  "thread_state" : "existing_thread",
  "call_to_actions":[
    {
      "type":"postback",
      "title":"Menu",
      "payload":"ACTION"
    }
  ]
}' "https://graph.facebook.com/v2.6/me/thread_settings?access_token=$FB_PAGE_ACCESS_TOKEN"

#
# Messenger Extensions Whitelist
# cf.) https://developers.facebook.com/docs/messenger-platform/messenger-extension
#
echo ''
echo 'add extensions whitelist.'
curl -i -X POST \
 -d "setting_type=domain_whitelisting" \
 -d "whitelisted_domains=%5B$FB_MESSENGER_EXTENSIONS_WHITELIST%5D" \
 -d "domain_action_type=add" \
 -d "access_token=$FB_PAGE_ACCESS_TOKEN" \
 "https://graph.facebook.com/v2.8/me/thread_settings"
