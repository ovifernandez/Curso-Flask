import os	

#AQUI VAN LOS PARAMETROS DE CONFIGYRACION DE LA APLICACION

secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
PWD = os.path.abspath(os.curdir)	

DEBUG = True

# --- EL RESTO DE TUS CONFIGURACIONES ---
SQLALCHEMY_TRACK_MODIFICATIONS = False

SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://ovifernandez:PU@adjYjk@t^*jQe0cYU@ovifernandez.mysql.pythonanywhere-services.com/ovifernandez$tienda'