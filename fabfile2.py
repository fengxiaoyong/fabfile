from fabric.api import settings,env,local,run,cd,lcd,abort,put,task
from fabric.contrib import files
import os
from datetime import datetime

env.hosts=['192.168.8.90','192.168.8.108']
env.user='root'
env.password='yanlihua1982'

RT_DIR='/home'
path='/root/demo1'
UP_DIR='/tmp'	
def dir_name():
	dir_path,dirname=os.path.split(path)
	return dir_path, dirname

def test():
	pass

def tar():
	dir_path,dirname=dir_name()
	with cd(dir_path):
		if os.path.isdir(path):
			local('tar -zcvf %s.tar.gz %s/' %(dirname,dirname))
		else:
			abort('tar %s is not a dir,process failed' %dirname)
def upload():
	dir_path,dirname=dir_name()
	filename=dirname+'.tar.gz'
	with cd(dir_path):
		print filename,os.path.join(dir_path,filename)
		if os.path.isfile(os.path.join(dir_path,filename)):
			result=put(filename,UP_DIR)
			if result.succeeded:
				print('upload sucessed')
				local('rm -f %s' %filename)
			else:
				if not confirm('anyway continue [y|n]?'):
					abort('upload failed....')
		else:
			abort('the upload file not correct...')	

def untar():
	dir_path,dirname=dir_name()
	filename=dirname+'.tar.gz'
	with cd(UP_DIR):
		result=run('test -f %s' %filename)
		if result.return_code==0:
			result1=run('tar -zvxf  %s' %filename)
			if result1.succeeded:
				run('rm -f %s' %filename)
		else:
			abort('the file want to untar %s is not exisited ...' %filename)

def cp():
	now=datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        dir_path,dirname=dir_name()
        filename=dirname+'_'+now
	with cd(UP_DIR):	
		with settings(warn_only=True):
			result=run('test -d %s' %dirname)
			print result.succeeded,result.failed,result.lower()
			if result.return_code==0:
				result1=run('yes|cp -r /tmp/%s  %s' %(dirname,os.path.join(RT_DIR,filename)))
				if result1.succeeded:
					run('rm -rf %s' %dirname)
				else:
					abort('cp process failed...')
			else:
				abort('dir %s is not upload or tar....i'% dirname)
	  
@task(name='dofiles')
def do_files():
	dir_path,dirname=dir_name()
	with settings(warn_only=True):
		with cd(RT_DIR):
			run('pwd')
		        if  files.exists('www'):
				run('rm -f www')
			result1=run('ls')
			r=result1.lower().split()
			L=[]
			[L.append(n) for n in r if n.startswith(dirname)]
			L.sort(reverse=True)
			print L
			result2=run('ln -s %s %s'%(L[0],'www'))
			if result2.failed:
				abort('create softlink failed ...')
			with cd('www'):
				run('mkdir log')
				run('chmod -R 755 log')

@task(name='deploy')
def deploy():
	tar()
	upload()
	untar()
	cp()
        do_files()

