# Artisan_chatbot

## Create docs
(no need to run if docs.txt already exists in data)
`python web_crawler.py`

## Test locally
```
cd artisan-chatbot

poetry env use 3.9

cat ../requirements.txt | xargs poetry add

poetry shell

poetry add "fastapi[standard]"

fastapi dev
```
For more information, pleas check [link](https://fly.io/docs/python/frameworks/fastapi/)

## Launch the app on fly.io
`fly launch`
or
`fly deploy` for re-launch

## Interact with the app
```buildoutcfg
curl -X 'POST' \
  'https://artisan-chatbot.fly.dev/chat' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "content": "What can you do?"
}'
```

