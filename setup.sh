#!/bin/bash
if [ "$EUID" -ne 0 ]
    then
    echo "Must be root, run sudo -i before running this script."
	exit;
fi
echo -e "IMPORTANT: this will delete default nginx sites!\r\nYou have 3 seconds to back off...";
sleep 3;
echo "Deleting default nginx sites..."
rm /etc/nginx/sites-enabled/*
echo "Copying nginx default site file..."
cp nginx.site /etc/nginx/sites-enabled/default-site
dir=`pwd`
new_dir=$(echo $dir | sed 's/\//\\\//g')
exp="s/\%ROOT\%/${new_dir}\/html/g"
sed -i $exp /etc/nginx/sites-enabled/default-site
echo "Installing NginX, HostAPd, DNsMasq, PHP...etc"
apt install -y nginx dnsmasq hostapd php7.3-fpm php7.3-mbstring php7.3-mysql php7.3-curl php7.3-gd php7.3-curl php7.3-zip php7.3-xml
echo "If all of the above went well, you're good to go."