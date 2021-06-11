#!/bin/bash
dir=$(cd .. && pwd -P)

echo "Starting akamai cli etp tests..."

total_pass=0
total_fail=0

function test_result() {
    if [[ $1 == 0 ]]; then
        pass "[PASS] $2"
        total_pass=$(($total_pass + 1))
    else
        error "[FAIL] $2"
        total_fail=$(($total_fail + 1))
    fi
}

function pass() {
    GREEN='\033[0;32m'
    NC='\033[0m' # No Color
    printf "${GREEN}$1${NC}\n"
}

function error() {
    RED='\033[0;31m'
    NC='\033[0m' # No Color
    printf "${RED}$1${NC}\n"
}

if [ "$1" == "cli" ]; then
    # Native Akamai CLI
    interpreter='akamai etp -v'
else
    # For development purpose
    if type -t deactivate > /dev/null; then
        deactivate
    fi
    . $dir/venv/bin/activate
    interpreter="$dir/bin/akamai-etp -v"
fi

etp_config_id=$(grep etp_config_id ~/.edgerc|awk '{print $3}')
if [[ "$etp_config_id" == "" ]]; then
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
test_result $? "Display cli-etp version"

# Pull events

$interpreter event aup
test_result $? "Fetch recent AUP events"
$interpreter event threat
test_result $? "Fetch recent Threat events"

# List management
$interpreter list get
test_result $? "Fetch security lists"

random_listid=$($interpreter list get|sort -R| head -n 1|cut -f1 -d,)
test_result $? "Pick a random list to work with"

$interpreter list add $etp_config_id $random_ip
test_result $? "Add IP to the list $random_listid"

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

error "Total error(s): $total_fail"
pass "Total success(es): $total_pass"

echo "Test completed."