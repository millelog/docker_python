#!/bin/bash
./manage_class.py -n jupyter.cgrb.oregonstate.local
./manage_class.py -c classA first1 last1 email1@email.com user1 jupyter.cgrb.oregonstate.local latest 16G 1024
./manage_class.py -c classB first2 last2 email2@email.com user2 jupyter.cgrb.oregonstate.local latest 16G 1024
./manage_class.py -c classC first3 last3 email3@email.com user3 jupyter.cgrb.oregonstate.local latest 16G 1024
