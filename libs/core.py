import os
import subprocess

import util

class EnviromentIsNone(Exception):

    def __init__(self, arg):
        pass

    def __str__(self):
        return 'Enviroment needed.'
        

class CommunicationInterruptions(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'Interruptions happend when connented to %s.' % (self.value,)

class CommandNotFound(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return 'Command %s not found.' % self.value

class ScriptTool:

    def __init__(self,command = 'node -v'):
        if not subprocess.call(command, stdout=open(os.devnull, 'w'), stderr=open(os.devnull, 'w'), shell=False):
            pass
        else:
            raise CommandNotFound(command)

    def run_script(self,credential):
        if os.path.isfile(credential):
            result = subprocess.check_output('node '+credential,shell=True)
            os.remove(credential)
        else:
            temp_folder = util.get_temp_folder()
            script_path = temp_folder+os.sep+'script.js'
            file_handle = open(script_path,'wb')
            file_handle.write(credential)
            file_handle.close()
            result = subprocess.check_output('node '+script_path,shell=True)
        return result