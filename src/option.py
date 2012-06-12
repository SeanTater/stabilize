'''
Created on Jun 8, 2012

@author: Sean Gallagher
@copyright: (C) 2012 Sean Gallagher
@license: GPLv3 or later
'''

import collections
all_groups = []
OptGroup = collections.namedtuple("OptGroup", "name description opts")

class OptGroup(dict):
    ''' This is a frontend to argparse but it's usable in other UI's (which argparse wouldn't be).
        The option's names are the keys in this dictionary. The name of the group is expected to be
        prepended to the option's names and the description displayed somewhere around them. 
        The default value of the function should be set as the "value" key of the option:
         e.g.: OptGroup("server", "serves files")['port'] = {"value", 80} '''
     
    def __init__(self, name, description):
        dict.__init__(self)
        self.name, self.description = name, description
        all_groups.append(self)
    
    def __call__(self, name):
        return self[name]['value']