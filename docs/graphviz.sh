# 'dot' is the command line tool from the graphviz library - http://www.graphviz.org/Home.php

cd `dirname $0`
dot -Tpng < module_dependency.graphviz > module_dependency.png
dot -Tpng < entity_keys.graphviz > entity_keys.png
dot -Tpng < issues_status_transitions.graphviz > issues_status_transitions.png

