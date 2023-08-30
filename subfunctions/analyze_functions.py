# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 23:05:18 2021

@author: Administrator
"""
import numpy as np
import random
import csv

def read_csv(file_name, my_delim=',', my_quote='"'):
    len_csv = 0
    file_content = []
    with open(file_name, 'rU') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=my_delim, quotechar=my_quote)
        
        counter = 0
        for row in spamreader:
            #print ', '.join(row)
            if len_csv == 0:
                len_csv = len(row)
            elif len_csv != len(row):
                print('[warning] row %i size not equal %i/%i' % (counter, len(row), len_csv))
                print(', '.join(row))
            
            clean_row = []
            for list_item in row:
                if len(list_item) > 0 and list_item[-1] in [' ']:
                    list_item = list_item[:-1]
                if ',' in list_item:
                    list_item=list_item.replace(',',' ')
                if list_item == '':
                    continue
                else:
                    list_item=float(list_item)
                clean_row.append(list_item)
            file_content.append(clean_row)
            counter += 1        
        csv_np = np.array(file_content)    
    #file_contnet_pd = pd.read_csv(file_path)
    return csv_np
def write_csv(variable,csv_file):
    #csv_file = csv_name
    with open(csv_file, 'w') as f:
        for i1 in range(variable.shape[0]):
            if len(variable.shape)>1:
                for i2 in range(variable.shape[1]):
                    f.write(variable[i1,i2])
                    f.write(',')
            else:
              f.write(str(variable[i1]))  
            f.write('\n')
def write_csv_num(variable,csv_name):
    csv_file = csv_name + '.csv'
    with open(csv_file, 'w') as f:
        for i1 in range(variable.shape[0]):
            if len(variable.shape)>1:
                for i2 in range(variable.shape[1]):
                    f.write(str(variable[i1,i2]))
                    f.write(',')
            else:
              f.write(str(variable[i1]))  
            f.write('\n')
def sort_files(all_files, sep='_'):
    
    sorted_idx = []
    
    switcher = {
        'mono_motion': 0,
        'bino_motion': 1,
        'mono_static': 2,
        'bino_static': 3
        }
    for idx in range(len(all_files)):
        file = all_files[idx]
        name_split = file.split(sep)
        sorted_idx.append(int(idx/4) * 4 + switcher['_'.join(name_split[2:4])])
    
    arg_idx = np.argsort(sorted_idx)
    sorted_list = np.array(all_files)[arg_idx]
    
    
    return sorted_list

def unify_lim_whole(axes):
    
    for rw in range(axes.shape[0]):
        for col in range(axes.shape[1]):
            start0, end0 = axes[rw, col].get_ylim()
            if rw == 0 & col == 0:
                yst = start0
                yed = end0
                
            if yst > start0:
                yst = start0
            if yed < end0:
                yed = end0
    
    for rw in range(axes.shape[0]):
        for col in range(axes.shape[1]):
            axes[rw, col].set_ylim(yst, yed)
    
    return axes

def unify_lim(axes):
    
    all_st = []
    all_ed = []
    init_flag = True
    yst, yed = axes[0, 0].get_ylim()
    for col in range(axes.shape[1]):
        if col % 2 == 0 and col != 0:
            
            all_st.append(yst)
            all_ed.append(yed)
            
            init_flag = True
            
        for rw in range(axes.shape[0]):
            start0, end0 = axes[rw, col].get_ylim()
            
            if init_flag:
                yst = start0
                yed = end0
                init_flag = False
                
            if yst > start0:
                yst = start0
            if yed < end0:
                yed = end0
    all_st.append(yst)
    all_ed.append(yed)
            
    for col in range(axes.shape[1]):
        if col % 2 == 0:
            yst = all_st[int(col/2)]
            yed = all_ed[int(col/2)]
        for rw in range(axes.shape[0]):
            axes[rw, col].set_ylim(yst, yed)
    
    return axes

def unify_lim1(axes):
    """
    
    Parameters
    ----------
    axes : TYPE
        list of big figures.

    Returns
    -------
    axes : TYPE
        list of big figures.

    """
    
    yst, yed = axes[0][0, 0].get_ylim()
    for idx_fig in range(len(axes)):
        for rw in range(axes[idx_fig].shape[0]):
            for col in range(axes[idx_fig].shape[1]):
                start0, end0 = axes[idx_fig][rw, col].get_ylim()
                if yst > start0:
                    yst = start0
                if yed < end0:
                    yed = end0

            
    for idx_fig in range(len(axes)):
        for rw in range(axes[idx_fig].shape[0]):
            for col in range(axes[idx_fig].shape[1]):
                axes[idx_fig][rw, col].set_ylim(yst, yed)
    
    return axes

