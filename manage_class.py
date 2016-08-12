#!/usr/bin/env python3
import add_class as create
import class_database as data
import argparse

def parse_args():
        parser = argparse.ArgumentParser(description='Command line interface to manage dockerized jupyterhub classes.')
        parser.add_argument('-c', '--create_class', dest='class_info', nargs='+',
                help = "Create new Jupyterhub docker. Memory limit entered as a string i.e. 20G. version is either latest or v*.* \n Format: python manage_class.py --create_class <class_name> <first> <last> <email> <username> <host> <version> <memory_limit>")
        parser.add_argument('-d', '--delete_class', dest='delete_class',
                help = "Delete a docker container from database and docker daemon by name.\nFormat: python manage_class.py --delete_class <class_name>")
        parser.add_argument('-a', '--add_extension', dest='extension',
                help = "Add an ipython extension to Jupyterhub by name.\nFormat: python manage_class.py --add_extension <extension_name>")
        parser.add_argument('-n', '--add_host', dest='new_host',
                help = "Add a new hostname to the database of available hosts and their ports.\nFormat: python manage_class.py --add_host <host_name>")
        return parser.parse_args()


def create_class(args, db):
        info = {'class_name':args.class_info[0],
                'first':args.class_info[1],
                'last':args.class_info[2],
                'email':args.class_info[3],
                'user':args.class_info[4],
                'host':args.class_info[5],
                'port':db.get_first_available_port(args.class_info[5]),
                'version':args.class_info[6],
                'mem_limit':args.class_info[7]
                }	
        create.create_class(info)
        db.insert_class(info['host'], info['port'], info['class_name'], info['user'], info['first'], info['last'], info['email'])
        print("inserted into db")

def add_host(args, db):
        db.populate_port_table(args.new_host)

def delete_class(args, db):
        create.delete_class(args.delete_class)
        db.remove_class(args.delete_class)
        print("Class "+args.delete_class+" was successfully deleted from the database and the docker container was removed.")

def main():
        #parse args and get database
        args = parse_args()
        db = data.class_database()
        #If trying to create class
        if args.class_info:
                if len(args.class_info) == 8:
                        if all(create.valid_input(arg) for arg in args.class_info):
                                if args.class_info[5] in db.get_unique_hosts():
                                        create_class(args, db)
                                else:
                                        print("That is not a valid host name. use the -h flag to add new hosts to the database.")
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
                                delete_class(args, db)
                                found = True
                if not found:
                        print("Name not found in the database of classes")
        #if adding new host
        elif args.new_host:
                #TODO add valid format check?
                add_host(args, db)

        #TODO
        elif args.extension:
                pass

if __name__=='__main__':
        main()
