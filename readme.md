## Local Configuration

---

### Database

Database is created on *PostgreSQL* in *version 16*, but it should work with 
other versions as well.

[Download PostgreSQL](https://www.postgresql.org/download/)

1. Create *.env* file in the root directory of the project (where manage.py is located) and add the following content:
    ```
    DB_NAME=bank_db
    DB_USER=admin_bank
    DB_PASSWORD=root1234
    DB_HOST=localhost
    DB_PORT=5432
    ```
    Save the file.

2. Edit pg_hba.conf file:

    In order to work most efficiently, you may need to edit the file *pg_hba.conf* in the PostgreSQL root directory.

    - Windows: `C:\Program Files\PostgreSQL\16\data\pg_hba.conf`
    - Linux: `/etc/postgresql/16/main/pg_hba.conf`
    - MacOS: `/Library/PostgreSQL/16/data/pg_hba.conf`
   
    At the end of the file, modify the column **METHOD** by adding `trust` instead of `scram-sha-256` or `md5` as follows:

    ```
    # TYPE  DATABASE        USER            ADDRESS                 METHOD
    # "local" is for Unix domain socket connections only
    local   all             all                                     trust
    # IPv4 local connections:
    host    all             all             127.0.0.1/32            trust
    # IPv6 local connections:
    host    all             all             ::1/128                 trust
    # Allow replication connections from localhost, by a user with the
    # replication privilege.
    local   replication     all                                     trust
    host    replication     all             127.0.0.1/32            trust
    host    replication     all             ::1/128                 trust
    ```

3. Restart PostgreSQL service:

    - Windows: win + R and write `services.msc`. Then find PostgreSQL service and restart it.
    - Linux: `sudo service postgresql restart`
    - MacOS: `sudo service postgresql restart`

4. Create role and database:

    1. Open *psql* terminal.
        ```
        psql -U postgres
        ```
    2. Create role with password using following command:
        ```sql
        CREATE ROLE admin_bank WITH LOGIN ENCRYPTED PASSWORD 'root1234';
        ```
    3. Create database using following command:
        ```sql
        CREATE DATABASE bank_db WITH OWNER admin_bank;
        ```
    4. Grant all privileges to the role:
        ```sql
        GRANT ALL PRIVILEGES ON DATABASE bank_db TO admin_bank;
        ```
    5. Exit the terminal:
        ```sql
        \q
       ```
   
[OPTIONAL 1] If you have a backup of the database, you can restore it using the following command:
 ```
 psql -U admin_bank -d bank_db -h localhost -p 5432 -f path_to_backup_file.sql
 ```

[OPTIONAL 2] You can use the following command to check if the database was created successfully:
 ```
 psql -U admin_bank -d bank_db -h localhost -p 5432
 ```
You'll see a message like this:
```
psql (16.2)
Type "help" for help.
mainbank=>
```
To exit the terminal, type `\q` and press Enter.

---
