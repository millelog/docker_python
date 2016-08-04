import add_class as create
import class_database as data
import argparse

def parse_args():
	parser = argparse.ArgumentParser(desscription='Command line interface to manage dockerized jupyterhub classes.')
	parser.add_argument('-c', '--create_class', dest='class_info', nargs='+',
		help = "Create new Jupyterhub docker.\nFormat: python manage_class.py --create_class <class_name> <first> <last> <email> <username> <port> <version>")
	parser.add_argument('-d', '--delete_class', dest='delete_class',
		help = "Delete a docker container from database and docker daemon by name.\nFormat: python manage_class.py --delete_class <class_name>")
	parser.add_argument('-a', '--add_extension', dest='extension',
		help = "Add an ipython extension to Jupyterhub by name.\nFormat: python manage_class.py --add_extension <extension_name>")

def main():
	#parse args and get database
	args = parse.args()
	db = data.class_database()
	#If trying to create class
	if args.class_info and len(args.class_info == 7):
		info = args.class_info
		if all(create.valid_input(arg) for arg in info):
			create_class(args)
		else:
			print("Invalid input, please only use valid characters.")
	else:
		print("Invalid number of arguments.")
	#if removing class
	elif args.delete_class:
		if delete_class in db.get_class_names():
			create.delete_class(delete_class)
		else:
			print("Given class name is not in the database of active classes")
	elif args.extension:
		pass