# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 14:07:26 2020

@author: Administrator
"""
import csv
import time
import sys
import numpy as np
import os
# In[]

def check_dir(folder):
    if not os.path.isdir('output'):
        os.mkdir(folder)
    return

def expand_data(invar):
    
    if len(invar)==1:
        invar = '0'+invar
    return invar

def init_output(time_str, OUTPUT_PATH, outfile_base, ok_data, play_sound=True, additional=True):
    check_dir(OUTPUT_PATH)
    # if additional:
    #     year, month, day, hour, minutes = map(int, time.strftime("%Y %m %d %H %M").split())
    #     time_str = '-'.join([str(year), expand_data(str(month)), expand_data(str(day)), expand_data(str(hour)), expand_data(str(minutes))])
    # else:
    #     time_str = ''
    if not additional:
        time_str = ''
    time_str += '_' + ok_data[2] + '_' + ok_data[3] +  '_' + ok_data[4]+  '_' + ok_data[5]
        
    output_file = '_'.join([outfile_base, time_str, os.path.basename(sys.argv[0])]) + r'.csv'
    csv_hdl = open(os.path.join(OUTPUT_PATH, output_file),'w')
    
    return csv_hdl

def init_log(time_str, OUTPUT_PATH, outfile_base, idx, ok_data, additional=True):
    check_dir(OUTPUT_PATH)
    # if additional:
    #     year, month, day, hour, minutes = map(int, time.strftime("%Y %m %d %H %M").split())
    #     time_str = '-'.join([str(year), expand_data(str(month)), expand_data(str(day)), expand_data(str(hour)), expand_data(str(minutes))])
    # else:
    #     time_str = ''
    
    if not additional:
        time_str = ''
    time_str += '_' + ok_data[2] + '_' + ok_data[3] +  '_' + ok_data[4]+  '_' + ok_data[5]
        
    output_file = '_'.join([outfile_base, time_str, os.path.basename(sys.argv[0])]) + '_' + str(idx) + r'_log.csv'
    csv_hdl = open(os.path.join(OUTPUT_PATH, output_file),'w')
    
    return csv_hdl


def write2file(csvhdl,data):
    
    for ir in range(len(data)):
        curr_data = data[ir]
        csvhdl.write('{}, {}, {}, {}, {}, {}, {}, {}, {}, {}\n'.format(*curr_data))
    
    csvhdl.close()
    
    return

def write2file25(csvhdl,data):
    
    for ir in range(len(data)):
        curr_data = data[ir]
        csvhdl.write('{}, {}, {}, {}, {}, {}\n'.format(*curr_data))
    
    csvhdl.close()
    
    return
def log2file(time_str, data,OUTPUT_PATH, OUTPUT_FILE, ok_data):
    
    print('Saving log to file')
    for i_exp in range(len(data)):
        csvhdl = init_log(time_str, OUTPUT_PATH, OUTPUT_FILE, i_exp, ok_data)
        i_exp,log_data=data[i_exp]
        for ir in range(len(log_data)):
            curr_data = log_data[ir]
            csvhdl.write('{}, {}, {}\n'.format(*curr_data))
        csvhdl.close()
    return