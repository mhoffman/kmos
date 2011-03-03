#!/usr/bin/python

import difflib
import copy

class UndoStack():
    def __init__(self, state_function, action = ''):
        self.stack = []
        self.head = 0
        self.current_action = action
        self.state_function = state_function
        self.origin = self.state_function()
        self.state = self.state_function()
        self.stack.append({'action':'',
            'diff':difflib.ndiff([],self.state)})

    def get_last_action(self):
        if self.stack:
            return self.stack[-1]['action']
        else:
            return ''

    def push_action(self, action):
        if self.state_function() != self.state:
            self.head += 1
            self.stack = self.stack[:self.head] + [{
                'action':self.current_action,
                'diff':difflib.ndiff(self.state, self.state_function())
                }]
            self.state = self.state_function()
        self.current_action = action

    def back(self):
        if self.head < 0 :
            raise UserWarning('BottomReached')
        else:
            diff = copy.copy(self.stack[self.head]['diff'])
            self.state = difflib.restore(diff, 1)
            self.head += -1
            self.current_action = self.stack[self.head]['action']
            return {'action':self.stat[self.head]['action'], 'state': self.state}
            

    def forward(self):
        if self.head  == len(self.stack) - 1 :
            return UserWarning('TopReached')
        else:
            self.head += +1
            diff = copy.copy(self.stack[self.head]['diff'])
            self.state = difflib.restore(diff, 1)
            self.current_action = self.stack[self.head]['action']
