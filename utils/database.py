import mysql.connector
from utils import is_dev, get_env

def get_db_connection():
    """
    Retrieves the database connection.
    """
    if is_dev():
        conn = mysql.connector.connect(
            host = get_env('DEV_DB_HOST'),
            database = get_env('DEV_DB_NAME'),
            user = get_env('DEV_DB_USER'),
            password = get_env('DEV_DB_PASS')
        )
    else:
        conn = mysql.connector.connect(
            host = get_env('DB_HOST'),
            database = get_env('DB_NAME'),
            user = get_env('DB_USER'),
            password = get_env('DB_PASS')
        )
    
    return conn

def get_saved_totals():
    """
    Retrieves the saved totals from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, amp, usd FROM totals ORDER BY id DESC LIMIT 2")
    totals_result = cursor.fetchall()
    return totals_result

def get_saved_tvl(new_batch_id, old_batch_id):
    """
    Retrieves the saved TVL from the database.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, contract, amp_total, usd, batch_id 
        FROM tvl
        WHERE batch_id = %s 
        OR batch_id = %s 
        ORDER BY batch_id ASC
        """, (old_batch_id, new_batch_id))
    tvl_result = cursor.fetchall()
    return tvl_result


def save_totals(amp_total, usd_total):
    """
    Saves the total AMP and USD values to the database.
    
    @params amp_total: The total AMP amount across all pools
    @params usd_total: The total USD value across all pools
    @returns: The ID of the inserted record
    @raises mysql.connector.Error: If database connection or query fails
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO totals (amp, usd) VALUES (%s, %s)", (amp_total, usd_total))
        conn.commit()
        
        return cursor.lastrowid
        
    except mysql.connector.Error as e:
        ##
        ## Log the error and re-raise with more context
        raise mysql.connector.Error(f"Database error while saving totals: {e}")
        
    finally:
        ##
        ## Ensure proper cleanup of database resources
        if cursor:
            cursor.close()
        if conn:
            conn.close()



def save_tvl(data, batch_id):
    """
    Saves the TVL data to the database.
    
    @params data: List of pool data where each item contains [name, contract, amp_total, usd_value]
    @params batch_id: The batch ID to associate with each TVL record
    @returns: The last row ID inserted
    """
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        ##
        ## Add batch_id to each data row
        data_with_batch_id = []
        for row in data:
            ##
            ## row format: [name, contract, amp_total, usd_value]
            ## need to append batch_id: [name, contract, amp_total, usd_value, batch_id]
            row_with_batch = row + [batch_id]
            data_with_batch_id.append(row_with_batch)
        
        cursor.executemany("INSERT INTO tvl (name, contract, amp_total, usd, batch_id) VALUES (%s, %s, %s, %s, %s)", data_with_batch_id)
        conn.commit()
        return cursor.lastrowid
        
    except mysql.connector.Error as e:
        ##
        ## Log the error and re-raise with more context
        raise mysql.connector.Error(f"Database error while saving TVL data: {e}")
        
    finally:
        ##
        ## Ensure proper cleanup of database resources
        if cursor:
            cursor.close()
        if conn:
            conn.close()