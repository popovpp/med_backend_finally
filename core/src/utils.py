import hashlib

from datetime import datetime, date
from ping3 import ping
from typing import List
from sqlalchemy.future import select as async_select
from sqlalchemy import (inspect, INTEGER, DATE, TIMESTAMP, DOUBLE_PRECISION, TIME, BIGINT,
                        Date, DATETIME)

from core.config.db import engine, metadata, Base
from core.config.cache_connector import CacheConnector

from core.sa_tables.accounts import UserTable
from core.config.settings import ORACLE_IP


cache = CacheConnector()
hasher= hashlib.sha256


async def get_model_class(tablename):
    for c in Base.__subclasses__():
        try:
            if c.__tablename__ == tablename:
                return c
        except Exception as e:
            pass


async def input_obj_constructor(model, new_instance, input_structure):

    # Определяем типы колонок и внешние ключи
    model_col_type_dict = {}
    async with engine.connect() as conn:
        columns_model_table = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_columns(model.__tablename__)
        )
        for c in columns_model_table :
            model_col_type_dict[c['name']] = c['type']

    # Перекладываем значения в new_instance
    for attr in UserTable.__dict__.keys():
            try:
                value = input_structure[attr]
                if isinstance(model_col_type_dict[attr], INTEGER):
                    if isinstance(value, str):
                        value = int(value)
                elif isinstance(model_col_type_dict[attr], BIGINT):
                    if isinstance(value, str):
                        value = int(value)
                elif isinstance(model_col_type_dict[attr], DATE):
                    if isinstance(value, str):
                        value = datetime.strptime(value, '%Y-%m-%d')
                elif isinstance(model_col_type_dict[attr], TIMESTAMP):
                    if isinstance(value, str):
                        value = datetime.strptime(value, '%Y-%m-%d')
                elif isinstance(model_col_type_dict[attr], TIME):
                    if isinstance(value, str):
                        value = datetime.strptime(value, '%H:%M').time()
                elif isinstance(model_col_type_dict[attr], DOUBLE_PRECISION):
                    if isinstance(value, str):
                        value = float(value)
                setattr(new_instance, attr, value)
            except Exception as e:
                pass

    return new_instance


async def input_obj_constructor_with_fk(model, new_instance, input_structure, date_time_format='%Y-%m-%d', updating=False):

    # Определяем типы колонок и внешние ключи
    model_col_type_dict = {}
    users_col_id_dict = {}
    async with engine.connect() as conn:
        try:
            columns_model_table = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_columns(model.__tablename__)
            )
            for c in columns_model_table :
                model_col_type_dict[c['name']] = c['type']

            for c in metadata.tables[model.__tablename__].columns:
                for fk in c.foreign_keys:
                    users_col_id_dict[str(c.name)] = await get_model_class(fk.column.table.name)
        except Exception as e:
            pass

        # Перекладываем значения в new_instance
        for attr in model.__dict__.keys():
            try:
                value = input_structure[attr]
                if isinstance(model_col_type_dict[attr], INTEGER):
                    if isinstance(value, str):
                        value = int(value)
                elif isinstance(model_col_type_dict[attr], BIGINT):
                    if isinstance(value, str):
                        value = int(value)
                elif isinstance(model_col_type_dict[attr], DATE):
                    if isinstance(value, str):
                        value = datetime.strptime(value, date_time_format)
                elif isinstance(model_col_type_dict[attr], Date):
                    if isinstance(value, str):
                        value = datetime.strptime(value, date_time_format)
                        print(attr, value)
                # elif isinstance(model_col_type_dict[attr], TIMESTAMP):
                #     value = datetime.strptime(value, date_time_format)
                elif isinstance(model_col_type_dict[attr], TIME):
                    if isinstance(value, str):
                        value = datetime.strptime(value, '%H:%M').time()
                elif isinstance(model_col_type_dict[attr], DATETIME):
                    if isinstance(value, str):
                        value = datetime.strptime(value, date_time_format)
                elif isinstance(model_col_type_dict[attr], DOUBLE_PRECISION):
                    if isinstance(value, str):
                        value = float(value)
                try:
                    obj = (await conn.execute(async_select(users_col_id_dict[attr]).filter(
                        getattr(users_col_id_dict[attr], 'client_id', None) == value
                    ))).unique().scalars().one_or_none()
                    if obj:
                        value = obj.id
                    else:
                        value = None
                except Exception as e:
                    pass
                if updating:
                    if value is not None:
                        setattr(new_instance, attr, value)
                else:
                    setattr(new_instance, attr, value)
            except Exception as e:
                print(e)

    return new_instance


async def input_obj_constructor_with_fk_id(model, new_instance, input_structure, date_time_format='%Y-%m-%d', updating=False):

    # Определяем типы колонок и внешние ключи
    model_col_type_dict = {}
    users_col_id_dict = {}
    async with engine.connect() as conn:
        try:
            columns_model_table = await conn.run_sync(
                lambda sync_conn: inspect(sync_conn).get_columns(model.__tablename__)
            )
            for c in columns_model_table :
                model_col_type_dict[c['name']] = c['type']

            for c in metadata.tables[model.__tablename__].columns:
                for fk in c.foreign_keys:
                    users_col_id_dict[str(c.name)] = await get_model_class(fk.column.table.name)
        except Exception as e:
            pass

        # Перекладываем значения в new_instance
        for attr in model.__dict__.keys():
            try:
                value = input_structure[attr]
                if isinstance(model_col_type_dict[attr], INTEGER):
                    if isinstance(value, str):
                        value = int(value)
                elif isinstance(model_col_type_dict[attr], BIGINT):
                    if isinstance(value, str):
                        value = int(value)
                elif isinstance(model_col_type_dict[attr], DATE):
                    if isinstance(value, str):
                        value = datetime.strptime(value, date_time_format)
                elif isinstance(model_col_type_dict[attr], Date):
                    if isinstance(value, str):
                        value = datetime.strptime(value, date_time_format)
                        print(attr, value)
                # elif isinstance(model_col_type_dict[attr], TIMESTAMP):
                #     value = datetime.strptime(value, date_time_format)
                elif isinstance(model_col_type_dict[attr], TIME):
                    if isinstance(value, str):
                        value = datetime.strptime(value, '%H:%M').time()
                elif isinstance(model_col_type_dict[attr], DATETIME):
                    if isinstance(value, str):
                        value = datetime.strptime(value, date_time_format)
                elif isinstance(model_col_type_dict[attr], DOUBLE_PRECISION):
                    if isinstance(value, str):
                        value = float(value)
                try:
                    obj = (await conn.execute(async_select(users_col_id_dict[attr]).filter(
                        getattr(users_col_id_dict[attr], 'id', None) == value
                    ))).unique().scalars().one_or_none()
                    if obj:
                        value = obj.id
                    else:
                        value = None
                except Exception as e:
                    pass
                if updating:
                    if value is not None:
                        setattr(new_instance, attr, value)
                else:
                    setattr(new_instance, attr, value)
            except Exception as e:
                print(e)

    return new_instance


async def table_to_schema_constructor(table_instance, schema_instance, updating=False):

    for key in schema_instance.__dict__.keys():
        try:
            value = table_instance.__dict__[key]
            if isinstance(value, date) or isinstance(value,datetime):
                value = value.strftime('%Y-%m-%d')
            if key == 'notification_time':
                value = value.strftime("%H:%M")
            if key == 'gender':
                value = int(value)
            if updating:
                if value is not None:
                    schema_instance.__dict__[key] = value
            else:
                schema_instance.__dict__[key] = value
        except Exception as e:
            pass

    return schema_instance


def get_search_words(search: str):

    # reductions_list = ['посёлок', 'поселок', 'пос', 'дом', 'ул', 'улица', 'р-н', 'район']

    result = []
    added_result = []
    search_words_list = search.strip().split()
    for word in search_words_list:
        for char in(',', '.'):
            word = word.lower().replace(char, '')
        result.append(word)
    # for word in result:
    #     if word in reductions_list:
    #         added_result.append(word[:1])
    #     else:
    #         added_result.append(word)

    return result


async def ip_address_ping(ip_address):
    response = ping(ORACLE_IP)
    if response:
        return True
    else:
        False


async def address_ping_with_repeat(
    ip_address: str,
    repeat: int,
    error_result: List[str],
    success_result: List[str]
):
    while repeat>0:
        response = await ip_address_ping(ip_address)
        if response:
            return success_result
        else:
            repeat -= 1
    return error_result
