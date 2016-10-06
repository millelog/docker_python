# docker_python
Python scripts to help automate the managment of educational docker containers


usage: manage_class.py [-h] [-d DELETE_CLASS] [-a EXTENSION]
                       [--add_host NEW_HOST] [-r RESTART]
                       {create_class} ...

Command line interface to manage dockerized jupyterhub classes.

positional arguments:
  {create_class}        Information to create a new class container. Use
                        ./manage_class.py create_class -h for more info.

optional arguments:
  -h, --help            show this help message and exit
  -d DELETE_CLASS, --delete_class DELETE_CLASS
                        Delete a docker container from database and docker
                        daemon by name. Format: ./manage_class.py
                        --delete_class <class_name>
  -a EXTENSION, --add_extension EXTENSION
                        Add an ipython extension to Jupyterhub by name.
                        Format: ./manage_class.py --add_extension
                        <extension_name>
  --add_host NEW_HOST   Add a new hostname to the database of available hosts
                        and their ports. Format: ./manage_class.py --add_host
                        <host_name>
  -r RESTART, --restart RESTART
                        Stop everything inside of a container and then restart
                        all internal services properly. Format:
                        ./manage_users.py --restart <class_name>
                        


usage: manage_class.py create_class [-h] -c CLASS_NAME -r READABLE_NAME -f
                                    FIRST -l LAST -e EMAIL -u USER -n HOSTNAME
                                    -v VERSION -m MEM_LIMIT -s CPU_SHARE

optional arguments:
  -h, --help            show this help message and exit
  -c CLASS_NAME, --class_name CLASS_NAME
                        The name of the class as defined by the class
                        directory in /ACTF
  -r READABLE_NAME, --readable_nae READABLE_NAME
                        The full, human readable name for the class. Please
                        encapsulate with quotes if there are spaces.
  -f FIRST, --first FIRST
                        The instructor's first name.
  -l LAST, --last LAST  The instructor's last name.
  -e EMAIL, --email EMAIL
                        The instructor's email.
  -u USER, --user USER  The instructor's username.
  -n HOSTNAME, --hostname HOSTNAME
                        The local hostname of the machine that will run this
                        container.
  -v VERSION, --version VERSION
                        The version of the jupyterhub/actf docker image to
                        use.
  -m MEM_LIMIT, --mem_limit MEM_LIMIT
                        Memory limit for the container. Format:
                        [number][unit], unit = k, m or g.
  -s CPU_SHARE, --cpu_share CPU_SHARE
                        Number of weighted CPU shares to alot this class,
                        default is 1024 for even cpu division accross all
                        containers

