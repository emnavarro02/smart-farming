import sqlite3
# from pathlib import Path

class Database:
    """Database class encapsulates methods for managing grootfarm coordinator database.

        Usage example:
            from db import Database
            config = Database('config.db')
            config.connect()
    """

    def __init__(self, db_name='config.db'):
        self.db_name = db_name

    def connect(self):
        """Searches for a database with the specified name. 
            If the databse doesn't exist, creates and initializes the database file.
            If the database name is not set, the default name is 'config.db'

            Parameters:
                db_name (String): the sqlite database file name. 
            
            Returns:
                (sqlite.db):Database connection

        """
        try:
            self.db = sqlite3.connect(self.db_name)
            if not self.is_db_initialized():
                print("[DEBUG] Trying to initalize database.")
                self.init()
                print("[DEBUG] Connected to database {database}.".format(database=self.db_name))
        except Exception as error:
            print(error)

    def init(self):
        """Initializes the database by creating the required tables and structures.
        """
        try:            
            print("[DEBUG] Database init.")       
            self.db.execute("""Create table Config(
                    ID     TEXT PRIMARY KEY NOT NULL,
                    Name   TEXT NOT NULL,
                    Mode   INT  NOT NULL,
                    Target TEXT NOT NULL);""")
            print("[DEBUG] Database intialized successfully.")
        except Exception as e:
            print(e)
            
    def is_db_initialized(self):
        """
            Check whether the database is initalized or not.

            Returns:
                (boolean):True if initialized, False if not initialized 
        """
        try:
            print("[DEBUG] Check if database is initialized.")
            r = self.db.cursor().execute("SELECT name FROM sqlite_master WHERE type='table';").fetchone()
            if r:
                print("[DEBUG] Database is initialized.")
                return True
            print("[DEBUG] Database is not initialized.")
            return False
        except Exception as error:
            print(error)

    def is_coord_registered(self):
        """
            Check if the coordinator is already registered.

            Returns:
                (boolean) 
        """
        try:
            print("[DEBUG] Check if coordinator is already initialized.")
            r = self.db.cursor().execute("SELECT id FROM Config;").fetchone()
            if r:
                print("[DEBUG] A coordinator is already registered.")
                return True
            print("[DEBUG] A coordinator is not registered yet.")
            return False
        except Exception as error:
            print(error)

    def reset(self):
        """
            Drops the Config table and clean any configurations stored in the database.
            Warning. This action can't be undone.
            
            Returns:
                (boolean)
        """
        try: 
            self.db.execute("DROP TABLE Config;")
            print("[DEBUG] Database has been reseted. To continue, ensure you have initialized database again.")
            return True
        except Exception as e:
            print(e)
            return False

    def register(self, id, name, mode, target):
        """
            Registers the information in the database. If the information is already registered, throws an error.

            Parameters:
                id (String): The id of the coordinator.
                name String): The name of the coordinator.
                mode (Int): The operation mode, whether master (0) or slave (1).
                target (String): The DNS name or IP address of the target device.

            Returns:
                (boolean):True if a new coordinator node is registered
        """
        try:
            if mode in (0,1):
                if not self.is_coord_registered():
                    with self.db:
                        self.db.execute("INSERT INTO Config (ID, Name, Mode, Target) VALUES (?, ?, ?, ?)", (id, name, mode, target))
                        print("[DEBUG] New coordinator registered.")
                        return True
                else:
                    print("[DEBUG] New coordinator not registered.")
                    return False
            else:
                raise sqlite3.OperationalError
        except sqlite3.OperationalError:
                        print("[ERROR] Invalid mode type. Use 0 or 1.")
        except Exception as error:
            print(error)
            return False

    def get_id(self):
        """
            Returns the coordinator id.
            
            Returns:
                (String):The coordinator id.
        """
        return self.db.execute("SELECT id FROM Config;").fetchone()[0]
    
    def get_name(self):
        """
            Return the coordinator name.
            
            Returns:
                (String)
        """
        return self.db.execute("SELECT name FROM Config;").fetchone()[0]

    def get_mode(self):
        """
            Return the coordinator mode.
            
            Returns:
                (Int)
        """
        return self.db.execute("SELECT mode FROM Config;").fetchone()[0]

    def get_target(self):
        """
            Return the coordinator target.
            
            Returns:
                (String)
        """
        return self.db.execute("SELECT target FROM Config;").fetchone()[0]

    def update_target(self, target):
        """
            Update the coordinator target.
            
            Returns:
                (String)
        """
        try:
            id = self.get_id()
            with self.db:
                self.db.execute("UPDATE Config Set target = ? where id = ?;", (target, id)).rowcount
                print("[DEBUG] New target: {target}.".format(target=target))
        except Exception as error:
            print("[DEBUG] Could not update target.")
            print(error)
    
    def update_name(self, name):
        """
            Update the coordinator name.
            
            Returns:
                (String)
        """
        try:
            id = self.get_id()
            with self.db:
                self.db.execute("UPDATE Config Set name = ? where id = ?;", (name, id)).rowcount
                print("[DEBUG] New name: {name}.".format(name=name))
        except Exception as error:
            print("[DEBUG] Could not update name.")
            print(error)

    def update_mode(self, mode):
        """
            Update the coordinator mode.
            
            Returns:
                (String)
        """
        try:
            if mode in (0, 1):
                id = self.get_id()
                with self.db:
                    self.db.execute("UPDATE Config Set mode = ? where id = ?;", (mode, id)).rowcount
                    print("[DEBUG] New target: {mode}.".format(mode=mode))
            else:
                raise sqlite3.OperationalError
        except sqlite3.OperationalError:
            print("[ERROR] Invalid mode type. Use 0 or 1.")
        except Exception as error:
            print("[ERROR] Could not update mode.")
            print(error)

    def close(self):
        self.db.close()
