from flask import request, render_template, redirect, g, url_for, send_from_directory
import sqlite3
from datetime import datetime
from flask import Flask, session
from flask_session import Session
import os
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['DATABASE'] = os.path.join(app.root_path, 'site.db')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}



# Esta función te ayuda a obtener la conexión a la base de datos
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('app.db')
        g.db.row_factory = sqlite3.Row
    return g.db

# Esta función te ayuda a cerrar la conexión a la base de datos
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_routes(app):

    @app.route('/')
    def index():
            return redirect(url_for('login'))   

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            passwordUser = request.form['passwordUser']

            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

            if not all([email, passwordUser]):
                return render_template("login.html", message="Por favor, completa todos los campos.")

            if user and check_password_hash(user['passwordUser'], passwordUser):
                session['user_id'] = user['idUser']
                session['user_name'] = user['nameUser']
                return redirect(url_for('feedUser'))
            else:
                return render_template('login.html', message="Credenciales incorrectas.")

        return render_template('login.html')
    
    @app.route("/register")
    def register():
        return render_template("register.html")
    
    @app.route("/register/i", methods=["POST"])
    def registerUsers():
        if request.method == 'POST':
            # Obtener datos del formulario
            nameUser = request.form.get('nameUser')
            lastName = request.form.get('lastName')
            nickName = request.form.get('nickName')
            email = request.form.get('email')
            passwordUser = request.form.get('passwordUser')

            if not all([nameUser, lastName, nickName, email, passwordUser]):
                return render_template("register.html", message="Por favor, completa todos los campos.")
                

            hashed_password = generate_password_hash(passwordUser)
            print(f"Hashed Password: {hashed_password}")

            # Obtener conexión a la base de datos
            db = get_db()
            cursor = db.cursor()

            cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                close_db()
                return render_template("register.html", message="El correo electrónico ya está registrado. Por favor, usa otro.")

            # Insertar datos en la base de datos
            cursor.execute(
                "INSERT INTO users (nameUser, lastName, nickName, email, passwordUser, imageProfile, createdAt) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (nameUser, lastName, nickName, email, hashed_password, 'default_profile.jpg', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )
            db.commit()

            # Cerrar la conexión a la base de datos
            close_db()
        
        return render_template("login.html")
    
    @app.route("/feed", methods=['GET'])
    def feedUser():
        
        user_id = session.get('user_id')
        if 'user_id' not in session:
            return redirect(url_for('login'))

        conn = get_db()
        query = '''
        SELECT posts.idPost, posts.titlePost, posts.description, posts.photoPost, posts.category, posts.createdAt, users.nickname
        FROM posts
        JOIN users ON posts.userId = users.idUser
        WHERE posts.userId != ?
        '''
        
        posts = conn.execute(query, (user_id,)).fetchall()
        return render_template('feed.html', posts=posts)
 
    
    @app.route("/post")
    def createPost():
        return render_template("post.html")
    

    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

    
    @app.route("/post/i", methods=["POST"])
    def createPostUsers():
            if request.method == 'POST':
                titlePost = request.form['titlePost']
                description = request.form['description']
                category = request.form['category']
                photoPost = request.files['photoPost']

                print(f"Title: {titlePost}")
                print(f"Decription: {description}")
                print(f"Category: {category}")
                print(f"Photo: {photoPost.filename}")

                if photoPost and allowed_file(photoPost.filename):
                    filename = secure_filename(photoPost.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    photoPost.save(filepath)
                    photo_url = f'/{app.config["UPLOAD_FOLDER"]}/{filename}'

                    print(f"File path: {filepath}")
                    print(f"Photo URL: {photo_url}")

                    try:
                        db = get_db()
                        cursor = db.cursor()
                        cursor.execute('INSERT INTO posts (titlePost, description, userId, category,  photoPost, createdAt) VALUES (?, ?, ?, ?, ?, ?)',
                                    (titlePost, description, session['user_id'], category, photo_url, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
                        db.commit()
                        
                        # Print the newly inserted data
                        cursor.execute('SELECT * FROM posts WHERE titlePost = ? AND description = ?', (titlePost, description))
                        new_post = cursor.fetchone()
                        print(f"New post inserted: {new_post}")

                        return redirect(url_for('createPost'))
                    except sqlite3.Error as e:
                        print(f"Error al insertar en la base de datos: {e}")
                        return 'Error al guardar en la base de datos.'

            return render_template('post.html')
    
    @app.route('/uploads/<filename>')
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    def get_current_user():
        user_id = session.get('user_id')
        if user_id:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM users WHERE idUser = ?", (user_id,))
            return cursor.fetchone()
        return None
    
    @app.route("/profile", methods=['GET'])
    def userProfile():
        user = get_current_user()
        if user:
            # Obtener las publicaciones del usuario desde la base de datos
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT * FROM posts WHERE userId = ? ORDER BY createdAt DESC", (user['idUser'],))
            posts = cursor.fetchall()
            
            return render_template('profile.html', user=user, posts=posts)
        else:
            return 'Usuario no encontrado.', 404
        
 
    
    def get_post_by_id(idPost):
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT p.idPost, p.titlePost, p.description, p.photoPost, u.nickName
            FROM posts p
            INNER JOIN users u ON p.userId = u.idUser
            WHERE p.idPost = ?
        """
        cursor.execute(query, (idPost,))
        post = cursor.fetchone()
        cursor.close()

        if post:
            print(f"Post encontrado: {dict(post)}")
        else:
            print("No se encontró ninguna publicación con el ID proporcionado.")
        
        return post
    
    # Depuración: Imprimir el resultado de la consulta
        

    @app.route('/post/<int:idPost>', methods=['GET', 'POST'])
    def detailsPost(idPost):
        db = get_db()

        userId = session['user_id']

        if request.method == 'POST':
            content = request.form['content']
            db.execute('INSERT INTO comments (postId, userId, content, createdAt) VALUES (?, ?, ?, ?)', (idPost, session['user_id'], content, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            db.commit()

        post = get_post_by_id(idPost)
        comments = get_comments_by_post_id(idPost)
        
        # Depuración: Imprimir los detalles del post y comentarios
        if post:
            print(f"Detalles del post: {dict(post)}")
        if comments:
            for comment in comments:
                print(f"Comentario: {dict(comment)}")
        
        return render_template('details.html', post=post, comments=comments)
    
    @app.route('/post/<int:idPost>', methods=['POST'])
    def add_comment(idPost):
        if 'user_id' not in session:
            return redirect(url_for('login'))

        # Obtener el contenido del comentario desde el formulario
        content = request.form.get('content')

        # Obtener el userId de la sesión actual
        userId = session['user_id']

        try:
            conn = get_db()
            cursor = conn.cursor()

            # Insertar el comentario en la tabla comments
            query = 'INSERT INTO comments (postId, userId, content) VALUES (?, ?, ?)'
            cursor.execute(query, (idPost, userId, content))
            conn.commit()

            
            return redirect(url_for('detailsPost', idPost=idPost))

        except Exception as e:
            print(f"Error al agregar comentario: {str(e)}")
            return('Ocurrió un error al agregar el comentario. Inténtelo de nuevo más tarde.', 'error')
            return redirect(url_for('detailsPost', idPost=idPost))
        
   
    def get_comments_by_post_id(post_id):
        db = get_db()
        cursor = db.cursor()
        query = """
            SELECT c.content, u.nickname, u.imageProfile
            FROM comments c
            INNER JOIN users u ON c.userId = u.idUser
            WHERE c.postId = ?
        """
        cursor.execute(query, (post_id,))
        comments = cursor.fetchall()
        cursor.close()
        return comments
        
    @app.route("/delete_post/<int:idPost>", methods=["POST"])
    def delete_post(idPost):
            if 'user_id' not in session:
                return redirect(url_for('login'))

            user_id = session['user_id']
            db = get_db()
            cursor = db.cursor()

            # Verificar que la publicación pertenece al usuario
            cursor.execute("SELECT userId FROM posts WHERE idPost = ?", (idPost,))
            post = cursor.fetchone()

            if post and post['userId'] == user_id:
                cursor.execute("DELETE FROM posts WHERE idPost = ?", (idPost,))
                db.commit()
                message = "Publicación eliminada con éxito."
            else:
                message = "No tienes permiso para eliminar esta publicación o no existe."

            cursor.close()
            return redirect(url_for('userProfile', message=message))
    


   
        
    

