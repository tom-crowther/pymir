#!/usr/bin/env python

import os
import subprocess

class Task:

    # assumes the only thing with 'miriad' in the path is miriad
    pathlist = os.environ['PATH'].split(':')
    mirdoc = os.environ['MIRPDOC']
    mirbin = next(filter(lambda x: 'miriad' in x, pathlist), None)
    if mirbin is None:
        print(f"Unable to find miriad binary directory")
        print(f"Check that it is in $PATH env variable correctly: {pathlist}")
        exit()
    mirhelp = os.path.join(mirbin, 'mirhelp')

    task_response = subprocess.run([mirhelp, 'tasks'], capture_output=True)
    if task_response.returncode != 0:
        print(str(task_response.stderr))
        print(f"Unable to find or call miriad help binary: {mirhelp}")
        print(f"Check that the $PATH variable contains miriad correctly")
        exit()

    task_list = task_response.stdout.decode('utf-8').splitlines()
    empty_lines = [idx for idx, val in enumerate(task_list) if '' == val]
    task_list = ' '.join(task_list[empty_lines[1]:empty_lines[2]]).split()

    def process_response(self, resp):
        if resp.returncode != 0:
            if resp.stderr != b'':
                print(str(resp.stderr))
            return resp.returncode
        else:
            return resp.stdout.decode('utf-8')

    def run_gen_cmd(self, cmd, args):
        if type(args) != list:
            args = [args]
        resp = subprocess.run([cmd] + args, capture_output=True)
        proc = self.process_response(resp)
        print(proc)
        return proc


    def __init__(self, taskname):
        # creating a task requires the task type to be defined
        if not taskname in Task.task_list:
            print(f"{taskname} is not in valid list of tasks")
            raise NameError(taskname)
        self.taskname = taskname
        self.doc = taskname + '.doc'
        self.executed = False
        self.response = None
        self._get_task_inputs()

    # annoyingly if a task has 'in' parameter we can't set attr directly
    # hopefully can find a way around this in the future
    def set_in(self, in_val):
        self._set_param_str('in', in_val)

    def go(self):
        print("Running task...")
        self._run_task_cmd()

    def interactive(self):
        print("Interactive mode")
        print("Set of all available inputs for this task as reference:")
        self.inp()
        print("Now running through each option and allowing for input")
        for param in self.inputs:
            self._print_param_name(param)
            param_val = input('')
            if param_val != '':
                self._set_param_str(param, param_val)

    def inp(self):
        self._print_taskname()
        for input in self.inputs:
            self._print_param_name(input)
            print(f"{self._get_param_str(input)}")

    def help(self):
        self.run_gen_cmd(Task.mirhelp, self.taskname)
        pass

    def unset(self, param):
        if hasattr(self, param):
            delattr(self, param)

    def clear(self):
        for param in self.inputs:
            if hasattr(self, param):
                delattr(self, param)

    # internal methods
    def _print_taskname(self):
        empty = ' ' * (self.longest_input - 5)
        print(f"Task:{empty}{self.taskname}")

    def _print_param_name(self, param):
        empty = ' ' * (self.longest_input - len(param))
        print(f"{param}{empty} =  ", end='')

    def _run_task_cmd(self):
        cmd = self._build_cmd_list()
        if cmd is not None:
            self.response = subprocess.run(cmd, capture_output=True)
            self._parse_output()
            print("Stdout response:")
            print(self.stdout)
            if self.errorflag:
                print("An error occurred during execution:")
                print(self.stderr)

    def _parse_output(self):
        stderr = self.response.stderr.decode('utf-8')
        if stderr != '':
            self.stderr = stderr
            self.errorflag = True
        else:
            self.stderr = None
            self.errorflag = False
        self.stdout = self.response.stdout.decode('utf-8')
        self.executed = True

    def _check_param_str(self, param):
        # special case
        if param == 'in':
            param = 'in_'
        return hasattr(self, param)

    def _set_param_str(self, param, value):
        # special case
        if param == 'in':
            param = 'in_'
        setattr(self, param, value)

    def _get_param_str(self, param):
        # special case
        if param == 'in':
            param = 'in_'
        if hasattr(self, param):
            return getattr(self, param)
        else:
            return ''

    def _get_task_inputs(self):
        inputs = []
        longest = 0
        with open(os.path.join(Task.mirdoc, self.doc), 'r') as f:
            for line in f.read().splitlines():
                if line[:3] == '%A ':
                    inputs.append(line[3:])
                    length = len(inputs[-1])
                    if length > longest:
                        longest = length
        self.inputs = inputs
        self.longest_input = longest # for formatting print output

    def _build_item_str(self, param):

        if not self._check_param_str(param):
            return
        input_str = param + '=' + self._get_param_str(param)
        return input_str

    def _build_cmd_list(self):
        cmd = [self.taskname]
        for input in self.inputs:
            input_str = self._build_item_str(input)
            if input_str is not None:
                cmd.append(input_str)
        if len(cmd) <= 1:
            print(f"Error: More inputs required before running command")
            self.inp()
            return
        return cmd

