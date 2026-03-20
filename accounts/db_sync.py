"""
Shared utilities for syncing member address and phone data to the legacy SQL Server database.

Used by both accounts.views (AddressViewSet, PhoneNumberViewSet) and
convention.views (staff check-in endpoints that update member data on behalf of staff).
"""
import os
import logging

import pymssql

logger = logging.getLogger(__name__)

SQL_PROD_HOST = os.getenv('SQL_PROD_HOST')
SQL_USER = os.getenv('SQL_USER')
SQL_PASSWORD = os.getenv('SQL_PASSWORD')

# Django address type → SQL Server address type
_DJANGO_TO_SQL_TYPE = {
    'Work': 'Business',
    'Home': 'Home',
    'School': 'School',
}

# Django phone type → SQL Server column name in the Address table
_PHONE_TYPE_TO_COLUMN = {
    'Mobile': 'add_CellPhone',
    'Home': 'add_phone',
    'Work': 'add_business_phone',
}
# Whitelist used to prevent SQL injection when interpolating column names
_ALLOWED_PHONE_COLUMNS = frozenset(_PHONE_TYPE_TO_COLUMN.values())


def sync_address_to_sql(action, member_id, address_data, old_address_data=None):
    """
    Sync an address create/update/delete to the legacy SQL Server database.

    Args:
        action: 'create', 'update', or 'delete'
        member_id: int — the legacy member_id (Member.member_id)
        address_data: dict with keys add_line1, add_line2, add_city, add_state, add_zip, add_type
        old_address_data: dict (required for 'update') — the address fields before the change
    """
    sql_type = _DJANGO_TO_SQL_TYPE.get(address_data.get('add_type', ''), address_data.get('add_type', ''))

    try:
        conn = pymssql.connect(
            server=SQL_PROD_HOST,
            tds_version=r'7.0',
            user=SQL_USER,
            password=SQL_PASSWORD,
            database='Member',
        )
        cursor = conn.cursor()

        if action == 'create':
            cursor.execute(
                'INSERT INTO Address (add_memid, add_line1, add_line2, add_city, add_state, add_zip, add_type) '
                'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                (
                    member_id,
                    address_data.get('add_line1', ''),
                    address_data.get('add_line2', ''),
                    address_data.get('add_city', ''),
                    address_data.get('add_state', ''),
                    address_data.get('add_zip', ''),
                    sql_type,
                ),
            )

        elif action == 'update':
            old_sql_type = _DJANGO_TO_SQL_TYPE.get(
                old_address_data.get('add_type', ''), old_address_data.get('add_type', '')
            ) if old_address_data else sql_type
            cursor.execute(
                'UPDATE Address '
                'SET add_line1=%s, add_line2=%s, add_city=%s, add_state=%s, add_zip=%s, add_type=%s '
                'WHERE add_memid=%s AND add_type=%s',
                (
                    address_data.get('add_line1', ''),
                    address_data.get('add_line2', ''),
                    address_data.get('add_city', ''),
                    address_data.get('add_state', ''),
                    address_data.get('add_zip', ''),
                    sql_type,
                    member_id,
                    old_sql_type,
                ),
            )
            # If no matching row exists in the legacy DB, fall back to INSERT
            if cursor.rowcount == 0:
                cursor.execute(
                    'INSERT INTO Address (add_memid, add_line1, add_line2, add_city, add_state, add_zip, add_type) '
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (
                        member_id,
                        address_data.get('add_line1', ''),
                        address_data.get('add_line2', ''),
                        address_data.get('add_city', ''),
                        address_data.get('add_state', ''),
                        address_data.get('add_zip', ''),
                        sql_type,
                    ),
                )

        elif action == 'delete':
            cursor.execute(
                'DELETE FROM Address WHERE add_memid=%s AND add_line1=%s AND add_type=%s',
                (member_id, address_data.get('add_line1', ''), sql_type),
            )

        conn.commit()
        cursor.close()
        conn.close()
        logger.debug('SQL Server: %s address (type: %s) for member %s', action, sql_type, member_id)

    except Exception as e:
        logger.error('Error syncing address to SQL Server: %s', e, exc_info=True)
        # Do not raise — Django operation succeeds even if legacy sync fails


def sync_phone_to_sql(action, member_id, phone_type, phone_number=None):
    """
    Sync a phone number create/update/delete to the legacy SQL Server database.
    Phone numbers are stored in the Address table where add_type='Home'.

    Args:
        action: 'create', 'update', or 'delete'
        member_id: int — the legacy member_id (Member.member_id)
        phone_type: 'Mobile', 'Home', or 'Work'
        phone_number: str of digits (or None/empty for delete)
    """
    column_name = _PHONE_TYPE_TO_COLUMN.get(phone_type)
    if not column_name or column_name not in _ALLOWED_PHONE_COLUMNS:
        logger.warning("Unknown phone type '%s', skipping SQL Server sync", phone_type)
        return

    # Format as XXX-XXX-XXXX for 10-digit numbers; pass through otherwise
    if phone_number:
        digits = ''.join(c for c in phone_number if c.isdigit())
        formatted = f'{digits[:3]}-{digits[3:6]}-{digits[6:10]}' if len(digits) == 10 else digits
    else:
        formatted = ''

    try:
        conn = pymssql.connect(
            server=SQL_PROD_HOST,
            tds_version=r'7.0',
            user=SQL_USER,
            password=SQL_PASSWORD,
            database='Member',
        )
        cursor = conn.cursor()

        # Phone numbers live in the Home address row
        cursor.execute(
            "SELECT COUNT(*) FROM Address WHERE add_memid=%s AND add_type='Home'",
            (member_id,),
        )
        home_exists = cursor.fetchone()[0] > 0

        if not home_exists:
            if action in ('create', 'update') and formatted:
                cursor.execute(
                    f"INSERT INTO Address (add_memid, add_type, {column_name}) VALUES (%s, 'Home', %s)",
                    (member_id, formatted),
                )
        else:
            if action == 'delete':
                cursor.execute(
                    f"UPDATE Address SET {column_name}='' WHERE add_memid=%s AND add_type='Home'",
                    (member_id,),
                )
            else:
                cursor.execute(
                    f"UPDATE Address SET {column_name}=%s WHERE add_memid=%s AND add_type='Home'",
                    (formatted, member_id),
                )

        conn.commit()
        cursor.close()
        conn.close()
        logger.debug('SQL Server: %s %s phone for member %s', action, phone_type, member_id)

    except Exception as e:
        logger.error('Error syncing phone to SQL Server: %s', e, exc_info=True)
        # Do not raise — Django operation succeeds even if legacy sync fails
