"""search models and subckt from txt files"""


from pathlib import Path
from tkinter import EXCEPTION

field_delimiters = '()=,' # according ngspice might be different in LT or P spice

class StateMachine:
    """ simple FSM to control parsing"""
    def __init__(self):
        self.search_states = ['awaiting', 'comment', 'found', 'follow_up', 'next_line', 'post', 'done', 'after_done']
        self.index = 0
        self.next_index = 0

    def __eq__(self, other):
        return other == self.search_states[self.index]

    def get(self):
        return self.search_states[self.index]

    def set(self, state):
        self.index = self.search_states.index(state)

    def set_next(self, state):
        self.next_index = self.search_states.index(state)

    def go_next(self):
        self.index = self.next_index

    def __str__(self):
        return self.get()


def get_models(file_path, model_list={}, recursive=True, **search_arguments):
    """search for models in file according to search_arguments
    retuns a dict { cnt: [ model, name , callable line, True]} """
    if model_list is None or len(model_list) == 0:
        model_list = {}
        model_cnt = 1
    else:
        model_cnt = max(model_list.keys()) + 1
    if not Path(file_path).exists():
        return { }
    state = StateMachine()
    search_args = dict(**search_arguments)
    line_cnt = 0
    model_count = 0
    last_comment = 1
    recursive_cnt = 0
    active_line = ''
    try:
        for line in open(file_path):
            line_cnt += 1
            if state == 'follow_up':
                if '+' in line:
                    nline = line.split('+')[1]
                    sline = active_line.split() + nline.split()
                    try:
                        found_model_type = sline[search_args['model_pos']]
                        for a in field_delimiters:
                            if a in found_model_type:
                                found_model_type = found_model_type.split(a)[0]
                        model_list[model_cnt] = [sline[search_args['name_pos']], found_model_type, file_path, line, True]
                        model_count += 1
                        model_cnt += 1
                    except IndexError:
                        print(f'error in file: {str(file_path)}')
                        print(f'error at line: {line_cnt}')
                        print(f'error in line: {line}')
                state.set_next('awaiting')
                state.go_next()

            if state == 'awaiting':
                if recursive or recursive_cnt == 0:
                    if search_args['model'] in line.upper():
                        try:
                            sline = line.split()
                            if len(sline) <3: # we cannot decode
                                active_line = line
                                state.set_next('follow_up')
                                state.go_next()
                            else:
                                found_model_type = sline[search_args['model_pos']]
                                for a in field_delimiters:
                                    if a in found_model_type:
                                        found_model_type = found_model_type.split(a)[0]
                                model_list[model_cnt] = [sline[search_args['name_pos']] , found_model_type, file_path, line, True]
                                model_count += 1
                                model_cnt += 1
                        except IndexError:
                            print(f'error in file: {str(file_path)}')
                            print(f'error at line: {line_cnt}')
                            print(f'error in line: {line}')

                if '.SUBCKT' in line.upper():
                    recursive_cnt += 1
                if '.ENDS' in line.upper() and recursive_cnt > 0:
                    recursive_cnt -= 1
    except  UnicodeDecodeError:
        pass


    return model_list, model_count

def get_model_body(file_path, model_name, recursive=True, **search_arguments):
    """search for models in file according to search_arguments
    retuns a dict { cnt: [ model, name , callable line, True]} """
    model_text = []
    state = StateMachine()
    if not Path(file_path).exists():
        return { }
    search_args = dict(**search_arguments)
    line_cnt = 0
    comment_count = 0
    recursive_cnt = 0
    recursive_level = 0

    for line in open(file_path):
        sline = line.split()
        if state in ['done', 'after_done']:
            break
        if state == 'awaiting':
            model_text = []
            comment_count = 0
            if (len(sline) == 0) or ('*' in sline[0]):
                state.set_next('comment')

        if state == 'comment':
            comment_count += 1
            if comment_count > search_args['max_comment_count']:
                model_text.pop(0)

            if (len(sline) == 0) or ('*' in sline[0]):
                state.set_next('comment')
            else:
                state.set_next('awaiting')  # can be overruled

        if recursive or recursive_cnt == 0:
            if (search_args['model'] in line.upper()) and (model_name.upper() in line.upper()):
                state.set_next('found')
                recursive_level = recursive_cnt + 1
                if not search_args['continuation']:
                    if r'\\' in line:
                        state.set_next('next_line')  # include next line
                    else:
                        state.set_next('post')  # check next line for inclusion

        if state =='found':
            if search_args['continuation'] :
                state.set_next('follow_up')
            else:
                if r'\\' in line:
                    state.set_next('next_line')   #  include next line
                else:
                    state.set_next('post')   # check next line for inclusion

        if state == 'follow_up':
            if (search_args['model_end'] in line.upper()) and (recursive_cnt == recursive_level):
                state.set_next('done')

        if state == 'next_line':
            if r'\\' in line:
                state.set_next('next_line')  # include next line
            else:
                state.set_next('post')  # check next line for inclusion

        if state == 'post':
            if len(sline) > 0 and r'+' in sline[0]:
                state.set_next('post')
            else:
                state.set_next('after_done')

        state.go_next()  # set found state to CTUAL

        # collect data
        if state in ['comment', 'found', 'follow_up', 'next_line', 'post', 'done']:
            model_text.append(line)

        if '.SUBCKT' in line.upper():
            recursive_cnt += 1
        if '.ENDS' in line.upper() and recursive_cnt > 0:
            recursive_cnt -= 1
        line_cnt += 1
        if line_cnt == 218:
            pass


    return model_text
