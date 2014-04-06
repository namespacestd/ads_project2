
#!/bin/bash

args=$#

usage() {
    echo "Usage:"
    echo "1. ./run.sh -key <api_key> -q <query> -t [infobox|question]"
    echo "2. ./run.sh -key <api_key> -f <file>  -t [infobox|question]"
    echo "Multiple word queries must be encapsulated in quotes."
}

if [ $args -eq 6 ]; then
    if [ $1 = '-key' ]; then
        key=$2
        
        if [ $3 = '-q' ] || [ $3 = '-f' ]; then
            query_file=$4
            if [ $5 = '-t' ] && [ $6 = 'infobox' ] || [ $6 = 'question' ]; then
                infobox_question=$6
                python main.py "$1" "$2" "$3" "$4" "$5" "$6" 
            else
                usage
            fi
        else
            usage
        fi

    else
        usage
    fi
else
    usage
fi