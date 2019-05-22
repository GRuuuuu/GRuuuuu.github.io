#!/bin/sh
curl -XPOST -u "apikey:0AaUBURhnkdxBbPgUhmti8t4PIsY6hX9N2HxCaLTZNc5" \
-F "images_file=@"$1"" \
"https://gateway.watsonplatform.net/visual-recognition/api/v3/detect_faces?version=2018-03-19"
