from docker import Client
import class_database as data
import argparse

def parse_args():
        parser = argparse.ArgumentParser(description='Create a new dockerized jupyterhub teaching interface')
        parser.add_argument('-n', dest='class_name', required=True,
                help = "Name of the class")
        parser.add_argument('-f', dest='first', required=True,
                help = "Instructor's first name")
        parser.add_argument('-l', dest='last', required=True,
                help = "Instrucotr's last name")
        parser.add_argument('-e', dest='email', required=True,
                help = "Instructor's email")
        parser.add_argument('-u', dest='user', required=True,
                help = "Instructor's username")
        parser.add_argument('-p', dest='port', required=True,
                help = "Host's port to map the docker to.")
        parser.add_argument('-v', dest='version', required=True,
                help="Version number of the jupyterhub/cgrb image.")
        return parser.parse_args()

def create_class(args):
        cli = Client(base_url='unix://var/run/docker.sock')
        #Create a container that mounts the given volumes and ports and sets resource limits
        container = cli.create_container(image='jupyterhub/actf:'+args['version'],
                        command='/bin/bash',
                        name=args['class_name'], ports=[8000],
                        volumes= ['/home','/srv/cgrb', '/local/cluster'],
                        host_config=cli.create_host_config(
                                port_bindings={8000:args['port']}, 
                                binds={
                                        '/local/cluster':{
                                                'bind': '/local/cluster',
                                                'mode': 'ro',
                                        }
                                }, mem_limit=args['mem_limit']
                        ), stdin_open=True, detach=True)

        response = cli.start(container=container.get('Id'))
        print(response)

        #Run the command and print the response returned, Creates initial user
        print(create_instrucotr(cli, args))

        #Run the command to add a line to the jupytehrub config file and print response
        config_line = 'c.Application.base_url = \'/'+args['class_name']+'/\''
        print(add_to_config(cli, args['class_name'], config_line)) 

        #Run the command to start the server and print the response
        print(start_jupyterhub(cli, args['class_name'])

        #Commit the class creation to database
        database_commit(args['port'], args['class_name'], args['user'])

def start_jupyterhub(cli, container_name):
        class_start = cli.exec_create(container=args['class_name'], cmd = 'jupyterhub --no-ssl')
        return(cli.exec_start(class_start.get('Id'), detach=True))

def add_to_config(cli, container_name, config_line):
        config_line = 'c.Application.base_url = \'/'+container_name+'/\''
        edit_config = cli.exec_create(container=container_name,
                cmd = 'echo '+config_line+' >> /srv/jupyterhub_config.py')
        return cli.exec_start(edit_config.get('Id'))


def create_instructor(cli, args):
        create_user = cli.exec_create(container=args['class_name'], cmd =\
         '/opt/anaconda/bin/python /home/public/data/jupyter_python/manage_users.py -a '+\
        args['first']+' '+args['last']+' '+args['user']+' '+args['email']+' instructor True')
        return cli.exec_start(create_user.get('Id'))


def delete_class(name):
    cli = Client(base_url='unix://var/run/docker.sock')
    cli.stop(container=name)
    cli.remove_container(container=name, v=False)


def database_commit(port, class_name, instructor):
        db = data.class_database()
        db.insert_class(port, class_name, instructor)

def valid_input(input_string):
        valid_string = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@._ \''
        for char in input_string:
            if char not in valid_string:
                return False
        if not input_string:
            return False
        return True

def valid_parser(args):
        return valid_input(args.class_name) and\
           valid_input(args.first) and\
           valid_input(args.last) and\
           valid_input(args.email) and\
           valid_input(args.user) and\
           valid_input(args.port) and\
           valid_input(args.version)

def main():
        print("Depreciated by manage_class.py")

if __name__=='__main__':
        main()
