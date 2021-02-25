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



############################################################################################

#                                   Metrics for Top Down Method

############################################################################################


def add_TOP_DOWN_FRACTIONS_1(metrics):
    '''

    '''
    TOT_CYC  = 'PAPI_TOT_CYC'
    TOT_INS  = 'PAPI_TOT_INS'
    STL_BE   = 'PAPI_NATIVE_STALL_BACKEND'
    STL_FE   = 'PAPI_NATIVE_STALL_FRONTEND'
    UOPS_RET = 'PAPI_NATIVE_INST_RETIRED'

    if(not (metrics.has_key(TOT_CYC) \
            and metrics.has_key(TOT_INS) \
            and metrics.has_key(STL_BE) \
            and metrics.has_key(STL_FE) \
            and metrics.has_key(UOPS_RET) \
           ) ):
        print ("ERROR adding TOP_DOWN_FRACTIONS_1 to metric dictionary")
        return False
    
    tot_cyc   = metrics[TOT_CYC].copy()
    tot_ins   = metrics[TOT_INS].copy()
    stl_be    = metrics[STL_BE].copy()
    stl_fe    = metrics[STL_FE].copy()
    uops_ret  = metrics[UOPS_RET].copy()
    
    tot_cyc.index  = tot_cyc.index.droplevel('context')
    tot_ins.index  = tot_ins.index.droplevel('context')
    stl_be .index  = stl_be .index.droplevel('context')
    stl_fe.index   = stl_fe.index.droplevel('context')
    uops_ret.index = uops_ret.index.droplevel('context')

    utot_cyc  = tot_cyc.unstack()
    utot_ins  = tot_ins.unstack()
    ustl_be   = stl_be .unstack()
    ustl_fe   = stl_fe.unstack()
    uuops_ret = uops_ret.unstack()

    metrics['DERIVED_FRONT_FRACTION']    = ( ustl_fe/(4*utot_cyc) ).stack()
    metrics['DERIVED_BACK_FRACTION']     = ( ustl_be/(4*utot_cyc) ).stack()
    metrics['DERIVED_BAD_SPEC_FRACTION'] = ( (utot_ins-uuops_ret)/(4*utot_cyc) ).stack()
    metrics['DERIVED_RETIRED_FRACTION']  = ( uuops_ret/(4*utot_cyc) ).stack()

    return True



# TODO use arm counters
def add_TOP_DOWN_FRACTIONS_2(metrics):
    '''

    '''
    TOT_CYC = 'PAPI_TOT_CYC'    
    TOT_STL = 'PAPI_NATIVE_CYCLE_ACTIVITY:STALLS_TOTAL'
    MEM_STL = 'PAPI_NATIVE_CYCLE_ACTIVITY:STALLS_MEM_ANY'
    SB_STL  = 'PAPI_NATIVE_RESOURCE_STALLS:SB'
    
    
    if(not (metrics.has_key(TOT_CYC) \
            and metrics.has_key(TOT_STL) \
            and metrics.has_key(MEM_STL) \
            and metrics.has_key(SB_STL) \
           ) ):
        print ("ERROR adding TOP_DOWN_FRACTIONS_2 to metric dictionary")
        return False
    
    tot_cyc  = metrics[TOT_CYC].copy()
    tot_stl  = metrics[TOT_STL].copy()
    mem_stl  = metrics[MEM_STL].copy()
    sp_stl   = metrics[SB_STL].copy()
    
    tot_cyc.index  = tot_cyc.index.droplevel('context')
    tot_stl.index  = tot_stl.index.droplevel('context')
    mem_stl.index  = mem_stl.index.droplevel('context')
    sp_stl.index   = sp_stl.index.droplevel('context')

    utot_cyc  = tot_cyc.unstack()
    utot_stl  = tot_stl.unstack()
    umem_stl  = mem_stl.unstack()
    usp_stl   = sp_stl.unstack()

    metrics['DERIVED_MEM_FRACTION']  = ( (umem_stl+usp_stl)/(utot_cyc) ).stack()
    metrics['DERIVED_CORE_FRACTION'] = ( (utot_stl - (umem_stl+usp_stl))/(utot_cyc) ).stack()

    return True


