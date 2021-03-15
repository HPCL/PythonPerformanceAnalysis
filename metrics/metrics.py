'''
functions to add derived metrics to the dictionaries of metrics

please use the examples to add more

Existing list of prewritten metrics:
add_IPC(metrics)                - Instructions per Cycle
add_CPI(metrics)                - Cycles per instruction
add_VIPC(metrics)               - vector instructions per cycle
add_VIPI(metrics)               - vector instructions per instruction (i.e. fraction of total)
add_L1_missrate(metrics)        - miss rate for L1 cache
add_DERIVED_BRANCH_MR(metrics)  - fraction of miss predicted branches 

add_DERIVED_RATIO_FETCH_STL_TOT_CYC(metrics)

'''


def add_metric_to_scaling_data(data, metric_func, other=None):
    '''
    data is data with scaling information
    metric_func is a function pointer to one of the metric functions in this file
    '''
    results = {}
    for kthread in data:
        if other is None:
            results[kthread] = metric_func(data[kthread])
        else:
            results[kthread] = metric_func(data[kthread], other)

    for kthread in results:
        if not results[kthread]:
            print ("ERROR adding metric to thread count: " + str(kthread))




def add_IPC(metrics):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    INS = 'PAPI_TOT_INS'
    CYC = 'PAPI_TOT_CYC'
    
    if(not (metrics.has_key(INS) and metrics.has_key(CYC)) ):
        print ("ERROR adding IPC to metric dictionary")
        return False
    
    cyc = metrics['PAPI_TOT_CYC'].copy()
    ins = metrics['PAPI_TOT_INS'].copy()
    cyc.index = cyc.index.droplevel('context')
    ins.index = ins.index.droplevel('context')    
        
    
    ucyc = cyc.unstack()
    uins = ins.unstack()

    metrics['DERIVED_IPC'] = (uins / ucyc).stack()
        
        
    return True

def add_CPI(metrics):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    INS = 'PAPI_TOT_INS'
    CYC = 'PAPI_TOT_CYC'
    
    if(not (metrics.has_key(INS) and metrics.has_key(CYC)) ):
        print ("ERROR adding CPI to metric dictionary")
        return False
        
    cyc = metrics['PAPI_TOT_CYC'].copy()
    ins = metrics['PAPI_TOT_INS'].copy()
    cyc.index = cyc.index.droplevel('context')
    ins.index = ins.index.droplevel('context')    
        
    
    ucyc = cyc.unstack()
    uins = ins.unstack()

    metrics['DERIVED_CPI'] = (ucyc / uins).stack()
        
        
    return True


def add_StallPercent(metrics):
    '''
    add vector instructions per ins to the metrics dictionary
    returns true if successful
    '''
    CYC = 'PAPI_TOT_CYC'
    STL = 'PAPI_RES_STL'
    

    if(not (metrics.has_key(STL) and metrics.has_key(CYC)) ):
        print ("ERROR adding StallPercent to metric dictionary")
        return False
    
    cyc = metrics[CYC].copy()
    stl = metrics[STL].copy()
    cyc.index = cyc.index.droplevel('context')
    stl.index = stl.index.droplevel('context')

    ucyc = cyc.unstack()
    ustl = stl.unstack()

    metrics['DERIVED_STALL_PERCENT'] = (ustl / ucyc).stack()

    return True

def add_DERIVED_BRANCH_MR(metrics):
    '''
    add miss rate for branch prediction to the metrics dictionary
    returns true if successful
    '''
    if (not metrics.has_key('PAPI_BR_MSP')):
        print ('ERROR adding DERIVED_BRANCH_MR to metric dictionary')
        return False
    a0 = metrics['PAPI_BR_MSP'].copy()
    a0.index = a0.index.droplevel('context')
    u0 = a0.unstack()
    if (not metrics.has_key('PAPI_BR_CN')):
        print ('ERROR adding DERIVED_BRANCH_MR to metric dictionary')
        return False
    a1 = metrics['PAPI_BR_CN'].copy()
    a1.index = a1.index.droplevel('context')
    u1 = a1.unstack()
    metrics['DERIVED_BRANCH_MR'] = (u0 / u1).stack()

    return True



############################################################################################

#                                   Statistics and plotting

############################################################################################



def plot_metric(dfs, metric, function='', inc_exc='Inclusive', percent=False):
    # inc_exc is either Inclusive or Exclusive
    metricdf = dfs[metric]
    if function:
        metricdf_fun = metricdf.loc[metricdf.index.get_level_values('region').str.contains(function)].copy()
    else:
        metricdf_fun = metricdf.copy()
    metricdf_fun['Thread Number'] = metricdf_fun.index.get_level_values('thread')
    if percent:
        metricdf_fun.style.format({inc_exc: '{:,.2%}'.format})
    g = sns.barplot(x='Thread Number', y=inc_exc, data=metricdf_fun)
    return metricdf_fun, g

def compute_correlations(metrics_dict, inc_exc='Inclusive',highlight_threshold=0.5):
    # Compute and display pair-wise metrics correlations, highlighting the 
    # values greater than highlight_threshold.
    alldata = combine_metrics(metrics_dict,'Inclusive')
    correlations = alldata.corr()
    cm = sns.light_palette("yellow", as_cmap=True)
    correlations = correlations.style.format("{:.2%}").background_gradient(cmap=cm)
        #.apply(lambda x: ["background: yellow" if v > 0.5 else "" for v in x], axis = 1)
    return correlations





############################################################################################

#                                   functions for generating metrics

############################################################################################

def gen_metric(met_list, name):
    func = "def add_" + name + "(metrics):\n"

    for m in range(len(met_list)):

        func += "\tif (not metrics.has_key('" + met_list[m] + "')):\n"
        func += "\t\tprint 'ERROR adding " + name + " to metric dictionary'\n"
        func += "\t\treturn False"

        func += "\ta" + str(m) + " = metrics['" + met_list[m] + "'].copy()\n"
        func += "\ta" + str(m) + ".index = a" + str(m) + ".index.droplevel('context')\n"
        func += "\tu" + str(m) + " = a" + str(m) + ".unstack()\n"
    

    func += "\tmetrics[" + name + "] = " + "\"PLEASE IMPLEMENT THIS PART\"\n\n"
    func += "\treturn True\n\n\n"
        
    
    return func


def gen_metric_complete(met_list, operation, name):
    func = "def add_" + name + "(metrics):\n"

    for m in range(len(met_list)):

        func += "\tif (not metrics.has_key('" + met_list[m] + "')):\n"
        func += "\t\tprint ('ERROR adding " + name + " to metric dictionary')\n"
        func += "\t\treturn False\n"

        func += "\ta" + str(m) + " = metrics['" + met_list[m] + "'].copy()\n"
        func += "\ta" + str(m) + ".index = a" + str(m) + ".index.droplevel('context')\n"
        func += "\tu" + str(m) + " = a" + str(m) + ".unstack()\n"
    
        operation.replace(met_list[m], "u" + str(m))

    func += "\tmetrics['" + name + "'] = " + operation + "\n\n"
    func += "\treturn True\n\n\n"
        
    
    return func

