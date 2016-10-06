import os
import class_database


def write_html_class(class_name, readable_name, instructor_first, instructor_last, instructor_email):
    """Creates a string of html that contains the class information that is passed to this function. 
    This html string is then written to the index.html of the main landing page to append the current list of classes there"""
    html = '''

            <div class="alert">
<<<<<<< HEAD
                <h2>{readable_name} with {first} {last} ({email})</h2>
                <div class="content">
                    <div class='imagelinks'>
                        <a href="https://jupyter.cgrb.oregonstate.edu/{class_name}/jupyter"><img
                            src="images/jupyter-logo.png"
                            alt=" Jupyter "
                            width='166' height='40'/></a>
                        <a href="https://jupyter.cgrb.oregonstate.edu/{class_name}/rstudio"><img
                            src='images/rstudio-logo.png'
                            alt=" R Studio "
                            width='115' height='40'/></a>
=======
                <h2>{readable_name}  -- {last}, {first}  -- Email: {email}</h2>
                <div class="content">
                    <div class='imagelinks'>
                        <a href="http://jupyter.cgrb.oregonstate.edu/{class_name}/jupyter"><img
                            src="images/jupyter-logo.png"
                            alt=" Jupyter "
                            width='270' height='65'/></a>
                        <a href="http://jupyter.cgrb.oregonstate.edu/{class_name}/rstudio"><img
                            src='images/rstudio-logo.png'
                            alt=" R Studio "
                            width='185' height='65'/></a>
>>>>>>> 083ac187920a7733c37f36ae876abec2c223698d
                    </div>
                </div>
            </div>


'''.format(class_name=class_name, readable_name=readable_name, last=instructor_last, first=instructor_first, email=instructor_email)
    with open('/usr/share/nginx/html/index.html', 'a') as f:
        f.write(html)


def write_html_head():
    """A function that copies all of the html before the list of classes back into the index.html when it is updated by this module."""
    cmd='cat /usr/share/nginx/html/index.head > /usr/share/nginx/html/index.html'
    os.system(cmd)

def write_html_tail():
    """Contains a hardcoded string of html that is meant to create the final logo at the bottom of the page and wrap up the html tags."""
    tail='''            <div class="logos">
                <a href="cgrb.oregonstate.edu"><img
                    src="images/cgrb-small-logo-transparent.png" 
                    alt="[ Oregon State University ]"
                    width="270" height="53" /></a>

            </div>
        </div>
    </body>
</html>'''


    with open('/usr/share/nginx/html/index.html', 'a') as f:
       f.write(tail)

def update_html():
    """Updates nginx’s index.html so that the class list on the webpage accurately reflects what the actual class list in the database is. 
    This is called everytime a container is created or destroyed by manage_class.py."""
    #Connect to database
    db = class_database.class_database()
    #Get the class names in the database
    classes = db.get_class_names()
    #Wrate the beginning of the main html page
    write_html_head()
    #add each class to this page
    for name in classes:
        #Get the instructors info
        info = db.get_instructor_info(name)
        #Write the html for each class
        write_html_class(name, info['class_name'], info['first'], info['last'], info['email'])
    #close all html things
    write_html_tail()
    print("Index.html has been updated to match the database of classes")
