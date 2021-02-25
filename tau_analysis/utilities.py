'''
Brian Gravelle, Boyana Norris

Useful functions for processing mictest data in the python notebooks 
This will evolve into a real library

Data Structures:
Currently these are somewhat in flux and poorly labeled accross functions,
but the important data structures are listed here

metric_data or metric_dict
  - a dictionary of panda dataframes that holds the metrics
  - each dictionary entry is a metric name (or METADATA) and a DF with the data
  - metric data contains lots of info about each reading including thread, rank, context
    also the region and the Inclusive and Exclusive values
  - you get this by calling load_perf_data or get_pandas
  - if from scaling data then there are 2 dictionary levels - num threads added above the metrics

alldata 
  - is a panda dataframe that combines these metrics into a single dataframe
  - this keeps the thread, region and either Inclusive OR Exclusive
  - get this by sending metric_data to combine_metrics


dfs
  - a data frame with data for one metric



'''




############################################################################################

#                                                    Imports

############################################################################################


import os
from os import listdir
from os.path import isfile, join

import sys
import shelve

try:
    import taucmdr
except ImportError:
    sys.path.insert(0, os.path.join(os.environ['__TAUCMDR_HOME__'], 'packages'))
finally:
    from taucmdr.model.project import Project
    from taucmdr.data.tau_trial_data import TauTrialProfileData

import matplotlib
import matplotlib.pyplot as plt
matplotlib.style.use('ggplot')
font = {'weight' : 'bold',
        'size'   : 24
}
matplotlib.rc('font', **font)

import pandas as pd
import math
import numpy as np
import operator
import time
import re
import collections
import seaborn as sns
# for fancy tables
from IPython.core.display import display, HTML, display_html
import copy


############################################################################################

#                                      Metric Names

############################################################################################

METRIC_NAMES={'PAPI_TOT_CYC':'Total Cycles',
'PAPI_NATIVE_UOPS_RETIRED:PACKED_SIMD':'Vector operations',
'PAPI_L2_TCA' : 'L2 accesses',
'PAPI_NATIVE_LLC_MISSES' : 'L3 total cache misses',
'PAPI_NATIVE_LLC_REFERENCES' : 'L3 accesses',
'PAPI_TLB_DM' : 'TLB data misses',
'PAPI_BR_MSP' : 'Branch mispredictions',
'PAPI_L1_TCM' : 'L1 total cache misses',
'PAPI_L2_TCM' : 'L2 total cache misses',
'PAPI_LST_INS' : 'Load/store instructions',
'PAPI_BR_CN' : 'Conditional branches',
'PAPI_TOT_INS' : 'Total instructions',
'PAPI_BR_INS' : 'Branch instructions',
'PAPI_BR_UCN' : 'Unconditional branches',
'PAPI_NATIVE_UOPS_RETIRED:SCALAR_SIMD' : 'Scalar vector ops',
'PAPI_RES_STL' : 'Total resource stalls (cycles)',
'PAPI_NATIVE_FETCH_STALL':'Number of cycles stalled for instruction cache miss',
'PAPI_NATIVE_RS_FULL_STALL' : 'Resource stalls',
'DERIVED_STALL_PERCENT' : 'Fraction of total stalls',
'DERIVED_L1_MISSRATE' : 'L1 miss rate',
'DERIVED_L3_MISSRATE' : 'L3 miss rate',
'DERIVED_BRANCH_MR' : 'Branch misprediction rate',
'DERIVED_IPC' : 'Instructions per cycle',
'DERIVED_CPI' : 'Cycles per instruction',
'DERIVED_VIPI' : 'Vector instructions fraction',
'DERIVED_VIPC' :'Vector instructions per cycle',
'Other' : 'Other'
}



############################################################################################

#                                   retrieving data from profiles

############################################################################################



#TODO add params so this is a real function
def get_pandas_non_summary():
    '''
    returns a dictionary of pandas
    keys are the metrics that each panda has data for
    vals are the pandas that have the data organized however they organzed it
    DEPRECATED - may not work
    '''
    num_trials = Project.selected().experiment().num_trials
    trials = Project.selected().experiment().trials(xrange(0, num_trials))
    trial_data = {}
    for i in xrange(0, num_trials):
        trial_data[i] = trials[i].get_data()
        
    start = time.time()
    metric_data = {}

    for trial in xrange(0, num_trials):
        thread_data = []
        for i in xrange(0, len(trial_data[trial])):
            for j in xrange(0, len(trial_data[trial][i])):
                for k in xrange(0, len(trial_data[trial][i][j])):
                    thread_data.append(trial_data[trial][i][j][k].interval_data())
                    metric_data[trial_data[trial][i][j][k].metric] = pd.concat(thread_data)
                    metric_data[trial_data[trial][i][j][k].metric].index.names = ['trial', 'rank', 'context', 'thread', 'region']
        
    end = time.time()
    
    print('Time spent constructing dataframes %s' %(end-start))
    print('\nMetrics included:')
    for m in metric_data.keys():
        print("\t%s"%m)
    
    return metric_data

def load_perf_data(application,experiment,nolibs=False,scaling=False,callpaths=True,time=False,multi=False,data_dir=".tau"):
    '''
        Return a Pandas dictionary from data in the detault path
        TODO filtering and scaling
    '''
    path = data_dir + "/" + application + "/" + experiment + "/"
    key=application + "-" + experiment 
    
    if os.path.exists(key + '.shelve.dat'):
         d = shelve.open(key+'.shelve',flag='r')
         metric_dict = d[key]
         d.close()
    else:
        if  not os.path.exists(path):
            sys.exit("Error: invalid data path: %s" % path)

        if scaling:
            metric_dict = get_pandas_scaling(path, callpaths=callpaths, time=time)
        elif multi:
            metric_dict = get_pandas_multi(path, callpaths=callpaths)
        else:
            metric_dict = get_pandas(path,callpaths=callpaths)
    
    if nolibs and not scaling:
        filtered_dict = {}
        for k,v in metric_dict.items():
            if k == 'METADATA': filtered_dict[k] = metric_dict[k]
            else: filtered_dict[k] = filter_libs_out(metric_dict[k])
        return filtered_dict
    elif nolibs:
        filtered_dict = {}
        for threads,vals in metric_dict.items():
            filtered_dict[threads] = {}
            for k,v in vals.items():
                if k == 'METADATA': filtered_dict[threads][k] = metric_dict[threads][k]
                else: filtered_dict[threads][k] = filter_libs_out(metric_dict[threads][k])
                #filtered_dict[threads][k] = filtered_dict[threads][k].replace('[SUMMARY] .TAU application  => [CONTEXT] .TAU application =>','')
        return filtered_dict
    else:
        return metric_dict

def get_pandas(path, callpaths=False, summary=True):
    '''
    returns a dictionary of pandas
        - keys are the metrics that each panda has data for
    params
        - path is the path to the trials (should e directory filled with numbered dirs)
        - 
    vals are the pandas that have the data organized however they organzed it
        - samples are turned into summaries
        - tau cmdr must be installed and .tau with the relevant data must be in this dir
    '''
    if not os.path.exists(path):
        sys.exit("Error: invalid data path: %s" % path)
    metric_data = {}
    
    paths = [path+n+'/' for n in listdir(path) if (not isfile(join(path, n)))]
    num_trials = len(paths)
    #files = [f for f in listdir(path) if not isfile(join(p, f))]
    for p in paths:
        d = [f for f in listdir(p) if (not isfile(join(p, f))) and (not (f == 'MULTI__TIME'))]
        prof_data = TauTrialProfileData.parse(p+'/'+d[0])
        time_data = TauTrialProfileData.parse(p+'/MULTI__TIME')
        prof_data.metadata = time_data.metadata
        metric = prof_data.metric
        if summary:
            metric_data[metric] = prof_data.summarize_samples()
        else:
            metric_data[metric] = prof_data.interval_data()

        metric_data[metric].index.names = ['rank', 'context', 'thread', 'region']
        if not callpaths:
            #metric_data[metric]['Total'] = metric_data[metric][metric_data[metric].index.get_level_values('region').str.match('[SUMMARY] .TAU application')]
            metric_data[metric] = metric_data[metric][~metric_data[metric].index.get_level_values('region').str.contains(".TAU application")]
            
        metric_data['METADATA'] = prof_data.metadata
    return metric_data

def get_pandas_multi(path, callpaths=False, summary=True):
    '''
    returns a dictionary of pandas
        - keys are the metrics that each panda has data for
    params
        - path is the path to the trials (should e directory filled with numbered dirs)
        - 
    vals are the pandas that have the data organized however they organzed it
        - samples are turned into summaries
        - tau cmdr must be installed and .tau with the relevant data must be in this dir
    '''
    if not os.path.exists(path):
        sys.exit("Error: invalid data path: %s" % path)
    metric_data = {}
    
    paths = [path+n+'/' for n in listdir(path) if (not isfile(join(path, n)))]
    num_trials = len(paths)
    #files = [f for f in listdir(path) if not isfile(join(p, f))]
    for p in paths:
        d = [f for f in listdir(p) if (not isfile(join(p, f))) and (not (f == 'MULTI__TIME'))]
        for _d in d: 
	        prof_data = TauTrialProfileData.parse(p+'/'+_d)
	        time_data = TauTrialProfileData.parse(p+'/MULTI__TIME')
	        prof_data.metadata = time_data.metadata
	        metric = prof_data.metric
	        if summary:
	            metric_data[metric] = prof_data.summarize_samples()
	        else:
	            metric_data[metric] = prof_data.interval_data()

	        metric_data[metric].index.names = ['rank', 'context', 'thread', 'region']
	        if not callpaths:
	            #metric_data[metric]['Total'] = metric_data[metric][metric_data[metric].index.get_level_values('region').str.match('[SUMMARY] .TAU application')]
	            metric_data[metric] = metric_data[metric][~metric_data[metric].index.get_level_values('region').str.contains(".TAU application")]
	            
	        metric_data['METADATA'] = prof_data.metadata
    return metric_data

def get_pandas_scaling(path, callpaths=False, time=False, summary=True):
    '''
    returns a dictionary of dictionaries of pandas
    The first layer of keys is the number of threads
    The second layer keys are the metrics that each panda has data for
    vals are the pandas that have the data organized however they organzed it
        - samples are turned into summaries
        - tau cmdr must be installed and .tau with the relevant data must be in this dir
    '''
    
    metric_data = {}
    
    # generate list of paths to read in
    paths = [path+n+'/' for n in listdir(path) if (not isfile(join(path, n)))]
    num_trials = len(paths)
    if num_trials <= 0:
        print("ERROR reading trials")

    num_threads = -1
    metric = 'NA'
    trial_cnt = 0
    error_cnt = 0

    # gather data for path lists
    # puts it in metric data
    #    starts as dict (thread count) of dict (metrics) of list (individual trials)
    for p in paths:
        if time:
            d = [f for f in listdir(p) if (not isfile(join(p, f))) and ((f == 'MULTI__TIME'))]
        else:
            d = [f for f in listdir(p) if (not isfile(join(p, f))) and (not (f == 'MULTI__TIME'))]

        try:
            trial_cnt +=1
            trial_dir = p+'/'+d[0]
        except:
            # if the dir is empty that trial ffailed for some reason so skip
            # TODO make this more precise (the metric is just a guess based on the previous one)
            # print "Possible missing metric: \nnthread = %d \nmetric  = %s \ndir     = %s\n" % (num_threads, metric, p)
            # print ("Possible missing metric: \nnthread = %d \nmetric  = %s\n" % (num_threads, metric))
            error_cnt +=1
            continue
            # print( p ) # some trials don't have data use this to figure out which
            # missing data caused by errors in experiment scripts or crashes


        prof_list = [f for f in listdir(trial_dir)]
        num_threads = len(prof_list)

        if num_threads not in metric_data.keys():
            metric_data[num_threads] = {}
        elif time:
            continue

        # prof_data = TauTrialProfileData.parse(trial_dir)
        try:
            prof_data = TauTrialProfileData.parse(trial_dir)
        except:
            print ( "Parsing ERROR: \ndir = %s" % (trial_dir))
            continue 


        metric = prof_data.metric


        if metric not in metric_data[num_threads].keys():
            metric_data[num_threads][metric] = []

        if summary:
            metric_data[num_threads][metric].append(prof_data.summarize_samples(callpaths=callpaths))
        else:
            tmp = prof_data.interval_data()
            base_data = tmp.loc[tmp['Timer Type'] == 'SAMPLE']
            not_summary = base_data[['Calls', 'Exclusive', 'Inclusive', 'ProfileCalls',  'Subcalls']]
            # not_summary = base_data.groupby(['Node', 'Context', 'Thread', 'Timer Name'])
            metric_data[num_threads][metric].append(not_summary)
        # metric_data[num_threads][metric].append(prof_data.interval_data())
        metric_data[num_threads][metric][-1].index.names = ['rank', 'context', 'thread', 'region']
        if not callpaths:
            # this line magically gets rid of the .TAU samples that otherwise unhelpfully dominate the data
            metric_data[num_threads][metric][-1] = metric_data[num_threads][metric][-1][~metric_data[num_threads][metric][-1].index.get_level_values('region').str.contains(".TAU application")]

        try:
            time_data = TauTrialProfileData.parse(p+'/MULTI__TIME')
            prof_data.metadata = time_data.metadata
            metric_data[num_threads]['METADATA'] = prof_data.metadata
        except:
            # TODO make this more precise (the metric is just a guess based on the previous one)
            print ( "Possible missing metric: \nnthread = %d \nmetric = %s" % (num_threads, metric))

    print( "Found: %d trials with %d errors\n\n" % (trial_cnt, error_cnt))


    # average metric data
    #   turns dict of dict of list into dict of dict of panda (average of listed trials)
    for kt in metric_data:
        for km in metric_data[kt]:
            if not (km == 'METADATA'):
                ntrials = len(metric_data[kt][km])
                if ntrials > 1:
                    temp = metric_data[kt][km][0].copy()
                    temp.index = temp.index.droplevel()
                    metric_sum = temp.unstack()
                    for i in range(1, ntrials):
                        temp = metric_data[kt][km][i].copy()
                        temp.index = temp.index.droplevel()
                        metric_sum = metric_sum + temp.unstack()
                    metric_data[kt][km] = (metric_sum / ntrials).stack()
                else:
                    metric_data[kt][km] = metric_data[kt][km][0]

    return metric_data

def remove_erroneous_threads(metric_data, thread_list):
    '''
    some trial are intended to run with n threads but m != n threads are recorded
    this function allows the user to easily remove trials that don't conform
    
    - metric_data is the dictionary output from get_pandas_scaling()
    - thread_list is the list of thread counts requested
        - any thread counts not in thread list will be excluded
        - this may not be entirely accurate if an erroneous count is equal to a real count
    - returns new dictionary
    '''

    filtered_data = {}
    for k in metric_data:
        if k in thread_list:
            filtered_data[k] = metric_data[k]

    return filtered_data


def combine_metrics(metric_dict,inc_exc='Inclusive'):
    '''
    Transforms a dictionary of metrics with each value as a panda into 
        a single panda with metrics as columns
    metric_dict hould be a dictionary with keys as metrics and pandas as values
    '''

    if inc_exc == 'Inclusive': todrop = 'Exclusive'
    else: todrop = 'Inclusive'
    
    metric_dict = copy.deepcopy(metric_dict)
    #TODO actually make this happen reading data in
    for m in metric_dict:
        if (not m == 'METADATA') and ('DERIVED' not in m):
            metric_dict[m].index = metric_dict[m].index.droplevel('context')
    
    alldata = metric_dict['PAPI_TOT_CYC'].copy().drop(['Calls','Subcalls',todrop,'ProfileCalls'], axis=1)
    alldata['PAPI_TOT_CYC'] = alldata[inc_exc]
    alldata.drop([inc_exc],axis=1,inplace=True)

    for x in metric_dict.keys():
        if x in ['PAPI_TOT_CYC','METADATA']: continue
        alldata[x] = metric_dict[x][inc_exc]
    return alldata
                  

############################################################################################

#                                   Printing and plotting data

############################################################################################

def print_metadata(data):
    
    for key in data['METADATA']:
        print('{:50} {}'.format(key,data['METADATA'][key] ))


def print_available_metrics(data, scaling=False):
    if not scaling:
        for key in data:
            if not key == 'METADATA':
                print(key)
    else:
        for key in data[data.keys()[0]]:
            if not key == 'METADATA':
                print(key)

def set_chart_font_size(fntsize):
    font = {'size'   : fntsize}; matplotlib.rc('font', **font)

def bar_chart(dfs,x='region',y='Inclusive',size=(15,7)):
    fig, ax = plt.subplots(figsize=size)
    dfs.plot(ax = ax, kind='bar')
    return fig

def highlight_max(data, color='yellow'):
    '''
    highlight the maximum in a Series or DataFrame
    '''
    attr = 'background-color: {}'.format(color)
    if data.ndim == 1:  # Series from .apply(axis=0) or axis=1
        is_max = data == data.max()
        return [attr if v else '' for v in is_max]
    else:  # from .apply(axis=None)
        is_max = data == data.max().max()
        return pd.DataFrame(np.where(is_max, attr, ''),
                            index=data.index, columns=data.columns)
    
def highlight(df, fmt="{:.2%}", ht=0.5, hcolor='yellow'):
    return df.style.format(fmt).apply(lambda x: ["background: %s" % hcolor if v >= ht else "" for v in x], axis = 1)

def highlight_higher(x):
    return ["background: yellow" if v > 0.8 else "" for v in x]

def select_metric_from_scaling(scale_data, metric):
    '''
    returns a single level dictionary with just the requested metric
    dictionary keys are the thread counts
    '''

    metric_data = {}
    for kt in scale_data:
        try:
            metric_data[kt] = scale_data[kt][metric]
        except:
            print ("ERROR getting %s for thread %d" % (metric, kt))

    return metric_data

def scaling_plot(data, inclusive=True, plot=True, function="\[SUMMARY\] .TAU application$", metric='PAPI_TOT_CYC', max=False):
    '''
    data is the whole scaling data
    function is what to search in the call-path please use regular functions
        default looks at the whole application
    metric is the metric to plot

    returns lists of threads and metrics per thread (i.e. data to plot)
    '''
    if inclusive: which='Inclusive'
    else: which='Exclusive'

    metric_data = select_metric_from_scaling(data, metric)
    thread_list  = sorted(metric_data.keys())
    if max:
        data_list = [metric_data[kt][metric_data[kt].index.get_level_values('region').str.contains(function)][which].max() for kt in thread_list]
    else:
        # cause TAU has 2 of everything average is half
        data_list = [metric_data[kt][metric_data[kt].index.get_level_values('region').str.contains(function)][which].sum()/(2*kt) for kt in thread_list]
    
    if plot: plt = matplotlib.pyplot.plot(thread_list, data_list)

    return thread_list, data_list


def thread_bar_plots(data_dict, t_list, y=-1):
    for kt in t_list:
        print ("Thread Count: %d" % kt)
        data = list(data_dict[kt])
        matplotlib.pyplot.bar(range(len(data)), data)
        if y != -1:
            matplotlib.pyplot.ylim(ymax=y)
        matplotlib.pyplot.show()


def get_thread_level_metric_scaling(_data, inclusive=True, metric='NONE'):
    '''
    data is a single metric scaling dictionary
    returns a dictionary of panda series 
    '''

    if metric=='NONE':
        data = _data
    else:
        data = select_metric_from_scaling(_data, metric) 

    metric_data = {}
    for kt in data:
        metric_data[kt] = get_thread_level_metric(data[kt],inclusive=inclusive)
    return metric_data

def get_thread_level_metric(data, inclusive=True):
    '''
    data is a panda dataframe of one metric and one thread count
    returns a panda series of the metric summed over each thread
    note: for certain derived metrics (i.e. ratios) this won't work because it sums
    '''
    if inclusive: which='Inclusive'
    else: which='Exclusive'
    metric_list = data.groupby(['thread'])[which].sum()
    return metric_list


def get_func_level_metric(data, inclusive=False, avg=True, func = 'NULL'):
    '''
    data is a panda dataframe of one metric and one thread count
    returns a panda series of the metric averaged or summed over each thread
    note: for certain derived metrics (i.e. ratios) this won't work because it sums
    
    TODO add filtering option data[n_thr] = filter_libs_out(data[n_thr])
    '''
    if inclusive: which='Inclusive'
    else: which='Exclusive'
        
    group_data = data.groupby(['region'])[[which]]

    if avg:
        metric_list = group_data.mean().sort_values(by=which,ascending=False)[[which]]
    else:
        metric_list = group_data.sum().sort_values(by=which,ascending=False)[[which]]

    if not func == 'NULL':
        metric_list = metric_list[metric_list.index.get_level_values('region').str.contains(func)][[which]]

    return metric_list


def get_corr(alldata, method='pearson', metrics=['PAPI_TOT_INS','PAPI_TOT_CYC'], sort='PAPI_TOT_CYC'):
    correlations = alldata.corr(method).fillna(0)[metrics]    # Other methods: 'kendall', 'spearman'
    correlations.insert(0, 'Metric',pd.Series(METRIC_NAMES))
    fmt = correlations.select_dtypes(exclude=['object']).style.format("{:.2%}").background_gradient(cmap=cm)
    return correlations

def get_full_app_metric(data, inclusive=True, avg=True, func = 'application'):
    '''
    data is a panda dataframe of one metric and one thread count
    returns a panda series of the metric averaged or summed over each thread
    note: for certain derived metrics (i.e. ratios) this won't work because it sums
    
    TODO add filtering option data[n_thr] = filter_libs_out(data[n_thr])
    '''
    if inclusive: which='Inclusive'
    else: which='Exclusive'
        
    group_data = data.groupby(['region'])[[which]]

    if avg:
        metric_list = group_data.mean().sort_values(by=which,ascending=False)[[which]]
    else:
        metric_list = group_data.sum().sort_values(by=which,ascending=False)[[which]]

    if not func == 'NULL':
        metric_list = metric_list[metric_list.index.get_level_values('region').str.endswith(func)][[which]]

    return metric_list


############################################################################################

#                                   Hotspots and related filtering functions

############################################################################################


def filter_libs_out(dfs):
    dfs_filtered = dfs.groupby(level='region').filter(lambda x: ('=>' not in x.name) \
                                                                and ('_kmp' not in x.name)\
                                                                and ('tbb' not in x.name)\
                                                                and ('syscall' not in x.name)\
                                                                and ('.so' not in x.name)\
                                                                and (' __pthread' not in x.name)\
                                                                and ('std::' not in x.name)\
                                                                )
    return dfs_filtered

def largest_stddev(dfs,n):
    return dfs['Exclusive'].groupby(level=region).std(ddof=0).dropna().sort_values(ascending=False, axis=0)[:n]

def largest_correlation(dfs,n):
    unstacked_dfs = dfs.unstack(region)
    return unstacked_dfs.loc[:,'Exclusive'].corrwith(unstacked_dfs.loc[:,('Inclusive','.TAU application')]).sort_values(ascending=False, axis=0)[:n]

def largest_exclusive(dfs,n):
    return dfs['Exclusive'].groupby(level='region').max().nlargest(n)

def largest_inclusive(dfs,n):
    return dfs['Inclusive'].groupby(level='region').max().nlargest(n)

def means(dfs, inclusive=True, sort=True, plot=False):
    if inclusive: which='Inclusive'
    else: which='Exclusive'
    temp = dfs.groupby('region')[which].sum().reset_index().groupby('region').mean()
    if sort: temp = temp.sort_values(by=which,ascending=False)
    if plot: bar_chart(temp)
    return temp

def thread_stddev(dfs, inclusive=True, sort=True, plot=False):
    if inclusive: which='Inclusive'
    else: which='Exclusive'
    temp = dfs.groupby(['thread','region'])[which].sum().reset_index().groupby(['thread']).std()
    if plot: bar_chart(temp)
    if sort: return temp.sort_values(by=which,ascending=False)
    else: return temp

def thread_variance(dfs, inclusive=True, sort=True, plot=False):
    if inclusive: which='Inclusive'
    else: which='Exclusive'
    temp = dfs.groupby(['thread','region'])[which].sum().reset_index().groupby(['thread']).var()
    if plot: bar_chart(temp)
    if sort: return temp.sort_values(by=which,ascending=False)

def hotspots(dfs, n, flag):
    if flag == 0:
        largest = largest_exclusive(dfs,n)
    elif flag == 1:
        largest = largest_inclusive(dfs,n)
    elif flag == 2:
        largest = largest_stddev(dfs,n)
    elif flag == 3:
        largest = largest_correlation(dfs,n)
    else:
        print('Invalid flag')
    y = ['exclusive time', 'inclusive time', 'standard deviation', 'correlation to total runtime']
    print('Hotspot Analysis Summary')
    print('='*80)
    print('The code regions with largest %s are: ' %y[flag])
    for i in xrange(0,n):
        try:
            print('%s: %s (%s)' %(i+1, largest.index[i], largest[i]))
        except:
            break

def get_hotspots(metric,n=10):
    print('selected metric: %s\n' %metric)
    hotspots(expr_intervals[metric], n, 1)
    
    print('='*80)
    
    filtered_dfs = filter_libs_out(expr_intervals[metric])
    hotspots(filtered_dfs, n, 1)


############################################################################################

#                                   Stuff that was supposed to print prety tables

############################################################################################

# UTILITIES (NOT WORKING)
# TODO make this work

# using something like head() in panda will probably be better
# or to_html()
# This is where useful functions go. Currently includes:

# table printing

# from IPython.core.display import display, HTML, display_html

# def parse_region(region):
#     _location_re = re.compile(r'\{(.*)\} {(\d+),(\d+)}-{(\d+),(\d+)}')
#     func = region.split('=>')[-1]
#     loc = re.search(r'\[(.*)\]', func)
#     if loc:
#         location = loc.group(1)
#         match = _location_re.match(location)
#         if match:
#             return match.group(1)
#     if '[SAMPLE]' in func:
#         loc = re.search(r'\[\{(.*)\} \{(\d+)\}\]', func)
#         if loc:
#             return loc.group(1)

# def add_link(multiindex):
#     link = parse_region(multiindex[4])
#     if link:
#         return (multiindex[0],multiindex[1],multiindex[2],multiindex[3],'<a href="{0}">{1}</a>'.format((link), multiindex[4]))
#     else:
#         return multiindex

    
# def print_table(intervals):
#     '''
#     intervals is a panda with a metric's data
#     '''
#     expr_intervals_link = intervals.copy()
#     expr_intervals_link.index = expr_intervals_link.index.map(lambda x: add_link(x))
#     HTML(expr_intervals_link.to_html(escape=False))

    
# metric='PAPI_TOT_CYC'
# print_table(expr_intervals[metric])
# expr_intervals_link = expr_intervals[metric].copy()
# expr_intervals_link.index = expr_intervals_link.index.map(lambda x: add_link(x))
# HTML(expr_intervals_link.to_html(escape=False))
