from constants import *


# remember to call close after finish writing
class VMWriter:
    def __init__(self, vm_filename):
        self.vm_file = open(vm_filename, 'w')


    def close(self):
        self.vm_file.close()


    def write_push(self, segment, index):
        if segment not in SEGMENTS:
            raise Exception('unknown segment')
        self.vm_file.write('push {} {}\n'.format(segment, index))


    def write_pop(self, segment, index):
        if segment not in SEGMENTS:
            raise Exception('unknown segment')
        self.vm_file.write('pop {} {}\n'.format(segment, index))


    def write_arithmetic(self, command):
        if command not in COMMANDS:
            raise Exception('unknown command')
        self.vm_file.write(command + '\n')


    def write_label(self, label):
        self.vm_file.write('label {}\n'.format(label))


    def write_goto(self, label):
        self.vm_file.write('goto {}\n'.format(label))


    def write_if(self, label):
        self.vm_file.write('if-goto {}\n'.format(label))


    def write_call(self, name, n_args):
        self.vm_file.write('call {} {}\n'.format(name, n_args))


    def write_function(self, name, n_args):
        self.vm_file.write('function {} {}\n'.format(name, n_args))


    def write_return(self):
        self.vm_file.write('return\n')
