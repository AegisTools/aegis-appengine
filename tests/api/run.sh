# Runs all API unit tests

cd `dirname $0`
python -m unittest discover -p '*.py'

