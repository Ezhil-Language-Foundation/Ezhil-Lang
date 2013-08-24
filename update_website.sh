#!/bin/bash
echo "Copying HTML files"
sudo cp ./website/* /var/www/html/
echo "Restart httpd"
sudo service httpd restart

