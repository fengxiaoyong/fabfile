#! -*- coding=utf8 -*-
from fabric.api import *
import time
from fabfile_git import addenv
env.hosts=['192.168.8.87','192.168.9.79']
env.exclude_hosts=['192.168.9.79']
filenames=['Python-3.5.2.tgz']
UP_DIR='/tmp'
env.key_filename='~/.ssh/id_rsa'
def up_load():
	#put('.ssh/id_rsa.pub' ,'/root')
	for filename in filenames:
		put(filename,UP_DIR)

def before_intall():
	with settings(warn_only=True):
		run('yum -y install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make')
def tar():
	with cd(UP_DIR):
		for filename in filenames:
			run('tar -zvxf %s' %filename)
			run('rm -f %s '%filename)
def install():
	with cd(UP_DIR):
		for filename in filenames:
			end_index=filename.index('.tgz')
			dir_1=filename[:end_index]
			with cd(dir_1):
				run('./configure --prefix=/usr/local/python35')
				run('make')
				run('make install')
				with cd('..'):
					run('rm -rf %s' %dir_1)

def env_create():
	#run('yes|cp /etc/profile /etc/profile.bak')
	run('echo "export PATH=/usr/local/python35/bin:$PATH">>/etc/profile')
	run("source /etc/profile")
#@parallel
def deploy():
	before_intall()
	up_load()
	tar()
	install()
	env_create()
