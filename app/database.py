import sqlite3 as sql
from datetime import datetime
import os 



def bd():
    conn = sql.connect("app.db")
    cur = conn.cursor()
    script = """
    CREATE TABLE IF NOT EXISTS users (
        idUser INTEGER PRIMARY KEY AUTOINCREMENT,
        nameUser TEXT UNIQUE NOT NULL,
        lastName TEXT NOT NULL,
        nickName TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        passwordUser TEXT NOT NULL,
        imageProfile TEXT NOT NULL,
        createdAt DATETIME NOT NULL
    );

    CREATE TABLE IF NOT EXISTS posts (
        idPost INTEGER PRIMARY KEY AUTOINCREMENT,
        titlePost TEXT NOT NULL,
        description TEXT NOT NULL,
        userId INTEGER NOT NULL,
        category TEXT NOT NULL,
        photoPost TEXT NOT NULL, 
        createdAt DATETIME NOT NULL,
        FOREIGN KEY (userId) REFERENCES users(idUser)
    );

    CREATE TABLE IF NOT EXISTS comments (
        idComment INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        postId INTEGER NOT NULL,
        userId INTEGER NOT NULL,
        createdAt DATETIME NOT NULL,
        FOREIGN KEY (postId) REFERENCES posts(idPost),
        FOREIGN KEY (userId) REFERENCES users(idUser)
    );
    """

    cur.executescript(script)

    # Ahora insertamos un usuario
    insert_user_query = """
    INSERT INTO users (nameUser, lastName, nickName, email, passwordUser, imageProfile, createdAt)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    data = (
        "Val", "Ovalle", "mirrorvall", "valov@gmail.com", "mirrorball", "mir.jpg", datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

    cur.execute(insert_user_query, data)
    

    conn.commit()

    # Cerrar la conexión
    conn.close()

    print("User inserted successfully!")

# Llamar a la función para crear la base de datos y la tabla, e insertar el usuario
if __name__ == "__main__":
    bd()
