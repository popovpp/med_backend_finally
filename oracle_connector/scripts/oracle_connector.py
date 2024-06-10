import oracledb
import time
from ping3 import ping

from datetime import datetime
from core.config.cache_connector import CacheConnector
from core.src.utils import ip_address_ping, address_ping_with_repeat
from core.config.settings import PING_REPEATING
from ..config.settings import (ORACLE_USERNAME, ORACLE_PASSWORD, ORACLE_CONNECTIONSTRING,
                               REPEATING_OF_ORACLE_PROC)


def init_session(connection, requested_tag):
    with connection.cursor() as cursor:
        cursor.execute("alter session set nls_date_format = 'YYYY-MM-DD HH24:MI'")


pool = oracledb.create_pool(user=ORACLE_USERNAME,
                            password=ORACLE_PASSWORD,
                            dsn=ORACLE_CONNECTIONSTRING,
                            min=1,
                            max=100,
                            increment=1,
                            session_callback=init_session,
                            stmtcachesize=100,
                            timeout=5,
                            ping_interval=10,
                            wait_timeout=10000,
                            getmode=oracledb.POOL_GETMODE_TIMEDWAIT)


cache = CacheConnector()


def test_connection():
    start = time.time()
    with pool.acquire() as connection:
        with connection.cursor() as cursor:
            p_result_cur = cursor.var(oracledb.DB_TYPE_CURSOR)
            cursor.prefetchrows = 101
            cursor.arraysize = 100
            # cursor.execute("begin solution_med.pkg_perc_acc.get_pat_info(:1,:2,:3); end;",
            #                ['124501', '', p_result_cur])
            cursor.callproc('solution_med.pkg_perc_acc.get_pat_info',
                            parameters=[124501, None, p_result_cur],
                            keyword_parameters={})
            print(p_result_cur.getvalue())
            print(p_result_cur.getvalue().fetchall())
            # sql = """select sysdate from dual"""
            # for r in cursor.execute(sql):
            #     print(r)
            # for item in p_result_cur.getvalue():
            #     print(item)
    end = time.time()
    print(f'Затрачено времени на запрос в БД {(end-start)*1000} мс')
    return 'ok'


async def call_oracle_proc(data, proc_name):
    
    print('-------oracle call-------')
    print((proc_name, data))
    print('-------------------------')

    start = time.time()
    repeat = REPEATING_OF_ORACLE_PROC

    ping_result = await address_ping_with_repeat(
        ORACLE_CONNECTIONSTRING[:15],
        PING_REPEATING,
        [500, 'ping -> False', "Отсутствует соединение с Oracle."],
        [200, 'ping -> True', "Ok"]
    )

    if ping_result[0] !=200:
        return ping_result
    else:
        print(ping_result)

    result = None
    repeat = REPEATING_OF_ORACLE_PROC
    while repeat > 0:
        try:
            with pool.acquire() as connection:
                with connection.cursor() as cursor:
                    p_result_cur = cursor.var(oracledb.DB_TYPE_CURSOR)
                    data.append(p_result_cur)
                    print(data)
                    cursor.prefetchrows = 101
                    cursor.arraysize = 100
                    while repeat > 0:
                        try:
                            cursor.callproc(proc_name,
                                            parameters=data,
                                            keyword_parameters={})
                            result = p_result_cur.getvalue().fetchall()
                            print(result)
                            repeat = 0
                        except Exception as e:
                            print(e)
                            repeat -= 1
                            result = [[500, f"{e}"]]
        except Exception as e:
            print(e)
            repeat -= 1
            print(repeat)
            if repeat == 0:
                result = [500, str(result), f"{e} - Отсутствует соединение с Oracle."]
                return result
    end = time.time()
    print(f'Затрачено времени на запрос в Oracle {(end-start)*1000} мс')

    try:
        if result:
            result = [x if (not isinstance(x, datetime)) else x.strftime('%d.%m.%Y %H:%M:%S') for x in result[0]]
        else:
            result = [200, str(result), "Пустой результат процедуры Oracle."]
    except Exception as e:
        print(e)
        result = [500, str(result), f"{e} - Сбой обработки результата процедуры Oracle."]

    return result


async def call_oracle_proc_for_list_result(data, proc_name):

    start = time.time()
    repeat = REPEATING_OF_ORACLE_PROC
    status_code = None

    ping_result = await address_ping_with_repeat(
        ORACLE_CONNECTIONSTRING[:15],
        PING_REPEATING,
        [500, 'ping -> False', "Отсутствует соединение с Oracle."],
        [200, 'ping -> True', "Ok"]
    )

    if ping_result[0] !=200:
        status_code = 500
        return status_code, ping_result
    else:
        print(ping_result)

    result_row = None
    result = []
    repeat = REPEATING_OF_ORACLE_PROC
    while repeat > 0:
        try:
            with pool.acquire() as connection:
                with connection.cursor() as cursor:
                    p_result_cur = cursor.var(oracledb.DB_TYPE_CURSOR)
                    data.append(p_result_cur)
                    print(data)
                    cursor.prefetchrows = 101
                    cursor.arraysize = 100
                    while repeat > 0:
                        try:
                            cursor.callproc(proc_name,
                                            parameters=data,
                                            keyword_parameters={})
                            result_row = p_result_cur.getvalue().fetchall()
                            print(result_row)
                            repeat = 0
                            status_code = 200
                        except Exception as e:
                            print(e)
                            repeat -= 1
        except Exception as e:
            print(e)
            repeat -= 1
            print(repeat)
            if repeat == 0:
                result.append([500, str(result_row), f"{e} - Отсутствует соединение с Oracle."])
                return result
    end = time.time()
    print(f'Затрачено времени на запрос в Oracle {(end-start)*1000} мс')

    try:
        if result_row:
            for item in result_row:
                result.append([x if (not isinstance(x, datetime)) else x.strftime('%d.%m.%Y %H:%M:%S') for x in item])
        else:
            result.append([404, str(result), "Пустой результат процедуры Oracle."])
            status_code = 404
    except Exception as e:
        print(e)
        result.append([500, str(result), f"{e} - Сбой обработки результата процедуры Oracle."])
        status_code = 500

    return status_code, result
