#!/bin/bash

# This script builds bits of text for HTML page, to load and display examples

ls ../ezhil_tests/*.n -c1 | cut -d'/' -f3 | sort -u > examples.txt
for i in `cat examples.txt`
do 
  echo '<option value="'"$i"'">'$i'</option>' 
done
echo "we have a total of " `wc -l examples.txt` " to show the user on Ezhil website"
rm examples.txt
