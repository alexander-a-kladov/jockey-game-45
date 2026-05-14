#!/usr/bin/bash
echo -n "const PLANE_SRC   = 'data:image/png;base64," > plane.js
base64 plane.png | tr -d '\n' >> plane.js
echo "';" >> plane.js
echo -n "const HORSES_SRC   = 'data:image/png;base64," > horses.js
base64 horses.png | tr -d '\n' >> horses.js
echo "';" >> horses.js
echo -n "const HAY_SRC   = 'data:image/png;base64," > hay.js
base64 haystack.png | tr -d '\n' >> hay.js
echo "';" >> hay.js