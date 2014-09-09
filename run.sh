#!/bin/bash

cd `dirname $0`
dev_appserver.py --host 0.0.0.0 --log_level debug $@ .

