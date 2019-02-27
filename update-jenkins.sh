#! /usr/bin/env bash
#
# Downloads a new Jenkins version, places in the directory and links the latest
# version.

# The target directory
source ~/.config/update-server
if [[ -d "${JENKINS_DIR}" ]]; then
    echo "Storing new Jenkins version to $JENKINS_DIR"
else
    echo "Jenkins directory not specified." \
	    "Check if JENKINS_DIR is set in ~/.config/update-server"
    exit 1
fi
# The target file
jenkins_binary="${JENKINS_DIR}jenkins.war"

# Set the version. Manually for now.
if [[ $1 =~ [1-9][0-9]*\.[0-9]+ ]]; then
    echo "Updating to version $1."
else
    echo "Version $1 is invalid. Should be like #.##."
    exit
fi
jenkins_latest=$1

# Mirror page has wrong certificate

# Download .war file
wget http://mirrors.jenkins.io/war/${jenkins_latest}/jenkins.war
# Download certificate
wget http://mirrors.jenkins.io/war/${jenkins_latest}/jenkins.war.sha256

# Veify sha256. It is the first sequence before one or more spaces.
expected_sha256_hash=$(cat jenkins.war.sha256 | awk '{ print $1 }')
sha256_hash=`sha256sum jenkins.war | awk '{ print $1 }'`

if [ "$expected_sha256_hash" == "$sha256_hash" ]; then
    echo "sha256 valid"
else
    echo "sha256 invalid"
    exit 1
fi

# Copy over
jenkins_target="${jenkins_directory}jenkins-${jenkins_latest}.war"
cp jenkins.war ${jenkins_target}
cp jenkins.war.sha256 "${jenkins_target}.sha256"

# Create the symbolic link
unlink ${jenkins_binary}
ln -s ${jenkins_target} ${jenkins_binary}

# Restart the service
echo "Restarting jenkins with version ${jenkins_latest}"
service jenkins restart
