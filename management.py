# this is a script to manage the server and the database
import sys
import subprocess
from time import sleep

sys.path.append('rpc_server')
sys.path.append('extraction')

# if the argument is collectdata, it will call the extraction module
# if the argument is startserver, it will call the server module
# declare the main with the argument
def main(arg):
    if arg == 'collectdata':
        from extraction import extraction as extr
        extr.data_extraction()
        
        from processing import processing as proc
        proc.processing()
    elif arg == 'startserver':
        from rpc_server import rpc_server as rpc
        rpc.start_rpc()
    elif arg == 'Todo':
        subprocess.Popen(['python', './management.py', 'startserver'])
        sleep(5)
        subprocess.Popen(['python', './pagina/manage.py', 'runserver'])
        sleep(5)
        subprocess.Popen(['streamlit', 'run', './pagina/frontend/pages/website.py'])
    else:
        print('invalid argument')
        print('please use collectdata or startserver')
        
if __name__ == '__main__':
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('invalid number of arguments')
        print('please use collectdata or startserver')
        print(' defaulting to startserver')
        main("collectdata")