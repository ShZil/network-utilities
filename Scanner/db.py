from import_handler import ImportDefence
with ImportDefence():
    import sqlite3

SELECT_SPECIFIC_SCAN = "SELECT * FROM information WHERE name=?"

def get_information_about_scan(name: str):
    connection = sqlite3.connect('scans.db')
    cursor = connection.cursor()
    try:
        cursor.execute(SELECT_SPECIFIC_SCAN, (name, ))
    except sqlite3.OperationalError:
        raise FileNotFoundError("SQL table 'information' was not found.")
    result = cursor.fetchone()
    connection.close()
    return result


if __name__ == '__main__':
    print(get_information_about_scan('ICMP Sweep'))
