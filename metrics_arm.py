'''
functions to add derived metrics to the dictionaries of metrics

please use the examples to add more

Existing list of prewritten metrics:
'''




from utilities import *




def add_DERIVED_OTHER_INS(metrics):
    '''

    '''
    TOT = 'PAPI_NATIVE_INST_SPEC'
    LD  = 'PAPI_LD_INS'
    ST  = 'PAPI_SR_INS'
    FP  = 'PAPI_FP_INS'
    VEC = 'PAPI_VEC_INS'
    BR  = 'PAPI_BR_INS'
    

    if(not (metrics.has_key(TOT)\
            and metrics.has_key(LD)\
            and metrics.has_key(ST)\
            and metrics.has_key(FP)\
            and metrics.has_key(VEC)\
            and metrics.has_key(BR)\
           ) ):
        print ("ERROR adding DERIVED_OTHER_INS to metric dictionary")
        return False
    
    tot = metrics[TOT].copy()
    ld  = metrics[LD].copy()
    st  = metrics[ST].copy()
    fp  = metrics[FP].copy()
    vec = metrics[VEC].copy()
    br  = metrics[BR].copy()
    
    tot.index = tot.index.droplevel('context')
    ld.index  = ld.index.droplevel('context')
    st.index  = st.index.droplevel('context')
    fp.index  = fp.index.droplevel('context')
    vec.index = vec.index.droplevel('context')
    br.index  = br.index.droplevel('context')

    utot = tot.unstack()
    uld  = ld.unstack()
    ust  = st.unstack()
    ufp  = fp.unstack()
    uvec = vec.unstack()
    ubr  = br.unstack()

    metrics['DERIVED_OTHER_INS'] = (utot - (uld + ust + ufp + uvec + ubr)).stack()

    return True



def add_L2_missrate(metrics):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    L2M = 'PAPI_L2_DCM' # total load store
    L2H = 'PAPI_L2_DCH'  # L2 accesses
    
    if(not (metrics.has_key(L2H) and metrics.has_key(L2M)) ):
        print ("ERROR adding L2 MR to metric dictionary")
        return False
        
    hits = metrics[L2H].copy()
    miss = metrics[L2M].copy()
    hits.index = hits.index.droplevel('context')
    miss.index = miss.index.droplevel('context')    
        
    uhits = hits.unstack()
    umiss = miss.unstack()

    metrics['DERIVED_L2_MISSRATE'] = (umiss / (uhits+umiss)).stack()
        
    return True


def add_L1_missrate(metrics):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    L1M = 'PAPI_L1_DCM' # total load store
    L1A = 'PAPI_L1_DCA'  # L2 accesses
    
    if(not (metrics.has_key(L1A) and metrics.has_key(L1M)) ):
        print ("ERROR adding L1 MR to metric dictionary")
        return False
        
    acc = metrics[L1A].copy()
    miss = metrics[L1M].copy()
    acc.index = acc.index.droplevel('context')
    miss.index = miss.index.droplevel('context')    
        
    uacc = acc.unstack()
    umiss = miss.unstack()

    metrics['DERIVED_L1_MISSRATE'] = (umiss / (uacc)).stack()
        
    return True


