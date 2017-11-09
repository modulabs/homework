import time
import sqlite3 as lite
import sys
import matplotlib.pyplot as plt


log_level_error = 1
log_level_warning = 2
log_level_info = 3
log_level_debug = 4
log_level_trace = 5

log_level = 5

def debug(level, logstr):
    if(log_level >= level):
        print("[" + getCurrentTime() + "] "+str(logstr))

def getCurrentTime():
    now = time.localtime()
    s = "%04d-%02d-%02d %02d:%02d:%02d" % (
    now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    return s

# Extracts the number of input and output units from an OpenAI Gym environment.
def env_dims(env):
    return (env.observation_space.shape[0], env.action_space.shape[0])


##### sqlite DB utils ###############################
# sudo apt-get install sqlite3 libsqlite3-dev
# http://zetcode.com/db/sqlitepythontutorial/

def testSqlite():
    con = lite.connect('test.db')

    with con:
        cur = con.cursor()
        cur.execute('SELECT SQLITE_VERSION()')
        data = cur.fetchone()
        print ("SQLite version: %s" % data)




def make_logtable_ifnot_exist():
    con = lite.connect('test.db')

    with con:
        cur = con.cursor()

        query = "CREATE TABLE IF NOT EXISTS "
        query += "TB_LOG"
        query += "("
        query += "  ValueType TEXT, "
        query += "  Game TEXT, "
        query += "  Algorithm TEXT, "
        query += "  Model TEXT, "
        query += "  Iter INTEGER, "
        query += "  Value REAL "
        query += ")"

        try:
            cur.execute(query)
            con.commit()
            print("CREATE TABLE: TB_LOG OK..")
        except lite.Error as er:
            print("CREATE TABLE : ERROR CODE..(%s)" % er.message)

        '''ret = cur.execute(query)

        if(lite.SQLITE_OK==ret):
            print("CREATE TABLE: TB_LOG OK..")
        else :
            msg = cur.fetchone()
            if msg is None:
                print("CREATE TABLE: ALREADY EXISTS..")
            else :
                print("CREATE TABLE: ERROR CODE..(%s)" % msg)

        con.commit()'''


def drop_logtable():
    con = lite.connect('test.db')

    with con:
        cur = con.cursor()

        query = "DROP TABLE IF EXISTS "
        query += "TB_LOG"

        try:
            cur.execute(query)
            con.commit()
            print("DROP TABLE: TB_LOG OK..")
        except lite.Error as er:
            print("DROP TABLE : ERROR CODE..(%s)" % er.message)


        '''ret = cur.execute(query)

        if(lite.SQLITE_OK==ret):
            print("DROP TABLE: TB_LOG OK..")
        else :
            msg = cur.fetchone()
            if msg is None:
                print("DROP TABLE: ALREADY Deleted..")
            else :
                print("DROP TABLE: ERROR CODE..(%s)" % msg)

        con.commit()'''



def insert_log_data(datas):
    con = lite.connect('test.db')

    with con:
        cur = con.cursor()

        query = "INSERT INTO "
        query += "TB_LOG" + " "
        query += "VALUES(?, ?, ?, ?, ?, ?)"
        '''query += "  ValueType = ?, "
        query += "  Game = ?, "
        query += "  Algorithm = ?, "
        query += "  Model = ?, "
        query += "  Iter = ?, "
        query += "  Value = ? "
        query += ")"'''

        try:
            cur.executemany(query, datas)
            con.commit()
            print("INSERT INTO : TB_LOG OK..")
        except lite.Error as er:
            print("INSERT INTO : ERROR CODE..(%s)" % er.message)

        '''if (lite.SQLITE_OK == ret):
            print("INSERT INTO : TB_LOG OK..")
        else:
            msg = cur.fetchone()
            print("INSERT INTO : ERROR CODE..(%s)" % msg)'''




# conditions is a hashtable whose keys are [columnnames] and values are data is list
# eg.) conditions = { 'ValueType':['t_return', 'loss'], 'Model':['DenseModel'] }
def select_log_data(conditions):
    con = lite.connect('test.db')

    with con:
        cur = con.cursor()
        #condition_cnt = 0
        condition_one_list = []

        query = "SELECT * FROM "
        query += "TB_LOG" + " "
        if conditions is not None:
            #query += get_where_statement(conditions)
            wherestatement, condition_one_list = get_where_statement(conditions)
            query += wherestatement
            '''query += "WHERE "

            assert len(conditions['ValueType']) >= 1

            for key in conditions.keys():
                condition_list = conditions[key]
                if condition_list is not None and len(condition_list) > 0:
                    if condition_cnt > 0:
                        query += "AND "
                    query += key + " "
                    query += "IN ({})".format(','.join('?' * len(condition_list))) + " "
                    condition_cnt += 1
                    condition_one_list.extend(condition_list)'''
        query += "ORDER BY ValueType, Game, Algorithm, Model, Iter"
        print(query)
        print(condition_one_list)
        return cur.execute(query, condition_one_list).fetchall()

        #else:
        #    assert False


def delete_previous_log(conditions):
    con = lite.connect('test.db')

    with con:
        cur = con.cursor()

        query = "DELETE FROM "
        query += "TB_LOG" + " "
        if conditions is not None:
            # query += get_where_statement(conditions)
            wherestatement, condition_one_list = get_where_statement(conditions)
            query += wherestatement

        try:
            cur.execute(query, condition_one_list)
            con.commit()
            print("DELETE FROM TABLE: TB_LOG OK..")
        except lite.Error as er:
            print("DELETE FROM TABLE : ERROR CODE..(%s)" % er.message)


def get_where_statement(conditions):
    condition_cnt = 0
    condition_one_list = []
    querystr = "WHERE "

    assert len(conditions['ValueType']) >= 1

    for key in conditions.keys():
        condition_list = conditions[key]
        if condition_list is not None and len(condition_list) > 0:
            if condition_cnt > 0:
                querystr += "AND "
            querystr += key + " "
            querystr += "IN ({})".format(','.join('?' * len(condition_list))) + " "
            condition_cnt += 1
            condition_one_list.extend(condition_list)

    return querystr, condition_one_list




######################################################
##### matplotlib utils ###############################

def get_plot_data(datas):
    print('--------------')
    print(datas)
    data_x_hash = {}
    data_y_hash = {}
    for idx in range(len(datas)):
        dataset = datas[idx]
        #key = tuple(list(dataset)[1:4])
        key = tuple(list(dataset)[0:4])
        data_x = list(dataset)[4]
        data_y = list(dataset)[5]
        if key not in data_x_hash.keys():
            data_x_hash[key] = []
            data_y_hash[key] = []
        data_x_hash[key].append(data_x)
        data_y_hash[key].append(data_y)

    return data_x_hash, data_y_hash



def draw_plot(datas, x_units=1 ):
    plot_data_x, plot_data_y = get_plot_data(datas)
    plt.figure(figsize=(15, 10))

    x_label = 'Iters'
    if(x_units>1):
        x_label += '('+str(x_units)+'s)'
    y_label = datas[0][0]
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    for keys in plot_data_x.keys():
        print("plot_data_x.keys(): "+str(keys))
        data_x = plot_data_x[keys]
        data_y = plot_data_y[keys]
        plot_label = str(keys)
        print(plot_label)
        plt.plot(data_x, data_y, label=plot_label)
    plt.grid()
    plt.legend()
    plt.show()
