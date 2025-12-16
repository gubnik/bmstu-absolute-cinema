#!/bin/bash

if [[ -z $1 ]]; then
    DIR=$PWD/docs
else
    DIR=$1
fi

dot -Tpng $DIR/cinema_db.gv -o cinema_db.png
