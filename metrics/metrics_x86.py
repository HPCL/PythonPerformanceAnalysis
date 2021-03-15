'''
functions to add derived metrics to the dictionaries of metrics

please use the examples to add more

Existing list of prewritten metrics:
add_MEM_BOUND_FRACTIONS(metrics) - fraction of stalls associated with mem boundedness
add_BW_BOUND_FRACTIONS(metrics)  - fraction of mem bound stalls associated with BW bound
    -- note the above two add multiple metrics
add_IPC(metrics)                 - Instructions per Cycle
add_CPI(metrics)                 - Cycles per instruction
add_VIPC(metrics)                - vector instructions per cycle
add_VIPI(metrics)                - vector instructions per instruction (i.e. fraction of total)
add_L1_missrate(metrics)         - miss rate for L1 cache
add_DERIVED_BRANCH_MR(metrics)   - fraction of miss predicted branches 

add_DERIVED_RATIO_FETCH_STL_TOT_CYC(metrics)

'''


def add_MEM_BOUND_FRACTIONS(metrics):
    '''

    '''
    TOT_CYC  = 'PAPI_TOT_CYC'
    STL_ALL  = 'PAPI_NATIVE_RESOURCE_STALLS:ALL'
    STL_SB   = 'PAPI_NATIVE_RESOURCE_STALLS:SB'
#     L1D_PEND = 'PAPI_NATIVE_CYCLE_ACTIVITY:CYCLES_L1D_PENDING'
    L1D_PEND = 'PAPI_NATIVE_CYCLE_ACTIVITY:STALLS_L1D_MISS' # might be thisnot sure yet


    if(not (metrics.has_key(TOT_CYC) \
            and metrics.has_key(STL_ALL) \
            and metrics.has_key(STL_SB) \
            and metrics.has_key(L1D_PEND) \
           ) ):
        print ("ERROR adding MEM_BOUND_FRACTIONS to metric dictionary")
        return False
    
    stl_all  = metrics[STL_ALL].copy()
    stl_sb   = metrics[STL_SB].copy()
    l1d_pend = metrics[L1D_PEND].copy()
    cyc   = metrics[TOT_CYC].copy()
    
    stl_all.index = stl_all.index.droplevel('context')
    stl_sb.index  = stl_sb.index.droplevel('context')
    l1d_pend.index  = l1d_pend.index.droplevel('context')
    cyc.index   = cyc.index.droplevel('context')

    ustl_all  = stl_all.unstack()
    ustl_sb = stl_sb.unstack()
    ul1d_pend = l1d_pend.unstack()
    ucyc   = cyc.unstack()

#     metrics['DERIVED_MEM_BOUND_FRACTION'] = ( max(ul1d_pend,ustl_sb)/(ustl_all) ).stack()
    metrics['DERIVED_L1D_PEND_FRACTION'] = ( ul1d_pend/ustl_all ).stack()
    metrics['DERIVED_STL_SB_FRACTION'] = ( ustl_sb/ustl_all ).stack()

    return True


def add_BW_BOUND_FRACTIONS(metrics):
    '''

    '''
    TOT_CYC  = 'PAPI_TOT_CYC'
    STL_ALL  = 'PAPI_NATIVE_RESOURCE_STALLS:ALL'
    STL_SB   = 'PAPI_NATIVE_RESOURCE_STALLS:SB'
    SQ_FULL  = 'PAPI_NATIVE_OFFCORE_REQUESTS_BUFFER:SQ_FULL'
    FB_FULL  = 'PAPI_NATIVE_L1D_PEND_MISS:FB_FULL'
    


    if(not (metrics.has_key(TOT_CYC) \
            and metrics.has_key(STL_ALL) \
            and metrics.has_key(STL_SB) \
            and metrics.has_key(SQ_FULL) \
            and metrics.has_key(FB_FULL) \
           ) ):
        print ("ERROR adding BW_BOUND_FRACTIONS to metric dictionary")
        return False
    
    stl_all  = metrics[STL_ALL].copy()
    stl_sb   = metrics[STL_SB].copy()
    sq_full  = metrics[SQ_FULL].copy()
    fb_full  = metrics[FB_FULL].copy()
    cyc   = metrics[TOT_CYC].copy()
       
    stl_all.index = stl_all.index.droplevel('context')
    stl_sb.index  = stl_sb.index.droplevel('context')
    sq_full.index = sq_full.index.droplevel('context')
    fb_full.index  = fb_full.index.droplevel('context')
    cyc.index   = cyc.index.droplevel('context')

    ustl_all  = stl_all.unstack()
    ustl_sb = stl_sb.unstack()
    usq_full  = sq_full.unstack()
    ufb_full = fb_full.unstack()
    ucyc   = cyc.unstack()

#     metrics['DERIVED_MEM_BOUND_FRACTION'] = ( max(ul1d_pend,ustl_sb)/(ustl_all) ).stack()
    metrics['DERIVED_SQ_FB_FULL_FRACTION'] = ( (usq_full+ufb_full)/ustl_all ).stack()
    metrics['DERIVED_STL_SB_FRACTION'] = ( ustl_sb/ustl_all ).stack()

    return True





def add_VIPC(metrics):
    '''
    add vector instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    CYC = 'PAPI_TOT_CYC'
    VEC = 'PAPI_NATIVE_UOPS_RETIRED:PACKED_SIMD'
    

    if(not (metrics.has_key(CYC) and metrics.has_key(VEC)) ):
        print ("ERROR adding VecEfficiency to metric dictionary")
        return False
    
    vec = metrics[VEC].copy()
    cyc = metrics[CYC].copy()
    vec.index = vec.index.droplevel('context')
    cyc.index = cyc.index.droplevel('context')

    uvec = vec.unstack()
    ucyc = cyc.unstack()

    metrics['DERIVED_VIPC'] = (uvec / ucyc).stack()

    return True

def add_VIPI(metrics):
    '''
    add vector instructions per ins to the metrics dictionary
    returns true if successful
    '''
    INS = 'PAPI_TOT_INS'
    VEC = 'PAPI_NATIVE_UOPS_RETIRED:PACKED_SIMD'
    

    if(not (metrics.has_key(INS) and metrics.has_key(VEC)) ):
        print ("ERROR adding VecEfficiency to metric dictionary")
        return False
    
    vec = metrics[VEC].copy()
    ins = metrics[INS].copy()
    vec.index = vec.index.droplevel('context')
    ins.index = ins.index.droplevel('context')

    uvec = vec.unstack()
    uins = ins.unstack()

    metrics['DERIVED_VIPI'] = (uvec / uins).stack()

    return True


def add_DERIVED_SP_VOPO(metrics):
    if (not metrics.has_key('PAPI_SP_OPS')):
        print ('ERROR adding DERIVED_SP_VOPO to metric dictionary')
        return False
    a0 = metrics['PAPI_SP_OPS'].copy()
    a0.index = a0.index.droplevel('context')
    u0 = a0.unstack()
    if (not metrics.has_key('PAPI_NATIVE_FP_ARITH:128B_PACKED_SINGLE')):
        print ('ERROR adding DERIVED_SP_VOPO to metric dictionary')
        return False
    a1 = metrics['PAPI_NATIVE_FP_ARITH:128B_PACKED_SINGLE'].copy()
    a1.index = a1.index.droplevel('context')
    u1 = a1.unstack()
    if (not metrics.has_key('PAPI_NATIVE_FP_ARITH:256B_PACKED_SINGLE')):
        print ('ERROR adding DERIVED_SP_VOPO to metric dictionary')
        return False
    a2 = metrics['PAPI_NATIVE_FP_ARITH:256B_PACKED_SINGLE'].copy()
    a2.index = a2.index.droplevel('context')
    u2 = a2.unstack()
    metrics['DERIVED_SP_VOPO'] = ((u1 + u2) / (u0 )).stack()

    return True


def add_L1_missrate(metrics, lst=True):
    '''
    add Instructions per cycle to the metrics dictionary
    lst is if it should use lst ins instead of L1
    returns true if successful
    '''
    if lst:
        LST = 'PAPI_LST_INS' # total load store
    else:
        LST = 'PAPI_L1_TCA' # total load store
        
    L1M = 'PAPI_L1_TCM'  # L1 misses
    
    if(not (metrics.has_key(LST) and metrics.has_key(L1M)) ):
        print ("ERROR adding L1 MR to metric dictionary")
        return False
        
    access = metrics[LST].copy()
    misses = metrics[L1M].copy()
    access.index = access.index.droplevel('context')
    misses.index = misses.index.droplevel('context')    
        
    
    uaccess = access.unstack()
    umisses = misses.unstack()

    metrics['DERIVED_L1_MISSRATE'] = (umisses / uaccess).stack()
        
        
    return True

def add_L2_missrate(metrics, req=False):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''
    L2M = 'PAPI_L2_TCM' # total load store
    if req:
        L2A = 'PAPI_NATIVE_L2_RQSTS:REFERENCES'  # L2 accesses
    else:
        L2A = 'PAPI_L2_TCA'  # L2 accesses
    
    if(not (metrics.has_key(L2A) and metrics.has_key(L2M)) ):
        print ("ERROR adding L2 MR to metric dictionary")
        return False
        
    access = metrics[L2A].copy()
    misses = metrics[L2M].copy()
    access.index = access.index.droplevel('context')
    misses.index = misses.index.droplevel('context')    
        
    uaccess = access.unstack()
    umisses = misses.unstack()

    metrics['DERIVED_L2_MISSRATE'] = (umisses / uaccess).stack()
        
    return True


def add_L3_missrate(metrics, llc=False):
    '''
    add Instructions per cycle to the metrics dictionary
    returns true if successful
    '''

    if llc:
        L3A = 'PAPI_NATIVE_LLC_REFERENCES' # total load store
        L3M = 'PAPI_NATIVE_LLC_MISSES'  # L1 misses
    else:
        L3A = 'PAPI_L3_TCA' # total load store
        L3M = 'PAPI_L3_TCM'  # L1 misses
    
    if(not (metrics.has_key(L3A) and metrics.has_key(L3M)) ):
        print ("ERROR adding L3 MR to metric dictionary")
        return False
        
    access = metrics[L3A].copy()
    misses = metrics[L3M].copy()
    access.index = access.index.droplevel('context')
    misses.index = misses.index.droplevel('context')    
        
    
    uaccess = access.unstack()
    umisses = misses.unstack()

    metrics['DERIVED_L3_MISSRATE'] = (umisses / uaccess).stack()
        
        
    return True


def add_DERIVED_RATIO_FETCH_STL_TOT_CYC(metrics):
    if (not metrics.has_key('PAPI_NATIVE_FETCH_STALL')):
        print ('ERROR adding DERIVED_RATIO_FETCH_STL_TOT_CYC to metric dictionary')
        return False
    a0 = metrics['PAPI_NATIVE_FETCH_STALL'].copy()
    a0.index = a0.index.droplevel('context')
    u0 = a0.unstack()
    if (not metrics.has_key('PAPI_TOT_CYC')):
        print ('ERROR adding DERIVED_RATIO_FETCH_STL_TOT_CYC to metric dictionary')
        return False
    a1 = metrics['PAPI_TOT_CYC'].copy()
    a1.index = a1.index.droplevel('context')
    u1 = a1.unstack()
    metrics['DERIVED_RATIO_FETCH_STL_TOT_CYC'] = (u0 / u1).stack()

    return True


def add_DERIVED_OTHER_INS(metrics):
    '''
    add a count of 'other' instructions to the metrics dictionary
    other meaning not LST, SIMD, or FLOP (all doubles for now)
    useful for pie charts
    returns true if successful
    '''
    TOT  = 'PAPI_TOT_INS'
    LST  = 'PAPI_LST_INS'
    V128 = 'PAPI_NATIVE_FP_ARITH_INST_RETIRED:128B_PACKED_DOUBLE'
    V256 = 'PAPI_NATIVE_FP_ARITH_INST_RETIRED:256B_PACKED_DOUBLE'
    V512 = 'PAPI_NATIVE_FP_ARITH_INST_RETIRED:512B_PACKED_DOUBLE'
    SFLP = 'PAPI_NATIVE_FP_ARITH_INST_RETIRED:SCALAR_DOUBLE'
    

    if(not (metrics.has_key(TOT)\
            and metrics.has_key(LST)\
            and metrics.has_key(V128)\
            and metrics.has_key(V256)\
            and metrics.has_key(V512)\
            and metrics.has_key(SFLP)\
           ) ):
        print ("ERROR adding DERIVED_OTHER_INS to metric dictionary")
        return False
    
    tot  = metrics[TOT].copy()
    lst  = metrics[LST].copy()
    v128 = metrics[V128].copy()
    v256 = metrics[V256].copy()
    v512 = metrics[V512].copy()
    sflop = metrics[SFLP].copy()
    
    tot.index = tot.index.droplevel('context')
    lst.index  = lst.index.droplevel('context')
    v128.index  = v128.index.droplevel('context')
    v256.index  = v256.index.droplevel('context')
    v512.index = v512.index.droplevel('context')
    sflop.index = sflop.index.droplevel('context')

    utot = tot.unstack()
    ulst  = lst.unstack()
    uv128  = v128.unstack()
    uv256  = v256.unstack()
    uv512 = v512.unstack()
    usflop = sflop.unstack()

    metrics['DERIVED_OTHER_INS'] = (utot - (ulst + uv128 + uv256 + uv512 + usflop)).stack()

    return True




############################################################################################

#                                   Metrics for BW stuff

############################################################################################


def add_LST_CYC_RATE(metrics):
    '''
    the ratio of loads and stores to total cycles
    intended to be a proxy for memory BW
    '''
    CYC = 'PAPI_TOT_CYC'
    LST = 'PAPI_LST_INS'
    

    if(not (metrics.has_key(CYC) and metrics.has_key(LST)) ):
        print ("ERROR adding DERIVED_LST_CYC_RATE to metric dictionary")
        return False
    
    lst = metrics[LST].copy()
    cyc = metrics[CYC].copy()
    lst.index = lst.index.droplevel('context')
    cyc.index = cyc.index.droplevel('context')

    ulst = lst.unstack()
    ucyc = cyc.unstack()

    metrics['DERIVED_LST_CYC_RATE'] = (ulst / ucyc).stack()

    return True

def add_TCM3_CYC_RATE(metrics):
    '''
    the ratio of memory access (L3 misses) to total cycles
    intended to be a proxy for BW
    '''
    CYC = 'PAPI_TOT_CYC'
    LST = 'PAPI_L3_TCM'
    

    if(not (metrics.has_key(CYC) and metrics.has_key(LST)) ):
        print ("ERROR adding DERIVED_TCM3_CYC_RATE to metric dictionary")
        return False
    
    lst = metrics[LST].copy()
    cyc = metrics[CYC].copy()
    lst.index = lst.index.droplevel('context')
    cyc.index = cyc.index.droplevel('context')

    ulst = lst.unstack()
    ucyc = cyc.unstack()

    metrics['DERIVED_TCM3_CYC_RATE'] = (ulst / ucyc).stack()

    return True


def add_OFF_REQ_RATE(metrics):
    '''
    the ratio of memory access (L3 misses) to total cycles
    intended to be a proxy for BW
    '''
    CYC = 'PAPI_TOT_CYC'
    LST = 'PAPI_NATIVE_OFFCORE_REQUESTS:ALL_REQUESTS'
    

    if(not (metrics.has_key(CYC) and metrics.has_key(LST)) ):
        print ("ERROR adding OFF_REQ_RATE to metric dictionary")
        return False
    
    lst = metrics[LST].copy()
    cyc = metrics[CYC].copy()
    lst.index = lst.index.droplevel('context')
    cyc.index = cyc.index.droplevel('context')

    ulst = lst.unstack()
    ucyc = cyc.unstack()

    metrics['DERIVED_OFF_REQ_RATE'] = (ulst / ucyc).stack()

    return True




def add_MEM_UOPS_RATE(metrics):
    '''
    the ratio of memory access (L3 misses) to total cycles
    intended to be a proxy for BW
    '''
    CYC = 'PAPI_TOT_CYC'
    LD  = 'PAPI_NATIVE_MEM_UOPS_RETIRED:ALL_LOADS'
    ST  = 'PAPI_NATIVE_MEM_UOPS_RETIRED:ALL_STORES'
    

    if(not (metrics.has_key(CYC) and metrics.has_key(LD) and metrics.has_key(ST)) ):
        print ("ERROR adding MEM_UOPS_RATE to metric dictionary")
        return False
    
    ld  = metrics[LD].copy()
    st  = metrics[ST].copy()
    cyc = metrics[CYC].copy()
    ld.index = ld.index.droplevel('context')
    st.index = st.index.droplevel('context')
    cyc.index = cyc.index.droplevel('context')

    uld  = ld.unstack()
    ust  = st.unstack()
    ucyc = cyc.unstack()

    metrics['DERIVED_MEM_UOPS_RATE'] = ((uld+ust) / ucyc).stack()

    return True



def add_IMC_CAS_COUNT_RATE(metrics):
    '''
    '''
    CYC  = 'PAPI_TOT_CYC'
    IMC0 = 'PAPI_NATIVE_UNC_M_CAS_COUNT:ALL:cpu=0'
    

    if(not (metrics.has_key(CYC) \
            and metrics.has_key(IMC0) \
           ) ):
        print ("ERROR adding IMC_CAS_COUNT_RATE to metric dictionary")
        return False
    
    imc0 = metrics[IMC0].copy()
    cyc  = metrics[CYC].copy()
    imc0.index = imc0.index.droplevel('context')
    cyc.index  = cyc.index.droplevel('context')

    uimc0 = imc0.unstack()
    ucyc  = cyc.unstack()

#     metrics['DERIVED_IMC_CAS_COUNT_RATE'] = ((uimc0*64) ).stack()
    metrics['DERIVED_IMC_CAS_COUNT_RATE'] = ((uimc0*64*2101000000) /(ucyc*1000000) ).stack()

    return True


    
    

def add_LOAD_DRAM_RATE(metrics):
    '''
    the ratio of memory access (L3 misses) to total cycles
    intended to be a proxy for BW
    '''
    CYC = 'PAPI_TOT_CYC'
    LOC  = 'PAPI_NATIVE_MEM_LOAD_UOPS_L3_MISS_RETIRED:LOCAL_DRAM'
    REM  = 'PAPI_NATIVE_MEM_LOAD_UOPS_L3_MISS_RETIRED:REMOTE_DRAM'
    

    if(not (metrics.has_key(CYC) and metrics.has_key(LOC) and metrics.has_key(REM)) ):
        print ("ERROR adding LOAD_DRAM_RATE to metric dictionary")
        return False
    
    loc = metrics[LOC].copy()
    rem = metrics[REM].copy()
    cyc = metrics[CYC].copy()
    loc.index = loc.index.droplevel('context')
    rem.index = rem.index.droplevel('context')
    cyc.index = cyc.index.droplevel('context')

    uloc  = loc.unstack()
    urem  = rem.unstack()
    ucyc = cyc.unstack()

    metrics['DERIVED_LOAD_DRAM_RATE'] = ((uloc+urem) / ucyc).stack()

    return True


def add_MEM_TRANS_RATE(metrics):
    '''
    the ratio of memory access (L3 misses) to total cycles
    intended to be a proxy for BW
    '''
    CYC = 'PAPI_TOT_CYC'
    MEM = 'PAPI_NATIVE_MEM_TRANS_RETIRED'
    

    if(not (metrics.has_key(CYC) and metrics.has_key(MEM)) ):
        print ("ERROR adding MEM_TRANS_RATE to metric dictionary")
        return False
    
    mem = metrics[MEM].copy()
    cyc = metrics[CYC].copy()
    mem.index = mem.index.droplevel('context')
    cyc.index = cyc.index.droplevel('context')

    umem = mem.unstack()
    ucyc = cyc.unstack()

    metrics['DERIVED_MEM_TRANS_RATE'] = (umem / ucyc).stack()

    return True



def add_MEM_STL_RATES(metrics):
    '''
    the ratio of memory access (L3 misses) to total cycles
    intended to be a proxy for BW
    '''
    CYC  = 'PAPI_TOT_CYC'
    MCYC = 'PAPI_NATIVE_CYCLE_ACTIVITY:CYCLES_MEM_ANY'
    MSTL = 'PAPI_NATIVE_CYCLE_ACTIVITY:STALLS_MEM_ANY'
    

    if(not (metrics.has_key(CYC) and metrics.has_key(MCYC) and metrics.has_key(MSTL)) ):
        print ("ERROR adding MEM_STL_RATES to metric dictionary")
        return False
    
    mcyc = metrics[MCYC].copy()
    mstl = metrics[MSTL].copy()
    cyc = metrics[CYC].copy()
    mcyc.index = mcyc.index.droplevel('context')
    mstl.index = mstl.index.droplevel('context')
    cyc.index = cyc.index.droplevel('context')

    umcyc = mcyc.unstack()
    umstl = mstl.unstack()
    ucyc = cyc.unstack()

    metrics['DERIVED_MEM_STL_TOT_RATE'] = (umstl / ucyc).stack()
    metrics['DERIVED_MEM_STL_MEM_RATE'] = (umstl / umcyc).stack()

    return True


