import sys
import os
import paramiko
import re

env_config_directory = os.getcwd()+os.sep+'/Config'
sys.path.append(env_config_directory)
import environment

class PrepareSuiteData(environment.Environment):
    def __init__(self,env_name,feature_name):
        self.set_environment(env_name)
        self.feature_name = feature_name
        self.http_proxy = ''
        self.server_list = ''

def _print_message_string(string_to_print):
    print "\n+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    print string_to_print.encode('utf-8')
    print "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
def _print_error_string(string_to_print):
    print "\nERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR"
    # print
    print "\n",string_to_print.encode('utf-8'),"\n"
    print "ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR_ERROR\n"

def _print_warning_sting(string_to_print):
    print "\nWARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING"
    print "\n", string_to_print.encode('utf-8'), "\n"
    print "WARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING_WARNING\n"

def ssh_jumpnode(env_details):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print "\n++++++++++ ssh user and node details"
    print "node ip - ", env_details.jump_server_ip
    print "username - ", env_details.jump_user
    if env_details.password_auth == True:
        if len(env_details.jump_password) == 0:
            _print_error_string("seems like jump_password is not set in environment details. ssh connection could not continue. exiting")
            return False,''
        try:
            ssh_client.connect(env_details.jump_server_ip, username = env_details.jump_user, password=env_details.jump_password)
            return True,ssh_client
        except paramiko.ssh_exception.BadAuthenticationType, e:
            _print_error_string("unable to establish ssh connection error message - "+e.message)
            return False,''
    # trying ssh connection with key file
    if len(env_details.jump_ssh_key_file) == 0:
        _print_error_string("ssh key file  is not set in environment details. trying with user local id_rsa")
        if os.path.isfile(os.getenv('HOME')+os.sep+'.ssh'+os.sep+'id_rsa'):
            key_file = os.getenv('HOME')+os.sep+'.ssh'+os.sep+'id_rsa'
            print "\n\n Using user default private key - ", key_file
        else:
            _print_error_string("seems like user does have any key file in his hone directory")
            return False,''
    else:
        if os.path.isfile(env_details.jump_ssh_key_file):
            key_file = env_details.jump_ssh_key_file
        else:
            print "\n+++++++++++++++ given ssh key file in environment details is not a valid file. checking user default id_rsa"
            if os.path.isfile(os.getenv('HOME')+os.sep+'.ssh'+os.sep+'id_rsa'):
                key_file = os.getenv('HOME')+os.sep+'.ssh'+os.sep+'id_rsa'
                print "\n\n Using user default private key - ", key_file
            else:
                _print_error_string("seems like user does have any key file in his hone directory")
                return False,''
        
    ssh_client.connect(env_details.jump_server_ip,username=env_details.jump_user, key_filename = key_file)
    s = ssh_client.get_transport().open_session()
    # set up the agent request handler to handle agent requests from the server
    paramiko.agent.AgentRequestHandler(s)
    return True,ssh_client

def run_ssh_command(env_details, cmd):
    result_dict = {}
    print "\n++++++++++++ running remote command - ", cmd
    connection_flag, ssh_client = ssh_jumpnode(env_details)
    if connection_flag == False:
        _print_error_string("unable to connect jumpserver")
        return False, ''
    print "\n+++++++++++++++ ssh connection to jumpnode establised successfully"
    # print "\n++++++++++ Checking if http proxy is already running"
    # cmd = 'docker ps '
    stdin,stdout,stderr = ssh_client.exec_command(cmd,get_pty=True)
    out = ''.join(stdout.readlines())
    err = ''.join(stderr.readlines())
    cmd_out = stdout.channel.recv_exit_status()
    ssh_client.close()
    result_dict['exit_status'] = cmd_out
    # _print_message_string(str(result_dict))
    if cmd_out == 0:
        if len(out) == 0:
            result_dict['out'] = 'success'
        else:
            result_dict['out'] = out
        return True, result_dict
    if cmd_out != 0:
        if len(err) != 0:
            result_dict['out'] = err
        elif len(out) != 0:
            result_dict['out'] = out
        else:
            result_dict['out'] = 'failed'
        return True, result_dict
    if len(out) != 0:
        result_dict['out'] = out
        return True,result_dict
    if len(err) != 0:
        result_dict['out'] = err
        return True,result_dict
    result_dict['out']='failed'
    return True, result_dict


def remove_and_start_http_proxy(env_details,http_container_name,running = False):
    if running == True:
        print "\n ++++++++ removing  stopped container of http proxy +++++++++++="
        result_flag, result_dict = run_ssh_command(env_details, 'docker rm '+http_container_name)
        if result_dict == False:
            _print_error_string("Unable to connect to jump server")
            sys.exit(1)
        if result_dict['exit_status'] > 0:
            _print_warning_sting("linux command returned a non zero exit code. command output below:\n"+result_dict['out'])
            return False,''
    print "\n +++++++++++ starting http_proxy_container +++++++++++++"
    result_flag, result_dict = run_ssh_command(env_details, 'docker run -itd -P --name '+http_container_name+' '+env_details.test_app_list['http_proxy'][0])
    if result_dict == False:
        _print_error_string("Unable to connect to jump server")
        sys.exit(1)
    if result_dict['exit_status'] > 0:
        _print_warning_sting("linux command returned a non zero exit code. command output below:\n"+result_dict['out'])
        return False,''
    print "\n++++++++++++ container started successful"
    return True,''




def is_http_proxy_running(env_details,http_container_name):
    result_flag, result_dict = run_ssh_command(env_details, 'docker ps -a ')
    if result_dict == False:
        _print_error_string("Unable to connect to jump server")
        sys.exit(1)
    if result_dict['exit_status'] > 0:
        _print_warning_sting("linux command returned a non zero exit code. command output below:\n"+result_dict['out'])
    _print_message_string(result_dict['out'])
    if result_dict['out'].find(http_container_name) != -1:
        print "\n +++++++++++ http_proxy is running. validaing the status is active or stopped"
        container_status = re.search(r'\n(.*%s)'%http_container_name, result_dict['out'] )
        if not container_status:
            print "\n++++++++ Unable to get container status. exiting "
            return False,''
        container_status_list = container_status.group(1).split()
        if 'Exited' in container_status_list:
            _print_warning_sting("container is in stoped state. removing and starting container")
            result_flag,result = remove_and_start_http_proxy(env_details,http_container_name,True)
            if result_flag == True:
                return True,''
        if 'Up' in container_status_list:
            _print_message_string("containre already running")
            return True,''



        # result_flag, result = is_http_proxy_active(env_details,http_container_name)
        # if result_flag == True:
        #     return True,''
        # else:
        #     result_flag,result = 
    else:
        result_flag,result = remove_and_start_http_proxy(env_details,http_container_name)
        return True,''
    

def start_http_proxy(env_details):
    if env_details.test_app_list.has_key('http_proxy'):
        http_container_name = env_details.env_name +'_'+'http_proxy'
    else:
        _print_error_string("http proxy image details missing in app list. http proxy is required to run this test suite. exiting")
        return False, ''
    result_flag,result = is_http_proxy_running(env_details, http_container_name)
    if result_flag == True:
        return True,''


def set_test_bed(feature_name):
    import suite_setup
    print "\n+++++++++++++ setting environment details in a class object by initilizing it w.r.t env_name "
    env_details = PrepareSuiteData(suite_setup.env_name, feature_name)
    # if env_details.test_app_list.has_key('http_proxy'):
    #     http_container_name = env_details.env_name +'_'+'http_proxy'
    # else:
    #     _print_error_string("http proxy image details missing in app list. http proxy is required to run this test suite. exiting")
    #     return False, ''
    # print "\n+++++++++++++++++++ Checking http proxy container is running on jumpnode. container name -  "

    result_flag,result = start_http_proxy(env_details)
    # result_flag, result_dict = run_ssh_command(env_details, 'docker ps -a ')
    # if result_dict == False:
    #     _print_error_string("Unable to connect to jump server")
    #     sys.exit(1)
    # if result_dict['exit_status'] > 0:
    #     _print_warning_sting("linux command returned a non zero exit code. command output below:\n"+result_dict['out'])
    # if 
    # _print_message_string(result_dict['out'])


    # return env_obj


set_test_bed('infra')

# env_name = 'DEV'
# obj2 = environment.Environment()
# obj2.new_server = 'new_server'
# # obj2.set_environment(env_name)
# print obj2.maintainer_name, obj2.new_user, obj2.new_server, dir(obj2), dir(obj)


# Understanding scope fo instance variable
# name = ''
# class Test:
#     class_var_test = 'class var'
#     def fun1(self):
#         self.name = 'sandeep'
#         Test.class_var_test = 'class var updated inside any method'

#     def fun2(self):
#         title = 'singh'
#         self.fun1()
#         print self.name , title, Test.class_var_test #, class_var_test

# o = Test()
# o.fun2()