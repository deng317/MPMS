import os

db_user = os.environ.get("DB_USR")
db_passwd = os.environ.get("DB_PASSWD")

print(db_user)
print(db_passwd)
