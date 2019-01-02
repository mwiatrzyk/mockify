#!/bin/bash

ROOT_DIR=`dirname $0`

pytest $ROOT_DIR/docs/ $ROOT_DIR/mockify/ $ROOT_DIR/tests/ $@
