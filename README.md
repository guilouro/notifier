# Notifier

Realtime Web Application

## Requirements

- [Virtualbox](https://www.virtualbox.org/)
- [Vagrant](https://www.vagrantup.com/)

## Installation
Open your terminal and get Notifier up & running:

1. `$ cd path/to/notifier`
2. `$ vagrant up`
3. `$ vagrant ssh`
4. `$ cd /vagrant/api`
5. `$ python main.py` Yes, it's main, not runserver yet...
6. Go to 192.168.33.10:8080 and BANG!

## Observations
Application now is just a realtime public chat, without reliable queue.
Consumers will consume content and this content will be no more available.

## Roadmap
I'm still thinking on improviments...

