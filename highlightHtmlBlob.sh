#!/bin/bash

mkdir -p Simply_Lift/scripts Simply_Lift/css
cp highlighter/*.css Simply_Lift/css
cp highlighter/*.js Simply_Lift/scripts

for fl in Simply_Lift/index.html; do
    sed -i -e 's:</HEAD>:<script type="text/javascript" src="scripts/shCore.js"></script><script type="text/javascript" src="scripts/shBrushXml.js"></script><script type="text/javascript" src="scripts/shBrushScala.js"></script><link href="css/shCore.css" rel="stylesheet" type="text/css" /><link href="css/shThemeDefault.css" rel="stylesheet" type="text/css" /></HEAD>:' -e 's:</BODY>:<script type="text/javascript">SyntaxHighlighter.all()</script></BODY>:' $fl
done