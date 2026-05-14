#!/usr/bin/bash
echo -n "const GALLOP_SRC   = 'data:image/png;base64," > gallop.js
base64 gallop.mp3 | tr -d '\n' >> gallop.js
echo "';" >> gallop.js
echo -n "const OUCH_SRC   = 'data:image/png;base64," > ouch.js
base64 ouch.mp3 | tr -d '\n' >> ouch.js
echo "';" >> ouch.js
echo -n "const PLANES_SRC   = 'data:image/png;base64," > planes.js
base64 plane.mp3 | tr -d '\n' >> planes.js
echo "';" >> planes.js