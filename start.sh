#!/bin/bash
function ctrl_c() {
    echo "CTRL+C...Stopping Captive Portal..."
}
echo "Setting wlan0 IP..."
ifconfig wlan0 10.0.0.1 netmask 255.255.255.0
echo "Starting php-fpm..."
service php7.3-fpm restart;
echo "Starting nginx..."
service nginx restart;
echo "Adding iptables rules..."
iptables -t nat -A PREROUTING -s 10.0.0.0/24 -p tcp --dport 80 -j DNAT --to-destination 10.0.0.1:80;
iptables -t nat -A POSTROUTING -j MASQUERADE;
echo "Starting dnsmasq..."
dnsmasq -C dnsmasq.conf;
echo "Trapping CTRL+C..."
trap ctrl_c INT
echo "Starting HostAPd..."
hostapd hostapd.conf
echo "Killing dnsmasq..."
killall dnsmasq
echo "Clearing iptables rules..."
iptables -t nat -D PREROUTING 1;
iptables -t nat -D POSTROUTING 1;
