
import os
class Environment:
    '''this class is used to initilize variable which will be required to run the test for specific env'''
    # global new_user
    # new_user = 'new_vagrant'
    def __init__(self):
        self.maintainer_name = 'sdp.uturn@gmail.com'
        self.project_name = 'blackbird'
    def set_environment(self, env_name):
        if env_name == 'DEV':
            self.env_name = env_name
            self.jump_server_name = 'dev.example.com'
            self.jump_server_ip = '192.168.56.4'
            self.jump_user = 'vagrant'
            self.jump_ssh_key_file = os.getenv('HOME')+os.sep+'id_rsa'
            self.password_auth = False # True of False. True  is use password based ssh login
            self.jump_password = 'vagrant'
            self.test_app_list = {'http_proxy': ['dtgilles/tinyproxy','latest','',''], 'key':['image','version_or_latest','release','patch']}
            self.proxy_port = ''
            # new_user = 'vagrant_new'
        if env_name == 'QA':
            self.env_name = env_name
            self.jump_server_name = 'qa.example.com'
            self.jump_server_ip = '10.10.11.10'
            self.jump_user = 'vagrant'
            self.jumpnode_ssh_key_file =''

