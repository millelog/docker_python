#!/usr/bin/env python3
import add_class as create
import class_database as data
import argparse
from docker import Client
import html_manager
import logger

def parse_args():
        parser = argparse.ArgumentParser(description='Command line interface to manage dockerized jupyterhub classes.')
        parser.add_argument('-c', '--create_class', dest='class_info', nargs='+',
                help = "Create new Jupyterhub docker. Memory limit [number][unit], units = k, m or g, e.g. 20G. Number of weighted CPU shares, set to 1024 for default. class_name is the abbreviated name of the class with no spaces, readable name is the name of the class you want displayed and must be placed in quotes. version is either latest or v*.* \n Format: ./manage_class.py --create_class <class_name> \"<readable_name>\" <first> <last> <email> <username> <host> <version> <memory_limit> <cpu_shares>")
        parser.add_argument('-d', '--delete_class', dest='delete_class',
                help = "Delete a docker container from database and docker daemon by name.\nFormat: ./manage_class.py --delete_class <class_name>")
        parser.add_argument('-a', '--add_extension', dest='extension',
                help = "Add an ipython extension to Jupyterhub by name.\nFormat: ./manage_class.py --add_extension <extension_name>")
        parser.add_argument('-n', '--add_host', dest='new_host',
        	help = "Add a new hostname to the database of available hosts and their ports.\nFormat: ./manage_class.py --add_host <host_name>")
        parser.add_argument('-u', '--add_user', dest='user_info', nargs='+',
                help = "Create a new Jupyter user. Group = instructor or student. \nFormat: ./manage_users.py --add_user <class_name> <first> <last> <USER> <email> <group>")
        parser.add_argument('-r', '--restart', dest='restart',
                help = "Stop everything inside of a container and then restart all internal services properly. \nFormat: ./manage_users.py --restart <class_name>")
        return parser.parse_args()


def create_class(args, db, cli):
        #Convert the arguments to a relevant dictionary because that's how I did it ¯\_(ツ)_/¯
        info = {'class_name':args.class_info[0],
                'readable_name':args.class_info[1],
                'first':args.class_info[2],
                'last':args.class_info[3],
                'email':args.class_info[4],
                'user':args.class_info[5],
                'host':args.class_info[6],
                'jupyter_port':db.get_first_available_port(args.class_info[6]),
		'r_port':db.get_first_available_port(args.class_info[6]),
                'version':args.class_info[7],
                'mem_limit':args.class_info[8],
                'cpu_shares':args.class_info[9]
                }	
        create.create_class(info, cli)
        #Update the class database with the new class
        db.insert_class(info['host'], info['jupyter_port'], info['class_name'], info['readable_name'], info['user'], info['first'], info['last'], info['email'])
        #Update the index.html for nginx with this new database
        html_manager.update_html()
        #start/restart nginx
        try:
                create.subprocess.check_output(['service', 'nginx', 'restart'])
        except:
                create.subprocess.check_output(['service','nginx', 'start'])
        print("inserted into db")

def add_host(args, db):
        #add ports 8001-8100 of the given host name to the port table of the database 
        db.populate_port_table(args.new_host)
        create.subprocess.check_output(['systemctl', 'restart', 'nginx'])

def delete_class(args, db, cli):
        try:
                create.delete_class(args.delete_class, cli)
        except:
                print("Container does not exist")
        try:
                db.remove_class(args.delete_class)
        except:
                print("That class is not in the database")
        html_manager.update_html()
        print("Class "+args.delete_class+" was successfully deleted from the database and the docker container was removed.")

def create_user(user_info, cli):
        command = 'python3 /home/public/data/jupyter_python/manage_users.py --add_user '+user_info[1]+' '+user_info[2]+' '+user_info[3]+' '+user_info[4]+' '+user_info[5]+' True'
        create_user = cli.exec_create(container=user_info[0], cmd = command)
        print(cli.exec_start(create_user.get('Id')))
	
def restart_class(name, cli):
        cli.restart(container=name)
        create.start_jupyterhub(cli, name)
        create.start_rstudio(cli, name)
        create.start_ypbind(cli, name)
        logger.log(" "+name+" was restarted and all process were resumed")

def main():
        #parse args get database and connec to docker daemon
        args = parse_args()
        db = data.class_database()
        cli = Client(base_url='unix://var/run/docker.sock')
        #If trying to create class
        if args.class_info:
                #if the correct number of arguments
                if len(args.class_info) == 10:
                        #If all arguments use valid characters
                        if all(create.valid_input(arg) for arg in args.class_info):
                                #If the host exists in the ports table
                                if args.class_info[6] in db.get_unique_hosts():
                                        create_class(args, db, cli)
                                else:
                                        print("That is not a valid host name. use -h for help with adding new hostnames.")
                        else:
                                print("Invalid input, please only use valid characters.")
                else:
                        print("Invalid number of arguments.")
        #if removing class
        elif args.delete_class:
                #I hate using these types of variables, wtb python lessons
                found = False
                for name in db.get_class_names():
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
        elif args.user_info:
                if len(args.user_info) == 6:
                        if all(create.valid_input(arg) for arg in args.user_info):
                                if args.user_info[0] in db.get_class_names():
                                        create_user(user_info, cli)
                                else:
                                        print("That is not a valid class name")
                        else:
                                print("Invalid character(s)")
                else:
                        print("Invalid number of arguments")

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
