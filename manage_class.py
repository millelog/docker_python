#!/usr/bin/env python3
import add_class as create
import class_database as data
import argparse

def parse_args():
        parser = argparse.ArgumentParser(description='Command line interface to manage dockerized jupyterhub classes.')
        parser.add_argument('-c', '--create_class', dest='class_info', nargs='+',
                help = "Create new Jupyterhub docker. Port is the port that the docker container will be mapped to on the host. Memory limit entered as a string i.e. 20G. version is either latest or v*.* \n Format: python manage_class.py --create_class <class_name> <first> <last> <email> <username> <port> <version> <memory_limit>")
        parser.add_argument('-d', '--delete_class', dest='delete_class',
                help = "Delete a docker container from database and docker daemon by name.\nFormat: python manage_class.py --delete_class <class_name>")
        parser.add_argument('-a', '--add_extension', dest='extension',
                help = "Add an ipython extension to Jupyterhub by name.\nFormat: python manage_class.py --add_extension <extension_name>")
        return parser.parse_args()


def create_class(args):
        info = {'class_name':args.class_info[0],
                'first':args.class_info[1],
                'last':args.class_info[2],
                'email':args.class_info[3],
                'user':args.class_info[4],
                'port':args.class_info[5],
                'version':args.class_info[6],
                'mem_limit':args.class_info[7]
                }
        create.create_class(info)
        data.insert_class(info['port'], info['class_name'], info['user'])

def delete_class(args):
        create.delete_class(args.delete_class)
        data.remove_class(args.delete_class)


def main():
        #parse args and get database
        args = parse_args()
        db = data.class_database()
        #If trying to create class
        if args.class_info:
                if len(args.class_info) == 8:
                        if all(create.valid_input(arg) for arg in args.class_info):
                                create_class(args)
                        else:
                                print("Invalid input, please only use valid characters.")
                else:
                        print("Invalid number of arguments.")
        #if removing class
        elif args.delete_class:
                if delete_class in db.get_class_names():
                        delete_class(args)
                else:
                        print("Given class name is not in the database of active classes")
        elif args.extension:
                pass

if __name__=='__main__':
        main()
