#!/usr/bin/env python3
'''This is the main file that is meant to interface with the user. Through it you can create new docker containers, 
delete or restart an existing container, and add a new host machine to the host/port database.'''
import add_class as create
import class_database as data
import argparse
from docker import Client
import html_manager
import logger
import subprocess


def parse_args():
        '''Set up all of the possible options for argparse, including how to take their input from the command line and the info to display the main help message.'''
        parser = argparse.ArgumentParser(description='Command line interface to manage dockerized jupyterhub classes.')
        subparser = parser.add_subparsers(help = 'Information to create a new class container. Use ./manage_class.py create_class -h for more info.');
        new_class = subparser.add_parser('create_class');
        new_class.add_argument('-c', '--class_name', dest='class_name', required=True,
                help = "The name of the class as defined by the class directory in /ACTF")
        new_class.add_argument('-r', '--readable_nae', dest='readable_name', required=True,
                help = "The full, human readable name for the class. Please encapsulate with quotes if there are spaces.")
        new_class.add_argument('-f', '--first',  dest='first', required=True,
                help = "The instructor's first name.")
        new_class.add_argument('-l', '--last', dest='last', required=True,
                help = "The instructor's last name.")
        new_class.add_argument('-e', '--email', dest='email', required=True,
                help = "The instructor's email.")
        new_class.add_argument('-u', '--user', dest='user', required=True,
                help = "The instructor's username.")
        new_class.add_argument('-n', '--hostname', dest='hostname', required=True,
                help = "The local hostname of the machine that will run this container.")
        new_class.add_argument('-v', '--version', dest='version', required=True,
                help = "The version of the jupyterhub/actf docker image to use.")
        new_class.add_argument('-m', '--mem_limit', dest='mem_limit', required=True,
                help = "Memory limit for the container. Format: [number][unit], unit = k, m or g.")
        new_class.add_argument('-s', '--cpu_share', dest='cpu_share', required=True,
                help = "Number of weighted CPU shares to alot this class, default is 1024 for even cpu division accross all containers")
        parser.add_argument('-d', '--delete_class', dest='delete_class', 
                help = "Delete a docker container from database and docker daemon by name.\nFormat: ./manage_class.py --delete_class <class_name>")
        parser.add_argument('-a', '--add_extension', dest='extension',
                help = "Add an ipython extension to Jupyterhub by name.\nFormat: ./manage_class.py --add_extension <extension_name>")
        parser.add_argument('--add_host', dest='new_host',
        	help = "Add a new hostname to the database of available hosts and their ports.\nFormat: ./manage_class.py --add_host <host_name>")
        #parser.add_argument('-u', '--add_user', dest='user_info', nargs='+',
                #help = "Create a new Jupyter user. Group = instructor or student. \nFormat: ./manage_users.py --add_user <class_name> <first> <last> <USER> <email> <group>")
        parser.add_argument('-r', '--restart', dest='restart',
                help = "Stop everything inside of a container and then restart all internal services properly. \nFormat: ./manage_users.py --restart <class_name>")
        return parser.parse_args()


def create_class(args, db, cli):
        '''Create a new container for a class with the information gathered by parse_args(). 
        This function creates a new dictionary out of the arguments, passes them to add_class.py to create a new docker container, 
        adds the class to our database and updates the html for the landing page to include the new class.'''
        #Convert the arguments to a relevant dictionary because that's how I did it ¯\_(ツ)_/¯
        info = {'class_name':args.class_name,
                'readable_name':args.readable_name,
                'first':args.first,
                'last':args.last,
                'email':args.email,
                'user':args.user,
                'host':args.hostname,
                'jupyter_port':db.get_first_available_port(args.hostname),
                'r_port':db.get_first_available_port(args.hostname),
                'docu_port':db.get_first_available_port(args.hostname),
                'version':args.version,
                'mem_limit':args.mem_limit,
                'cpu_shares':args.cpu_share
                }
        if(all(create.valid_input(arg) for arg in info)):
                create.create_class(info, cli)
                #Update the class database with the new class
                db.insert_class(info['host'], info['jupyter_port'], info['class_name'], info['readable_name'], info['user'], info['first'], info['last'], info['email'])
                #Update the json objects that the front end uses to populate its dynamic content from the database
                html_manager.update_json()
                html_manager.update_class_info();
                #start/restart nginx
                try:
                        create.subprocess.check_output(['service', 'nginx', 'restart'])
                except:
                        create.subprocess.check_output(['service','nginx', 'start'])
                print("inserted into db")
        else:
                print("Invalid character(s) in the class information. Please only use valid characters.")

def add_host(args, db):
        '''Adds a new host to the port/host table and makes ports 8000-8100 under that hostname available to create_class() as a valid place to host internal jupyter/rstudio servers. 
        It then restarts nginx.'''
        #add ports 8001-8100 of the given host name to the port table of the database 
        db.populate_port_table(args.new_host)
        create.subprocess.check_output(['systemctl', 'restart', 'nginx'])

def delete_class(args, db, cli):
        '''If the container given to argparse exists this function will delete that container, remove it from the database of classes, and updates the html to reflect the database change.'''
        try:
                create.delete_class(args.delete_class, cli)
        except:
                print("Container does not exist")
        try:
                db.remove_class(args.delete_class)
        except:
                print("That class is not in the database")
        html_manager.update_json()
        html_manager.update_class_info()
        subprocess.check_output("docker rm -f "+args.delete_class, stderr=subprocess.STDOUT, shell=True)
        print("Class "+args.delete_class+" was successfully deleted from the database and the docker container was removed.")

def create_user(user_info, cli):
        '''Creates a new user inside of a given container with the credentials given on the command line. Depreciated by NIS.'''
        command = 'python3 /home/public/data/jupyter_python/manage_users.py --add_user '+user_info[1]+' '+user_info[2]+' '+user_info[3]+' '+user_info[4]+' '+user_info[5]+' True'
        create_user = cli.exec_create(container=user_info[0], cmd = command)
        print(cli.exec_start(create_user.get('Id')))

def restart_class(name, cli):
        '''Restart the entire docker container and turn back on the jupyterhub, rstudio and NIS clients inside of it.'''
        cli.restart(container=name)
        create.start_jupyterhub(cli, name)
        create.start_rstudio(cli, name)
        create.start_ypbind(cli, name)
        logger.log(" "+name+" was restarted and all process were resumed")

def main():
        '''This ensures that any arguments passed in by argparse have a valid syntax and are able to be passed to their corresponding functions without error. 
        This function also instantiates a parsed argparse object, a database object and a docker client object to be used by the functions in manage_class.py.'''
        #parse args get database and connec to docker daemon
        args = parse_args()
        db = data.class_database()
        cli = Client(base_url='unix://var/run/docker.sock')
        #If trying to create class
        if hasattr(args, 'class_name'):
                #If the host exists in the ports table
                if args.hostname in db.get_unique_hosts():
                        create_class(args, db, cli)
                else:
                        print("That is not a valid host name. use -h for help with adding new hostnames.")
        #if removing class
        elif args.delete_class:
                #I hate using these types of variables, wtb python lessons
                found = False
                for name in db.get_class_names()['name']:
                        if name == args.delete_class:
                                delete_class(args, db, cli)
                                found = True
                if not found:
                        print("Name not found in the database of classes")
        #if adding new host
        elif args.new_host:
                #TODO add valid format check?
                add_host(args, db)
        #Add a user inside the designated docker container
        #elif args.user_info:
        #        if len(args.user_info) == 6:
        #                if all(create.valid_input(arg) for arg in args.user_info):
        #                        if args.user_info[0] in db.get_class_names():
        #                                create_user(args.user_info, cli)
        #                        else:
        #                                print("That is not a valid class name")
        #                else:
        #                        print("Invalid character(s)")
        #        else:
        #                print("Invalid number of arguments")

        #TODO
        elif args.extension:
                pass
        #if you're restarting a class container
        elif args.restart:
                found = False
                for name in db.get_class_names():
                        if name == args.restart:
                                restart_class(args.restart, cli)
                                found = True
                if not found:
                        print("Name not found in the database of classes")


if __name__=='__main__':
        main()
