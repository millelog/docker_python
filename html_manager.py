import os
import json
import class_database

def update_json():
    """Updates nginx’s index.html so that the class list on the webpage accurately reflects what the actual class list in the database is. 
    This is called everytime a container is created or destroyed by manage_class.py."""
    #Connect to database
    db = class_database.class_database()
    #Get the class names in the database
    classes = db.get_class_names()
    #add each class to this page
    with open('/usr/share/nginx/html/public/class_list.json', 'w') as outfile:
        json.dump(classes, outfile);
    #close all html things
    print("Index.html has been updated to match the database of classes")

def update_class_info():
    db = class_database.class_database()
    class_names = db.get_class_names()['name'];
    classes = dict()
    for name in class_names:
        this_class = {name:dict()}
        classes.update(this_class);
    for name in class_names:
        classes[name] = db.get_instructor_info(name);
    with open('/usr/share/nginx/html/class_info.json', 'w') as outfile:
        json.dump(classes, outfile);
    print("class_info.json has been update");

