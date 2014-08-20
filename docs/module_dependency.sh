# 'dot' is the command line tool from the graphviz library - http://www.graphviz.org/Home.php

cd `dirname $0`
dot -Tpng < module_dependency.graphviz > module_dependency.png

