#!/bin/bash

wget 'https://www.w3schools.com/w3css/4/w3.css' w3.css
sed -i '' 's/\.w3/\.market-navigator-w3/g' w3.css
mv w3.css ../css/third_party
