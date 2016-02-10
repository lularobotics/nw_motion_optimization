#!/usr/bin/env python
######################################################################
# \file docker_tools.py
# \author Daniel Kappler
#######################################################################

######################################################################
# IMPORTANT
# since we need to run the output of this script in a shell for
# starting docker please do not print anything to the stdout
# unless you use Print_comment
######################################################################

import os
import sys
import argparse
import subprocess
import platform

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

######################################################################
# util functions
#######################################################################


def Print_comment(*args):
    print('# '+' '.join(map(str, args)))


def Print_separator():
    Print_comment(''.join(['-' for val in range(79)]))


def Execute_shell_script(cmd, blocking=True, print_stdout=False):
    if blocking:
        if print_stdout:
            p = subprocess.Popen(cmd, shell=True)
        else:
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        p.wait()
        return p
    p = subprocess.Popen(cmd, shell=True)
    return True


def Is_docker_running():
    cmd = 'docker info > /dev/null'
    p = Execute_shell_script(cmd)
    if p.returncode != 0:
        return False
    return True


def Remove_container(container_name):
    cmd = 'docker rm ' + container_name
    p = Execute_shell_script(cmd)
    if p.returncode != 0:
        return False
    return True


def Stop_running_container(run_container_name):
    cmd = 'docker stop '+run_container_name
    p = Execute_shell_script(cmd)
    if p.returncode != 0:
        return False
    return True


def Check_running_container(data_name):
    cmd = 'docker ps -f name='+data_name
    p = Execute_shell_script(cmd)
    output = p.stdout.read()
    # we check if our container name is metioned by docker output
    # if that is not the case we are done
    if data_name not in output:
        return False
    return Check_match(data_name, output.split('\n'))


def Check_container(data_name):
    cmd = 'docker ps -a -f name='+data_name
    p = Execute_shell_script(cmd)
    output = p.stdout.read()
    # we check if our container name is metioned by docker output
    # if that is not the case we are done
    if data_name not in output:
        return False
    return Check_match(data_name, output.split('\n'))


def Check_image(image_name):
    cmd = 'docker images'
    p = Execute_shell_script(cmd)
    output = p.stdout.read()
    # we check if our image name is metioned by docker output
    # if that is not the case we are done
    if image_name not in output:
        return False
    return Check_match(image_name, output.split('\n'))


def Check_match(value, list_of_strings):
    assert ' ' not in value, (
        'only strings without space are supported STRING={}'.format(value))
    for string in list_of_strings:
        # we check if this value is mentioned in this string
        if value in string:
            # it is mentioned now we want to make sure that we have
            # an exact match
            tmp = string.split(' ')
            # we get rid of all the empty spaces
            try:
                while True:
                    tmp.remove('')
            except ValueError:
                pass
            if value in tmp:
                # we have an exact match
                return True
    # no match was found
    return False

######################################################################
# setup functionality
#######################################################################

def Stop(image, container_name):
    if image is None:
        return False

    image_name = image['name']

    if not Check_image(image_name):
        Print_separator()
        Print_comment('image with name ' + image_name + 'does not exist')
        Print_separator()
        return True

    if Check_container(container_name):
        if Check_running_container(container_name):
            Print_separator()
            Print_comment('We stop the service now.')
            Print_separator()
            if not Stop_running_container(container_name):
                Print_separator()
                Print_comment('We could not stop the service')
                Print_separator()
                return False
        if not Remove_container(container_name):
            Print_separator()
            Print_comment('could not remove container ', container_name)
            Print_separator()
            return False
    return True

def Run(image, container_name, run_command):
    if image is None:
        return False

    image_name = image['name']

    if not Check_image(image_name):
        Print_separator()
        Print_comment('image with name ' + image_name + 'does not exist')
        Print_separator()
        return True

    if Check_container(container_name):
        if Check_running_container(container_name):
            Print_separator()
            Print_comment('The service is already started in a different terminal, we are stopping it now.')
            Print_separator()
            if not Stop_running_container(container_name):
                Print_separator()
                Print_comment('We could not stop the service')
                Print_separator()
                return False
        if not Remove_container(container_name):
            Print_separator()
            Print_comment('could not remove container ', container_name)
            Print_separator()
            return False

    cmd = 'docker run '
    cmd += ' ' + '--name ' + container_name
    cmd += ' --net=host'
    cmd += ' ' + image_name
    cmd += ' ' + '/bin/bash -c "' + run_command + '"'
    ###################################################################
    # this should actually be executed which is why we use
    # the normal print
    ###################################################################
    print(cmd)
    sys.exit(1)


def Get_script_directory():
    return os.path.realpath(os.path.dirname(sys.argv[0]))


def Get_system():
    system = platform.system()
    if system.lower() == 'linux':
        return 'linux'
    Print_comment('unsuported system '+system)
    sys.exit(-1)

def Print_docker_setup_message_linux():
    Print_comment("please make sure that docker is installed according")
    Print_comment("to the description https://docs.docker.com/linux/step_one")
    Print_comment("and that you are able to run docker ps")
    Print_comment("without an error appearing")

def Main():
    dir_path_script = Get_script_directory()
    file_path_default = os.path.join(dir_path_script, 'config.yaml')

    parser = argparse.ArgumentParser('docker tools to make creation simple')

    parser.add_argument(
        '--file-path-config',
        type=str,
        default=file_path_default,
        help='the default config file '+file_path_default)
    parser.add_argument(
        '--container',
        required=True,
        type=str,
        help='the run container name')
    parser.add_argument(
        '--run',
        type=str,
        help='the run command')
    parser.add_argument(
        '--stop',
        action='store_true',
        help='the stop a container')

    args = parser.parse_args()

    ######################################################################
    # IMPORTANT
    # since we need to run the output of this script in a shell for
    # starting docker please do not print anything to the stdout
    # unless you use Print_comment
    ######################################################################

    if not os.path.exists(args.file_path_config):
        Print_comment('file_path_config '+file_path_default+' does not exists')
        sys.exit(-1)
    if not os.path.isfile(args.file_path_config):
        Print_comment('file_path_config '+file_path_default+' is not a file')
        sys.exit(-1)
    if not os.path.isfile(args.file_path_config):
        Print_comment('file_path_config '+file_path_default+' is not a file')
        sys.exit(-1)
    try:
        with open(args.file_path_config, 'r') as fi:
            config = yaml.load(fi, Loader=Loader)
    except Exception as e:
        Print_comment(e.message + ' could not load ' + args.file_path_config)
        sys.exit(-1)

    system = Get_system()
    if not Is_docker_running():
        Print_separator()
        Print_comment('something is wrong with your docker setup')
        if system == 'linux':
            Print_docker_setup_message_linux()
            sys.exit(-1)

    if args.run != '':
        Print_separator()
        image = config['image']
        Print_comment('trying to load image ' + image['name'])
        Print_separator()
        if not Run(image, args.container, args.run):
            Print_separator()
            Print_comment('failed to load image ' + image['name'])
            Print_separator()
            sys.exit(-1)
    # in general we will exit normally
    sys.exit(0)

if __name__ == '__main__':
    Main()
