#!/usr/bin/python
# -*- coding: UTF-8 -*-

#author:ZHOGNQI

import os
curent_path = os.path.abspath('.')
print(curent_path)
print(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))