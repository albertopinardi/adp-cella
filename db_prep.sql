CREATE TABLE records(id INTEGER PRIMARY KEY AUTOINCREMENT, time, temp_freezer , temp_frigor , tens_freezer, tens_frigor );
CREATE TABLE alerts (id INTEGER PRIMARY KEY AUTOINCREMENT, fid , type, dest, err, FOREIGN KEY(fid) REFERENCES records(id));
