#!/bin/bash
echo "Copying HTML files"
sudo cp ./website/* /var/www/html/
sudo cp ./web/ezhil_eval.html /var/www/html
sudo cp ./web/ezhil_web.py /var/www/cgi-bin
echo "Restart httpd"
sudo service httpd restart

