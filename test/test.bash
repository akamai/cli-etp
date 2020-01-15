#!/bin/bash
dir=$(cd .. && pwd -P)

echo "Starting akamai cli etp tests..."

if [ "$1" == "cli" ]; then
    # Native Akamai CLI
    interpreter='akamai etp -v'
else
    # For development purpose
    if type -t deactivate > /dev/null; then
        deactivate
    fi
    . $dir/venv.27/bin/activate
    interpreter="$dir/bin/akamai-etp -v"
fi

etp_config_id=$(grep etp_config_id ~/.edgerc|awk '{print $3}')
if [$etp_config_id == ""]; then
    echo "ERROR: cannot extract etp_config_id in ~/.edgerc"
    exit 2
fi

random_ip="1.2.3.$(($RANDOM % 255))"
random_ip2="3.2.1.$(($RANDOM % 255))"
random_ip3="12.34.56.$(($RANDOM % 255))"

random_host="host-$random_ip.test.akamai.com"
random_host2="host2-$random_ip.test.akamai.com"
random_host3="host3-$random_ip.test.akamai.com"

# Version

$interpreter version

# Pull events

$interpreter event aup
$interpreter event threat

exit

# List management

$interpreter list add $etp_config_id $random_ip
$interpreter list add $etp_config_id $random_ip2 $random_ip3
$interpreter list add $etp_config_id $random_host
$interpreter list add $etp_config_id $random_host2 $random_host3
$interpreter list remove $etp_config_id $random_ip
$interpreter list remove $etp_config_id $random_ip2 $random_ip3
$interpreter list remove $etp_config_id $random_host
$interpreter list remove $etp_config_id $random_host2 $random_host3
$interpreter list deploy $etp_config_id

if type -t deactivate > /dev/null; then
    deactivate
fi

echo "Test completed."