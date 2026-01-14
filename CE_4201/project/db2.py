# Save data locally using tinydb.

from tinydb import TinyDB, Query
import datetime
db = None
decimals = 1

def set_up_db(path):
    """E.g.: "project/db2.json" """
    global db
    db = TinyDB(path)
    # add row if it is not already in db, row has id = 0
    if not len(db): db.insert({"id": 0, "timestamp": 0, 
                "roll": 0, "pitch": 0, "yaw": 0, "set_ref": 0,
                "temperature": 0, "angle": 0})
    
def update_row(roll, pitch, yaw, temperature, set_ref, ANGLE):
    """ update row 0
    returns data in format accepted by the mqtt protocol"""

    timestamp = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") # date and time
    data = {"id": 0, "timestamp": timestamp, 
               "roll": round(roll, decimals), "pitch": round(pitch, decimals), "yaw": round(yaw, decimals), "set_ref": set_ref,
               "temperature": round(temperature, decimals), "angle": ANGLE}
    
    db.update(data, Query().id == 0) # change row that has id = 0

    return data

def get_data():
    data = db.search(Query().id == 0)
    return data

# ignore this, for testing
if __name__ == "__main__":
    set_up_db("db2.json")
    print(get_data())



