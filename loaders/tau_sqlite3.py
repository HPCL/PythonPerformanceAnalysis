#!/usr/bin/env python3
import sqlite3
import os.path
from graphviz import Digraph

from utils import *
from fetcher import Fetcher


class TAU_sqlite3(Fetcher):
    DEBUG = True

    @staticmethod
    def set_types():
        types = dict()
        for col in ['trial', 'parent', 'node_rank', 'context_rank', 'thread_rank', 'thread',
                    'timer', 'line_number', 'line_number_end', 'column_number',
                    'column_number_end', 'metric']:
            types[col] = 'uint32'
        for col in ['id', 'sample_count']:
            types[col] = 'uint64'
        for col in ['short_name', 'timergroup', 'source_file']:
            types[col] = 'str'
        types['metadata:value'] = 'str'
        for col in ['maximum_value', 'minimum_value', 'mean_value', 'sum_of_squeres',
                    'timer_values:value']:
            types[col] = 'float64'
        types['created'] = 'datetime64'

    # Fetcher methods
    def __init__(self, filepath='tauprofile.db'):
        super().__init__()
        if not os.path.exists(filepath):
            err(f'Database file {filepath} does not exist.')
        self.sql3file = filepath

    def load_data(self):
        self.open_database()
        self.get_trials()
        #self.get_metadata()
        self.get_threads()
        self.get_metrics()
        self.get_timers()
        self.get_timer_values()
        self.get_counters()
        self.get_counter_values()
        # if self.DEBUG: self.write_callgraph()

    def close(self):
        if self.conn.cursor():
            self.conn.cursor().close()
        if self.conn:
            self.conn.close()

    # --------- TAU-specific methods  -------------
    def open_database(self):
        try:
            self.conn = sqlite3.connect(self.sql3file)
        except Exception as e:
            err(f'Could not open database file {self.sql3file}: {str(e)}')
        return True

    def _get_data(self, query, name):
        """
        Private method for creating dataframes corresponding to DB tables
        :param query: SQLite query
        :param name: the name of the SQL table
        :return: the dataframe created from the table
        """
        c = self.conn.cursor()
        rows = c.execute(query)
        desc = c.description
        column_names = [col[0] for col in desc]
        data = c.fetchall()
        debug(f'cols: {column_names}', debug=self.DEBUG)
        debug(f'rows: {data}', debug=self.DEBUG)
        self.data[name] = pd.DataFrame.from_records(data, columns=column_names)
        debug(f'\n::::{name}::::\n{self.data[name].head()}', self.DEBUG)
        return self.data[name]

    def get_trials(self):
        return self._get_data('SELECT id, data FROM trial', 'trials')

    def get_metadata(self):
        return self._get_data('SELECT trial, name, value FROM metadata', 'metadata')

    def get_threads(self):
        return self._get_data('SELECT id, node_rank, thread_rank FROM thread', 'threads')

    def get_metrics(self):
        return self._get_data('SELECT trial, name FROM metric', 'metrics')

    def get_timers(self):
        return self._get_data('SELECT id, trial, parent, short_name FROM timer', 'timers')

    def get_timer_values(self):
        return self._get_data('SELECT timer, metric, thread, value FROM timer_value',
                              'timer_values')

    def get_counters(self):
        return self._get_data('SELECT id, trial, name FROM counter', 'counters')

    def get_counter_values(self):
        return self._get_data('SELECT counter, timer, thread, sample_count, maximum_value, '
                              'minimum_value, mean_value, sum_of_squares FROM counter_value',
                              'counter_values')

    def write_callgraph(self):
        dot = Digraph(comment='TAU Callgraph')
        dot.edges = []
        timers = self.data['timers'].to_dict()
        for timer in timers:
            if timer['trial'] == 1:
                if timer['id'] == 1 or timer['parent'] != None:
                    dot.node(str(timer['id']), timer['short_name'])
                if timer['parent'] != None:
                    dot.edge(str(timer['id']), str(timer['parent']))
        debug(dot.source)
        dot.render('callgraph.gv', view=True)


class TAU:
    METRIC_NAMES = {'PAPI_TOT_CYC': 'Total Cycles',
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


if __name__ == '__main__':
    #tau = TAU_sqlite3('tauprofile.db')
    tau = TAU_sqlite3('p2z_omp.sqlite3')
    tau.load_data()
    # tau.write_callgraph()
