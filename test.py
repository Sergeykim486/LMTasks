from db import Database
import os

dbname = os.path.dirname(os.path.abspath(__file__)) + "/Database/" + "lmtasksbase.db"
db = Database(dbname)

users = db.select_table('Users')
userlist = []
for line in users:
    userlist.append(line[0])
print(userlist)