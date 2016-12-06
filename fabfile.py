# -*- coding=utf-8 -*-
from fabric.api import *
from fabric.contrib import files
import os,urllib2
import re
import pdb
env.user='root'
env.password='yanlihua1982'
#env.exclude_hosts=['192.168.8.90']
env.hosts=['192.168.8.108','192.168.8.90']
#env.roledefs={
#	'test1':['192.168.8.90'],
#	'test2':['192.168.8.108']
#}
#@roles('test1')
UP_DIR='/tmp'
filenames=['nginx-1.10.2.tar.gz']
pro='demo1'
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
				run('rm -f %s' %filename)
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
def startup():
	with settings(warn_only=True):
		with cd('/usr/local/nginx'):
			result=run('test -L /bin/nginx')
			if result.return_code==0:
				run('rm -f /bin/nginx')
			run('ln -s /usr/local/nginx/sbin/nginx /bin/nginx')
			result2=run('ps -ef|grep nginx')
			#pdb.set_trace()
			if result2.find('master')!=-1:
				run('nginx -s stop')
			#	print('11111111111111')
			#print('2222222222222222')
			run('nginx')
			result1=run('ps -ef |grep nginx')
			#print result1.strip()
			if  result1.find('master')!=-1:
				print 'nginx start succeeded...'
			else:
				print 'nginx start failed ... aborting'
				abort('you need to check nginx.conf')				
			#print result.lower(),result.return_code,result.succeeded,result.failed

def conf():
	tmp="""
	server {
	    listen      80; # 监听80端口

    	    root       /home/www/www;
    	    access_log /home/www/log/access_log;
            error_log  /home/www/log/error_log;

            server_name demo1.test.com.cn; # 配置域名

    	    # 处理静态文件/favicon.ico:
    location /favicon.ico {
        root /home/www/www;
    }
	
    # 处理静态资源:
    location ~ ^\/static\/.*$ {
        root /home/www/www;
    }

    # 动态请求转发到9000端口:
    location / {
        proxy_pass       http://127.0.0.1:9000;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
"""
	with settings(warn_only=True):
		rel=run('test -d /usr/local/nginx/conf/vhost')
		if rel.return_code==1:
			run('mkdir /usr/local/nginx/conf/vhost')		
		with cd('/usr/local/nginx/conf/vhost'):
			result=run('test -f %s.conf' %pro)
			if result.return_code==0:
				run('mv %s.conf %s.conf.bak'%(pro,pro))
			run("echo '%s' >%s.conf" %(tmp,pro))
	
def port_check():
	with settings(warn_only=True):
		result=run('firewall-cmd --query-port=80/tcp')	
		if result.return_code==0:
			print '80 port has been opened...'
		else:
			run('firewall-cmd --zone=public --add-port=80/tcp --permanent')
			run('firewall-cmd --reload')
		for host in env.hosts:
			response=urllib2.urlopen('http://%s/favicon.ico' %host)
			if response.code==200:
				print'主机%s 的80 端口设置成功' %host
			else:
				print "主机 %s的80端口打开失败，请检查" %host
@task(name='nginx')
@parallel
def deploy_nginx():
	upload()	
	tar()
	before_install()
	install()
	conf()
	startup()
	port_check()		
