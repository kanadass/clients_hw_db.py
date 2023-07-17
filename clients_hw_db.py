import psycopg2


# Функция, создающая структуру БД (таблицы)
def create_db(conn):
    with conn.cursor() as cur:
        cur.execute('''CREATE TABLE IF NOT EXISTS clients
                       (id SERIAL PRIMARY KEY,
                        first_name TEXT,
                        last_name TEXT,
                        email TEXT)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS phones
                       (client_id INTEGER REFERENCES clients(id),
                        phone TEXT)''')
        conn.commit()
        print('Таблицы созданы!')


# Функция, позволяющая добавить нового клиента.
def add_client(conn, first_name, last_name, email):
    with conn.cursor() as cur:
        cur.execute('''INSERT INTO clients (first_name, last_name, email)
                       VALUES (%s, %s, %s) RETURNING id, first_name, 
                       last_name, email''', (first_name, last_name, email))
        print(f'Клиент добавлен: {cur.fetchone()}')


# Функция, позволяющая добавить телефон для существующего клиента.
def add_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''INSERT INTO phones (client_id, phone) VALUES (%s, 
        %s) RETURNING client_id, phone''', (client_id, phone))
        print(f'Телефон добавлен: {cur.fetchone()}')

# Функция, позволяющая изменить данные о клиенте.
def change_client(conn, client_id, first_name=None, last_name=None, email=None):
    with conn.cursor() as cur:
        updates = []

        if first_name:
            cur.execute('''UPDATE clients SET first_name = %s WHERE id = %s''', (first_name, client_id))
            updates.append(first_name)

        if last_name:
            cur.execute('''UPDATE clients SET last_name=%s WHERE id=%s''', (last_name, client_id))
            updates.append(last_name)

        if email:
            cur.execute('''UPDATE clients SET email=%s WHERE id=%s''', (email, client_id))
            updates.append(email)

        conn.commit()
        print(f'Данные клиента: {client_id} изменены: {updates}')

# Функция, позволяющая удалить телефон для существующего клиента.
def delete_phone(conn, client_id, phone):
    with conn.cursor() as cur:
        cur.execute('''DELETE FROM phones WHERE client_id = %s AND phone = %s''', (client_id, phone))
        conn.commit()
        print(f'Телефон: {phone} клиента: {client_id} удален')

def delete_all_phone(conn, client_id):
    with conn.cursor() as cur:
        cur.execute('''DELETE FROM phones WHERE client_id = %s''', (client_id,))
        conn.commit()

# Функция, позволяющая удалить существующего клиента.
def delete_client(conn, client_id):
    delete_all_phone(conn, client_id)
    with conn.cursor() as cur:
        cur.execute('''DELETE FROM clients WHERE id = %s''', (client_id,))
        conn.commit()
        print(f'Клиент: {client_id} удален.')

# Функция, позволяющая найти клиента по его данным: имени, фамилии, email или телефону.
def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    with conn.cursor() as cur:
        query = "SELECT clients.*, phones.phone FROM clients LEFT JOIN phones ON clients.id = phones.client_id WHERE"
        conditions = []
        params = []

        if first_name:
            conditions.append('clients.first_name = %s')
            params.append(first_name)

        if last_name:
            conditions.append('clients.last_name = %s')
            params.append(last_name)

        if email:
            conditions.append('clients.email = %s')
            params.append(email)

        if phone:
            conditions.append('phones.phone = %s')
            params.append(phone)

        if conditions:
            query += " " + " AND ".join(conditions)

        cur.execute(query, tuple(params))
        result = cur.fetchall()

        if result:
            print(result)
        else:
            print('Клиент не найден.')



# Подключение к базе данных и проверка функций
with psycopg2.connect(database="clients_db", user="postgres", password="postgres") as conn:

    # with conn.cursor() as cur:
    #     cur.execute('''
    #     DROP TABLE phones;
    #     DROP TABLE clients;
    #     ''')

    create_db(conn)

    add_client(conn, 'Bob', 'Smith', 'bs@mail.com')
    add_client(conn, 'Sam', 'Kim', 'sk@mail.com')
    add_client(conn, 'John', 'Doe', 'jd@mail.com')
    add_client(conn, 'Yan', 'Soer', 'ys@mail.com')

    add_phone(conn, 1, '+79000000001')
    add_phone(conn, 2, '+79000000002')
    add_phone(conn, 2, '+79000000003')
    add_phone(conn, 3, '+79000000004')
    add_phone(conn, 4, '+79000000005')

    change_client(conn, 1, first_name='Jonny', last_name='Jonathan', email='jj@mail.com')
    change_client(conn, 2, first_name='Samuel')
    change_client(conn, 3, email='jj@mail.com')

    delete_phone(conn, 1, '+79000000001')

    delete_client(conn, 2)

    find_client(conn, first_name="John", email='jj@mail.com')
    find_client(conn, phone='+79000000005')
    find_client(conn, phone='+79000000006')

conn.close()

