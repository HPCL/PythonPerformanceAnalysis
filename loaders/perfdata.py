"""
Data structures for TAU-generated performance data (profiles).
"""

import tempfile
import sqlite3


class NamedObject:
    def __init__(self, name=None, prefix=''):
        if not name:
            self.name = tempfile.NamedTemporaryFile(prefix=prefix)
        else:
            self.name = name


class Experiment(NamedObject)
    def __init__(self, name=None, target=None, application=None, measurement=None):
        super().__init__(name)
        self.target = target
        self.application = application
        self.Measurement = measurement


class Application(NamedObject):
    """
    The application consists of the underlying items associated with the application - whether
    the application uses MPI, OpenMP, threads, CUDA, OpenCL, TBB, etc.
    """
    def __init__(self, name=None):
        super().__init__(name)


class Target(NamedObject):
    """
    This class describes the environment where data is collected. This includes the architecture
    where the experiment is performed, its operating system, CPU architecture, interconnectivity
    fabric, compilers, and installed software.
    In general, these are things external to the Application.
    """
    def __init__(self, name):
        super().__init__(name)


class Metric(NamedObject):
    def __init__(self, name=None):
        super().__init__(name)


def open_database(filename):
    """
    Opens the mysql3 database file
    :param filename: string filename, can be relative or full path
    :return: sqlite3.Connection
    """
    conn = sqlite3.connect('tauprofile.db')
    return conn


def get_timers(conn):
    """
    Create a DataFrame with timer data.
    :param conn: a sqlite3.Connection instance
    :return: Pandas dataframe containing performance Trial data
    """


PAPI_METRIC_NAMES = {
    'PAPI_TOT_CYC': ' Total Cycles',
    'PAPI_NATIVE_UOPS_RETIRED:PACKED_SIMD': 'Vector operations',
    'PAPI_L2_TCA': 'L2 accesses',
    'PAPI_NATIVE_LLC_MISSES': 'L3 total cache misses',
    'PAPI_NATIVE_LLC_REFERENCES': 'L3 accesses',
    'PAPI_TLB_DM': 'TLB data misses',
    'PAPI_BR_MSP': 'Branch mispredictions',
    'PAPI_L1_TCM': 'L1 total cache misses',
    'PAPI_L2_TCM': 'L2 total cache misses',
    'PAPI_LST_INS': 'Load/store instructions',
    'PAPI_BR_CN': 'Conditional branches',
    'PAPI_TOT_INS': 'Total instructions',
    'PAPI_BR_INS': 'Branch instructions',
    'PAPI_BR_UCN': 'Unconditional branches',
    'PAPI_NATIVE_UOPS_RETIRED:SCALAR_SIMD': 'Scalar vector ops',
    'PAPI_RES_STL': 'Total resource stalls (cycles)',
    'PAPI_NATIVE_FETCH_STALL': 'Number of cycles stalled for instruction cache miss',
    'PAPI_NATIVE_RS_FULL_STALL': 'Resource stalls',
    'DERIVED_STALL_PERCENT': 'Fraction of total stalls',
    'DERIVED_L1_MISSRATE': 'L1 miss rate',
    'DERIVED_L3_MISSRATE': 'L3 miss rate',
    'DERIVED_BRANCH_MR': 'Branch misprediction rate',
    'DERIVED_IPC': 'Instructions per cycle',
    'DERIVED_CPI': 'Cycles per instruction',
    'DERIVED_VIPI': 'Vector instructions fraction',
    'DERIVED_VIPC': 'Vector instructions per cycle',
    'Other': 'Other'
    }
