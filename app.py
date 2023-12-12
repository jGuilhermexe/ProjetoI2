from flask import Flask, render_template, request, redirect, url_for, session, flash, abort
from flaskext.mysql import MySQL
#from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)
app.secret_key = '1'

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'tratamento_db'
app.config['MYSQL_DATABASE_PORT'] = 3306

mysql = MySQL(app)
mysql.init_app(app)


def get_db():
    try:
        conn = mysql.connect()
        if conn is None:
            raise Exception("Não foi possível estabelecer uma conexão com o banco de dados.")
        return conn
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados no get_db(): {str(e)}")
        return None

    #return mysql.connection

def close_db(e=None):
    conn = mysql.connection
    conn.close()

@app.before_first_request
def criar_tabela():
    try:
        with app.app_context(), app.open_resource('schema.sql') as f:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(f.read().decode('utf8'))
            db.commit()
    except Exception as e:
        flash(f"Erro ao criar tabela: {str(e)}", 'erro')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/testar-conexao')
def testar_conexao():
    try:
        with app.app_context(), mysql.connection.cursor() as cur:
            cur.execute("SELECT 1")
        return 'Conexão com o banco de dados bem-sucedida!'
    except Exception as e:
        return f'Erro ao conectar ao banco de dados: {str(e)}'

@app.route('/pagina-de-cadastro', methods=['GET', 'POST'])
def pagina_cadastro():
    if request.method == 'POST':
        try:
            email = request.form['email']
            nome = request.form['nome']
            senha = request.form['senha']

            conexao = mysql.connect()
            cur = conexao.cursor()
            cur.execute('''
                INSERT INTO usuarios (email, nome, senha)
                VALUES (%s, %s, %s)
            ''', (email, nome, senha))
            conexao.commit()
            cur.close()
            conexao.close()

            flash('Cadastro bem-sucedido! Faça login para continuar.', 'sucesso')
            return redirect(url_for('index'))

        except Exception as e:
            flash(f"Erro ao cadastrar usuário: {str(e)}", 'erro')

    return render_template('pagina-de-cadastro.html')

@app.route('/fazer-login', methods=['GET','POST'])
def fazer_login():
    if request.method == 'POST':
        try:
            email = request.form['email']
            senha_digitada = request.form['senha']

            #conn = mysql.connect()
            #cur = conn.cursor()

            #cur.execute('''
            #            SELECT * FROM usuarios
            #            WHERE email = %s
            #''', (email,))
            #usuario = cur.fetchone()

            with app.app_context():
                conn = get_db()
                if conn is not None:
                    cur = conn.cursor()
                    cur.execute('''
                        SELECT * FROM usuarios
                        WHERE email = %s AND senha = %s
                    ''', (email, senha_digitada))
                    usuario = cur.fetchone()
                    cur.close()
                else:
                    flash('Erro ao conectar ao banco de dados no login.', 'erro')
                    return redirect(url_for('index'))

            

            # with mysql.connection.cursor() as cur:
            #     try:
            #         cur.execute('''
            #             SELECT * FROM usuarios
            #             WHERE email = %s AND senha = %s
            #         ''', (email, senha_digitada))
            #         usuario = cur.fetchone()
            #         flash(f"conectou ao banco de dados eu acho...")
            #     except Exception as e:
            #         flash(f"Erro ao executar consulta: {str(e)}", 'erro')
            #         return redirect(url_for('index'))

                
            #conn.commit()
            #cur.close()
            #conn.close()

            if usuario:
                session['usuario_id'] = usuario[0]
                flash('Login bem-sucedido!', 'sucesso')
                print('Redirecionando para o dashboard...')
                return redirect(url_for('dashboard'))  
            else:
                flash('Credenciais inválidas. Tente novamente.', 'erro')
                return redirect(url_for('index'))

        except Exception as e:
            flash(f"Erro ao fazer login: {str(e)}", 'erro')
            #return redirect(url_for('index'))

    #return render_template('index.html')
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'usuario_id' in session:
        return render_template('dashboard.html')
    else:
        flash('Você precisa fazer login primeiro.', 'erro')
        return redirect(url_for('index'))
    
@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Logout bem-sucedido!', 'sucesso')
    return redirect(url_for('index'))


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function



if __name__ == '__main__':
    app.run(debug=True)
