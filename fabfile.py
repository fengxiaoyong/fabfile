from fabric.api import *
from fabric.contrib import files
import os
import re
env.user='root'
env.password='yanlihua1982'
env.hosts=['192.168.8.90']
#env.roledefs={
#	'test1':['192.168.8.90'],
#	'test2':['192.168.8.108']
#}
#@roles('test1')
UP_DIR='/tmp'
filenames=['nginx-1.10.2.tar.gz']
#@task(name='up')
def upload():
	for filename in filenames:
		result=put(filename,UP_DIR)
		if result.failed:
			abort('up_loading nginx file %s failed...' %filename)
		print('upload succeeded...')

def tar():
	 with cd(UP_DIR):
		for filename in filenames:
			if files.exists(filename):
				run('tar -zvxf %s' %filename)
def before_install():
	with settings(warn_only=True):
		run('yum -y install gcc gcc-c++')
		run('yum -y install openssl openssl-devel')
		run('yum -y install zlib')
		run('yum -y install pcre')

def install():
	for filename in filenames:
		end_index=filename.index('.tar.gz')
		dirname=filename[:end_index]
		dir_prefix=filename.split('-')[0]
		print dirname
                if dir_prefix=='nginx':
			with cd(os.path.join(UP_DIR,dirname)):
				run('./configure --prefix=/usr/local/%s --with-http_ssl_module --with-pcre  --with-http_stub_status_module --with-threads' % dir_prefix)
				run('make')
				run('make install')
	
