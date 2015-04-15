export LC_ALL=en_US.UTF-8
apt-get update
apt-get install -y python3-dev
apt-get install -y python-virtualenv
apt-get install -y postgresql
apt-get install -y libpq-dev
apt-get install -y redis-server
apt-get install -y git

curl -sL https://deb.nodesource.com/setup | sudo bash -
apt-get install -y nodejs
apt-get install -y build-essential

npm install -g bower
npm install -g gulp

su vagrant << EOF
  virtualenv -p python3 env
  source ~/env/bin/activate
  pip install -r /vagrant/api/requirements.txt
  cd /vagrant/static
  sudo bower install -f --allow-root
EOF