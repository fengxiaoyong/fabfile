from fabric.api import local,lcd,settings,run,abort,cd,env,put
from fabric.contrib.console import confirm

env.hosts=['192.168.8.87']
#env.user='root'
#env.password='yanlihua1982'
env.key_filename='.ssh/id_rsa'

def shangchuan():
	put('../git-2.10.2.tar.gz','/root')	

def jieya():
	with cd('/root'):
		run('tar -zvxf git-2.10.2.tar.gz')	

def install_before():
	with settings(warn_only=True):
		result=run('yum install -y gcc gcc+c++')
		result1=run('yum install -y curl-devel expat-devel gettext-devel openssl-devel zlib-devel gcc perl-ExtUtils-MakeMaker')
	if result.failed or result1.failed:
		if not confirm('yum install failed.continue anyway?'):
			abort('Aborting at user request')
def install():
        with cd('git-2.10.2'):
		run('pwd')
		with settings(warn_only=True):
			result=run('make prefix=/usr/local/git all',)
			if result.failed and not confirm('install failed.continue anyway?'):
				abort('Aborting at user request')
			result1=run('make prefix=/usr/local/git install')
			if result1.failed and not confirm('install sencond failed continue anyway?'):
				abort('Aborting at user request')
def version():	
	result=local('git --version')
	pass

def addenv():
	run('echo "export PATH=/usr/local/git/bin:$PATH" >>/etc/profile')
        run('source /etc/profile')

def deploy():
	shangchuan()
	jieya()
        install_before()
	install()
	addenv()
	
	
