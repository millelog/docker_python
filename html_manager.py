import os
import class_database


def write_html_class(class_name, readable_name, instructor_first, instructor_last, instructor_email):
    html = '''

            <div class="alert">
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
                    </div>
                </div>
            </div>


'''.format(class_name=class_name, readable_name=readable_name, last=instructor_last, first=instructor_first, email=instructor_email)
    with open('/usr/share/nginx/html/index.html', 'a') as f:
        f.write(html)


def write_html_head():
    cmd='cat /usr/share/nginx/html/index.head > /usr/share/nginx/html/index.html'
    os.system(cmd)

def write_html_tail():
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
