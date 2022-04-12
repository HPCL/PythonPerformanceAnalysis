#!/usr/bin/env python
# coding: utf-8

import os
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statistics as st

from tau_parser import TauProfileParser


"""
"""

class Visualization(object):
    def __init__(self, nthreads, path, function_name):
        self.nthreads = nthreads
        self.path = path
        self.function_name = function_name


    def get_parsed_csv(self, hardware_counter):
        for i in range(8):
            kokkos = 'false'
            tmp_path = self.path
            if "FP_ARITH" in hardware_counter:
                tmp_path = tmp_path + hardware_counter + "/" + str(i) + "/MULTI__PAPI_NATIVE_" + hardware_counter + "/"
            else:
                tmp_path = tmp_path + hardware_counter + "/" + str(i) + "/MULTI__" + hardware_counter + "/"
            
            if i > 5:
                kokkos = 'true'

            data = TauProfileParser.parse(tmp_path)
            dataframe = data.interval_data()
            dataframe = dataframe['Exclusive']
            dataframe.to_csv('data.csv')

            data = pd.read_csv("data.csv") 

            function_df = data.loc[data['Timer'].str.contains('.TAU application ')]
            function_df = function_df.loc[function_df['Timer'].str.contains(self.function_name)]

            if(self.function_name == "KalmanGain"):
                function_df = function_df.drop(function_df[function_df['Timer'].str.contains('KalmanGainInv')].index)

            if '_TBB' in tmp_path:
                tmp_path = tmp_path.replace('_TBB', '')
        
            if kokkos == "true":
                df = pd.DataFrame()
                lst = []
                for i in range(self.nthreads):
                    mean = function_df.loc[function_df["Thread"] == i, "Exclusive"].mean()
                    if pd.isna(mean) != True:
                        lst.append(float(mean))
                df['Exclusive'] = lst
                df['Exclusive'].to_csv('Parsed Data/' + self.function_name + '_' + hardware_counter + '.csv', mode='a', index=False)
            else:
                function_df['Exclusive'].to_csv('Parsed Data/' + self.function_name + '_' + hardware_counter + '.csv', mode='a', index=False)

            os.remove("data.csv")


    def create_graph(self, graph_type, data_list, scale, graph_title, y_label, chart_type):
        for graph in graph_type:
            index = []
            for i in range(self.nthreads):
                index.append(i)

            if graph == 'gcc':
                keys = ["gcc_omp", "gcc_tbb", "gcc_eigen", "gcc_kokkos"]
                df = pd.DataFrame({keys[0]: data_list[0], keys[1]: data_list[2], keys[2]: data_list[4], keys[3]: data_list[6]}, index=index)
            elif graph == 'icc':
                keys = ["icc_omp", "icc_tbb", "icc_eigen", "icpc_kokkos"]
                df = pd.DataFrame({keys[0]: data_list[1], keys[1]: data_list[3], keys[2]: data_list[5], keys[3]: data_list[7]}, index=index)
        
            if chart_type == 'bar':
                ax = df.plot.bar(stacked=True)
            elif chart_type == 'line':
                ax = df.plot.line()
            fig = ax.get_figure()
            fig.set_size_inches(15, 6)
            plt.ylim(0, scale)
            plt.title(graph_title)
            plt.xlabel('Threads')
            plt.ylabel(y_label)
            plt.savefig('Graphs/' + graph_title + ' ' + graph + '.png', bbox_inches='tight')
            plt.show()


    def mean(self, data_list):
        for list in data_list:  
            if(len(list)) != self.nthreads:
                mean = sum(list)/len(list)
                for i in range(len(list), self.nthreads, 1):
                    list.append(mean) 


    def read_row(self, csvreader, index, tmp_list, data_list):
        for row in csvreader:
            if "Exclusive" in row:
                if(index != -1):
                    data_list.append(tmp_list)
                index += 1
                tmp_list = []
            else:
                tmp_list.append(float(row[0]))
        data_list.append(tmp_list)


    def create_visualization(self, hardware_counter, graph_type, scale, chart_type):
        file_exists = os.path.exists('Parsed Data/' + self.function_name + '_' + hardware_counter + '.csv')
        if not file_exists:
            self.get_parsed_csv(hardware_counter)
        else:
            print('File already exists')

        file = open('Parsed Data/' + self.function_name + '_' + hardware_counter + '.csv')
        csvreader = csv.reader(file)

        data_list = []
        tmp_list = []
        index = -1

        self.read_row(csvreader, index, tmp_list, data_list)
        self.mean(data_list)

        graph_title = self.function_name + ' ' + hardware_counter
        y_label = hardware_counter
        self.create_graph(graph_type, data_list, scale, graph_title, y_label, chart_type)


    def create_visualization_miss_rate(self, cache_miss_counter, cache_access_counter, miss_rate, graph_type, scale, chart_type):
        file_exists = os.path.exists('Parsed Data/' + self.function_name + '_' + cache_miss_counter + '.csv')
        if not file_exists:
            self.get_parsed_csv(cache_miss_counter)
        else:
            print('File already exists')

        file_exists = os.path.exists('Parsed Data/' + self.function_name  + '_' + cache_access_counter + '.csv')
        if not file_exists:
            self.get_parsed_csv(cache_access_counter)
        else:
            print('File already exists')


        # Read Cache Miss Data
        file = open('Parsed Data/' + self.function_name  + '_' + cache_miss_counter + '.csv')
        csvreader = csv.reader(file)

        data_list_misses = []
        tmp_list = []
        index = -1

        self.read_row(csvreader, index, tmp_list, data_list_misses)
        self.mean(data_list_misses)

        # Read Cache Access Data
        file = open('Parsed Data/' + self.function_name  + '_' + cache_access_counter + '.csv')
        csvreader = csv.reader(file)

        data_list_accesses = []
        tmp_list = []
        index = -1

        self.read_row(csvreader, index, tmp_list, data_list_accesses)
        self.mean(data_list_accesses)

        # Calculate Cache Miss Rate
        data_list = []
        tmp_list = []
        for i in range(len(data_list_accesses)):
            for j in range(len(data_list_accesses[i])):
                val = data_list_misses[i][j]/data_list_accesses[i][j]
                tmp_list.append(val)
            data_list.append(tmp_list)
            tmp_list = []

        # Graph settings
        graph_title = self.function_name  + ' ' + miss_rate
        y_label = miss_rate
        self.create_graph(graph_type, data_list, scale, graph_title, y_label, chart_type)


    def create_visualization_vector_flops(self, fp_128B_hardware_counter, fp_256B_hardware_counter, fp_512B_hardware_counter, graph_type, scale, chart_type):
        file_exists = os.path.exists('Parsed Data/' + self.function_name + '_' + fp_128B_hardware_counter + '.csv')
        if not file_exists:
            self.get_parsed_csv(fp_128B_hardware_counter)
        else:
            print('File already exists')

        file_exists = os.path.exists('Parsed Data/' + self.function_name + '_' + fp_256B_hardware_counter + '.csv')
        if not file_exists:
            self.get_parsed_csv(fp_256B_hardware_counter)
        else:
            print('File already exists')

        file_exists = os.path.exists('Parsed Data/' + self.function_name + '_' + fp_512B_hardware_counter + '.csv')
        if not file_exists:
            self.get_parsed_csv(fp_512B_hardware_counter)
        else:
            print('File already exists')

        offset = 1
        mul = 4 * offset
        index = -1
        data_list_128 = []


        file = open('Parsed Data/' + self.function_name + '_' + fp_128B_hardware_counter + '.csv')
        csvreader = csv.reader(file)
        for row in csvreader:
            if "Exclusive" in row:
                if(index != -1):
                    data_list_128.append(tmp_list)
                index += 1
                tmp_list = []
            else:
                tmp_list.append(float(row[0]) * mul)

        data_list_128.append(tmp_list)
        self.mean(data_list_128)
        
        offset+=1
        data_list_256 = []
        tmp_list = []
        index = -1

        file = open('Parsed Data/' + self.function_name + '_' + fp_256B_hardware_counter + '.csv')
        csvreader = csv.reader(file)
        for row in csvreader:
            if "Exclusive" in row:
                if(index != -1):
                    data_list_256.append(tmp_list)
                index += 1
                tmp_list = []
            else:
                tmp_list.append(float(row[0]) * mul)

        data_list_256.append(tmp_list)
        self.mean(data_list_256)

        offset+=1
        data_list_512 = []
        tmp_list = []
        index = -1

        file = open('Parsed Data/' + self.function_name + '_' + fp_512B_hardware_counter + '.csv')
        csvreader = csv.reader(file)
        for row in csvreader:
            if "Exclusive" in row:
                if(index != -1):
                    data_list_512.append(tmp_list)
                index += 1
                tmp_list = []
            else:
                tmp_list.append(float(row[0]) * mul)

        data_list_512.append(tmp_list)
        self.mean(data_list_512)

        data_list = []
        for i in range(len(data_list_128)):
            tmp = []
            for j in range(len(data_list_128[i])):
                total = data_list_128[i][j] + data_list_256[i][j] + data_list_512[i][j]
                tmp.append(total)
            data_list.append(tmp)
            
        # Graph settings
        graph_title = self.function_name + ' Vector_Flops'
        y_label = 'Vector_Flops'
        self.create_graph(graph_type, data_list, scale, graph_title, y_label, chart_type)