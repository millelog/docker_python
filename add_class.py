'''This file is used by the manage_class.py file to both create new docker containers and delete existing containers based off of the information gathered by manage_class.py.'''
from docker import Client
import class_database as data
import subprocess


def create_class(args, cli): 
        '''This is the main function of add_class.py and utilizes most of the other functions defined within it. 
        This function uses the docker-py API to create a docker container based on the class information passed by args. 
        It then executes a series of necessary configuration steps both inside and outside of the container.'''
        #Create a container that mounts the given volumes and ports and sets resource limits
        container = cli.create_container(image='cgrb/actf:'+args['version'],
                        #Default command of the container so that it will always have a process running
                        command='/usr/sbin/init',
                        #name of the container and the ports to forward to the host's ports
                        name=args['class_name'], ports=[8000, 8080, 8787],
                        #Hostname for command line aesthetics
                        hostname=args['class_name']+'_host',
                        #Directories to store outside of the container in case of container failure
                        volumes= ['/home','/srv/cgrb', '/local/cluster', '/ACTF', '/etc/yp.conf', '/etc/sysconfig/network', '/etc/nsswitch.conf', '/sys/fs/cgroup'],
                        host_config=cli.create_host_config(
                                #Bind the container's 8000 port to the variable host port based on availability
                                port_bindings={8000:int(args['jupyter_port']), 8080:int(args['docu_port']), 8787:int(args['r_port'])}, 
                                #Mount the nfs1 and local cluster for access to its bin
                                binds=[
                                        '/local/cluster:/local/cluster:ro',
                                        '/ACTF:/ACTF:rw',
                                        '/etc/yp.conf:/etc/yp.conf:ro',
                                        '/etc/sysconfig/network:/etc/sysconfig/network:ro',
                                        '/etc/nsswitch.conf:/etc/nsswitch.conf:ro',
                                        '/sys/fs/cgroup:/sys/fs/cgroup:ro'
                                ],
                                #NIS secruity options
                                security_opt=['seccomp=unconfined'],
                                cap_add=["SYS_ADMIN"], 
                                #Set resource limits for the container
                                mem_limit=args['mem_limit']),
                        environment=['container=docker'],
                        cpu_shares=int(args['cpu_shares']),
                        stdin_open=True, detach=True) #These allow the container to continue to run in the background)<--this paranthesis man... first time a comments made a bug...

        cli.start(container=container.get('Id'))

        

        #Run the command to add a line to the jupytehrub config file and print response
        #print(add_base_url(cli, args['class_name'])) 

        #Add the class name to the group whitelist for nis compatability
        print(add_group_whitelist(cli, args['class_name']))

        #set up the custom html to add the eula and logo/title
        #add_html_title(cli, args['class_name'], args['readable_name'])
        
        #Add the home directory for the class to the jupyterhub configuration
        print(add_home_directory(cli, args['class_name']))

        #Start the ypbind daemon for NIS mount
        print(start_ypbind(cli, args['class_name']))

        #Run the command to start the server and print the response
        print(start_jupyterhub(cli, args['class_name']))

        #Start the Rstudio server
        print(start_rstudio(cli, args['class_name']))

        #Add the nginx configuration for r studio server
        r_config = get_nginx_r_config(args['host'], args['r_port'], args['class_name'])

        #Add the path to the class to nginx configuration
        j_config = get_nginx_jupyter_config(args['host'], args['jupyter_port'], args['class_name'])
        
        #Update the config with these strings
        write_nginx_config(args['class_name'], j_config, r_config)

def add_html_title(cli, container_name, readable_name):
        '''Adds the name of the container to the html page template for Jupyter. Currently not functioning and is never called.'''
        cat_head = cli.exec_create(container=container_name, cmd = 'bash -exec \'cat /root/downloads/jupyter_config/page.html.head > /usr/share/jupyter/hub/templates/page.html\'')
        enter_title=cli.exec_create(container=container_name, cmd = 'bash -exec \'echo "  <h4 align=center>{container_name}</h4>" >> /usr/share/jupyter/hub/templates/page.html\''.format(container_name=readable_name))
        cat_tail = cli.exec_create(container=container_name, cmd = 'bash -exec \'cat /root/downloads/jupyter_config/page.html.tail >> /usr/share/jupyter/hub/templates/page.html\'')
        cli.exec_start(cat_head.get('Id'))
        cli.exec_start(enter_title.get('Id'))
        cli.exec_start(cat_tail.get('Id'))


def start_jupyterhub(cli, container_name):
        '''Starts the jupyterhub client within the docker with the command line flags to disable to the need for ssl, 
        sets the base url of the jupyter server to match what nginx is expecting and forces the uploaded configuration file to be used.'''
        class_start = cli.exec_create(container=container_name, cmd = 'jupyterhub --no-ssl --base-url='+container_name+'/jupyter -f \'/srv/jupyterhub_config.py\'')
        return cli.exec_start(class_start.get('Id'), detach=True)

def start_rstudio(cli, container_name):
        '''Starts the rstudio server within the docker container by directly calling the rserver executable.'''
        r_start = cli.exec_create(container=container_name, cmd = '/usr/lib/rstudio-server/bin/rserver')
        return cli.exec_start(r_start.get('Id'), detach=True)

def start_ypbind(cli, container_name):
        '''Starts the ypbind service within the container so that the NIS users can be used as users within the container.'''
        ypbind = cli.exec_create(container=container_name, cmd = 'systemctl start ypbind')
        return cli.exec_start(ypbind.get('Id'))

def add_base_url(cli, container_name):
    """add the line to the jupyterhub config that allows the nginx to route to the container correctly"""
    edit_config = cli.exec_create(container=container_name,
        cmd = 'bash -exec \'echo c.Application.base_url = \\\"/%s/jupyter\\\" >> /srv/jupyterhub_config.py\'' % (container_name, ))
    return cli.exec_start(edit_config.get('Id'))
    
def add_home_directory(cli, container_name):
        '''Adds a line to the configuration file of jupyterhub within the container to set the location of the home directory to the corresponding class file on /ACTF.'''
        add_home = cli.exec_create(container=container_name,
            cmd='bash -exec \'echo c.Spawner.notebook_dir = \\\"/ACTF/{container_name}\\\" >> /srv/jupyterhub_config.py\''.format(container_name=container_name))
        return cli.exec_start(add_home.get('Id'))

def add_group_whitelist(cli, container_name):
        '''Adds users that belong to either the group with the name of the container or the cgrb group to jupyterhub’s authentication whitelist.'''
        add_group = cli.exec_create(container=container_name,
            cmd='bash -exec \'echo c.localAuthenticator.group_whitelist = set\(\\\"{container_name}\\\", \\\"cgrb\\\"\) >> /srv/jupyterhub.config.py\''.format(container_name=container_name))
        return cli.exec_start(add_group.get('Id'))

def create_instructor(cli, args):
    '''Creates a user within the container by calling the manage_users.py script and passing it the information from arg parser. 
    This function was deprecated by the addition of NIS users.'''
    create_user = cli.exec_create(container=args['class_name'], cmd =\
        '/opt/anaconda/bin/python /home/public/data/jupyter_python/manage_users.py -a '+\
    args['first']+' '+args['last']+' '+args['user']+' '+args['email']+' instructor True')
    return cli.exec_start(create_user.get('Id'))

def write_nginx_config(class_name, jupyter, r_studio):
    '''Creates a new nginx configuration file outside of the container and adds the necessary configuration as dictated by the jupyter and r_studio strings.'''
    with open('/etc/nginx/conf.d/classes/{class_name}.conf'.format(class_name=class_name), 'w') as f:
        f.write(r_studio+"\n\n\n"+jupyter);

def get_nginx_jupyter_config(host, port, class_name):
    """Add the relevant configuration details for this container to the nginx configuration directory"""
    config_file="""location ~* /{class_name}/jupyter(/.+)? {{
        proxy_pass http://{host}:{port};
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header Host $host; # necessary
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-NginX-Proxy true;
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade; # necessary
        proxy_set_header Connection $connection_upgrade; # necessary
        proxy_read_timeout 86400;
    }}""".format(class_name=class_name, host=host, port=port)

    return config_file

def get_nginx_r_config(host, port, class_name):
    '''Takes the networking information about the class and returns a string of valid nginx configuration settings for rstudio.'''
    config_lines="""location /{class_name}/rstudio/ {{
        rewrite ^/{class_name}/rstudio/(.*)$ /$1 break;
        proxy_pass http://{host}:{port};
        proxy_redirect http://{host}:{port}/ $scheme://$host/{class_name}/rstudio/;
        #Web socket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade; # necessary
        proxy_set_header Connection $connection_upgrade; # necessary
        proxy_read_timeout 86400;
    }}""".format(class_name=class_name, host=host, port=port)

    return config_lines

def delete_class(name, cli):
    '''Deletes the class container that matches the given name and removes all a associated configuration files from nginx as well.'''
    #delete the container
    cli.stop(container=name)
    cli.remove_container(container=name)
    #Delete the ngnix config file 
    path = "/etc/nginx/conf.d/classes/{class_name}.conf".format(class_name=name)
    subprocess.check_output(["rm", "-f", path])
    
def valid_input(input_string):
    '''Determines if the given input_string is of a valid format to be accepted as input for a new class or user.
    A valid format means it only contains letters, numbers, @s, periods, underscores, spaces or apostrophes.'''
    valid_string = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@._ \''
    for char in input_string:
        if char not in valid_string:
            return False
    if not input_string:
        return False
    return True


def main():
        print("Depreciated by manage_class.py")

if __name__=='__main__':
        main()
