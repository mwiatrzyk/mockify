#!/bin/bash

THIS_DIR=`dirname $0`

ROOT_DIR="$THIS_DIR/.."

pytest $ROOT_DIR/docs/ $ROOT_DIR/mockify/ $ROOT_DIR/tests/ $@
