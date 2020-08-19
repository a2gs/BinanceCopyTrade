#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

from datetime import datetime

def getTimeStamp()->str:
	return(datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))
