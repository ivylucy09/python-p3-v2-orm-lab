from __init__ import CURSOR, CONN
from department import Department
from employee import Employee

class Review:

    # Dictionary of objects saved to the database.
    all = {}

    def __init__(self, year, summary, employee_id, id=None):
        self.id = id
        self.year = year
        self.summary = summary
        self.employee_id = employee_id

    def __repr__(self):
        return (
            f"<Review {self.id}: {self.year}, {self.summary}, "
            + f"Employee: {self.employee_id}>"
        )

    @classmethod
    def create_table(cls):
        """ Create a new table to persist the attributes of Review instances """
        sql = """
            CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY,
            year INT,
            summary TEXT,
            employee_id INTEGER,
            FOREIGN KEY (employee_id) REFERENCES employee(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Review instances """
        sql = """
            DROP TABLE IF EXISTS reviews;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        """ 
        Insert a new row with the year, summary, and employee id values of the current Review object.
        Update the object id attribute using the primary key value of the new row.
        Save the object in local dictionary using table row's PK as dictionary key
        """
        if self.id is None:
            CURSOR.execute('''
                INSERT INTO reviews (year, summary, employee_id)
                VALUES (?, ?, ?)
            ''', (self.year, self.summary, self.employee_id))
            self.id = CURSOR.lastrowid
            Review.all[self.id] = self
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        """ 
        Initialize a new Review instance and save the object to the database.
        Return the new instance. 
        """
        review = cls(year, summary, employee_id)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        """ 
        Return a Review instance having the attribute values from the table row. 
        Check the dictionary for an existing instance using the row's primary key.
        """
        id = row[0]
        if id in cls.all:
            return cls.all[id]
        review = cls(row[1], row[2], row[3])
        review.id = id
        cls.all[id] = review
        return review

    @classmethod
    def find_by_id(cls, id):
        """ 
        Return a Review instance having the attribute values from the table row with the given id. 
        """
        sql = "SELECT * FROM reviews WHERE id = ?"
        row = CURSOR.execute(sql, (id,)).fetchone()
        if row:
            return cls.instance_from_db(row)
        return None

    def update(self):
        """ 
        Update the table row corresponding to the current Review instance.
        """
        if self.id:
            CURSOR.execute('''
                UPDATE reviews SET year = ?, summary = ?, employee_id = ?
                WHERE id = ?
            ''', (self.year, self.summary, self.employee_id, self.id))
            CONN.commit()

    def delete(self):
        """ 
        Delete the table row corresponding to the current Review instance.
        Delete the dictionary entry and set the id attribute to None.
        """
        if self.id:
            CURSOR.execute('DELETE FROM reviews WHERE id = ?', (self.id,))
            del Review.all[self.id]
            self.id = None
        CONN.commit()

    @classmethod
    def get_all(cls):
        """ 
        Return a list containing one Review instance per table row. 
        """
        sql = "SELECT * FROM reviews"
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    # Property Methods

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer greater than or equal to 2000.")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("Summary must be a non-empty string.")
        self._summary = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        sql = "SELECT id FROM employees WHERE id = ?"
        if CURSOR.execute(sql, (value,)).fetchone() is None:
            raise ValueError("Employee ID must reference an existing employee.")
        self._employee_id = value

