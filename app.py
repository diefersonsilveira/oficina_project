from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from config import db_config
from functools import wraps
from fpdf import FPDF
import os
from flask_login import login_required
import base64
from io import BytesIO

app = Flask(__name__)
app.secret_key = 'chave_super_secreta'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def get_db_connection():
    return mysql.connector.connect(**db_config)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Faça login para acessar esta página.", "info")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuario WHERE usuario = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user and check_password_hash(user['senha'], password):
            session['user_id'] = user['id']
            flash("Login realizado com sucesso!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Credenciais inválidas.", "danger")
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['usuario']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm']
        
        if password != confirm_password:
            flash("As senhas não coincidem.", "danger")
            return redirect(url_for('register'))

        password_hash = generate_password_hash(password)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO usuario (usuario, email, senha) 
                VALUES (%s, %s, %s)
            """, (usuario, email, password_hash))
            conn.commit()
            flash("Cadastro realizado com sucesso!", "success")
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            conn.rollback()
            flash("Email ou usuário já cadastrado.", "danger")
        finally:
            cursor.close()
            conn.close()
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/clientes', methods=['GET', 'POST'])
@login_required
def clientes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM cliente")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('clientes.html', clientes=clientes)

@app.route('/cadastrar_cliente', methods=['POST'])
@login_required
def cadastrar_cliente():
    nome = request.form['nome']
    contato = request.form['contato']
    endereco = request.form['endereco']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO cliente (nome, contato, endereco)
            VALUES (%s, %s, %s)
        """, (nome, contato, endereco))
        conn.commit()
        flash("Cliente cadastrado com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao cadastrar cliente: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('clientes'))

@app.route('/editar_cliente/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        nome = request.form['nome']
        contato = request.form['contato']
        endereco = request.form['endereco']
        
        try:
            cursor.execute("""
                UPDATE cliente 
                SET nome = %s, contato = %s, endereco = %s 
                WHERE idCliente = %s
            """, (nome, contato, endereco, id))
            conn.commit()
            flash("Cliente atualizado com sucesso!", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Erro ao atualizar cliente: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('clientes'))
    
    cursor.execute("SELECT * FROM cliente WHERE idCliente = %s", (id,))
    cliente = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('editar_cliente.html', cliente=cliente)

@app.route('/excluir_cliente/<int:id>', methods=['POST'])
@login_required
def excluir_cliente(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cliente WHERE idCliente = %s", (id,))
        conn.commit()
        flash("Cliente excluído com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao excluir cliente: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('clientes'))

@app.route('/carros')
@login_required
def carros():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT c.*, cl.nome AS nome_cliente FROM carro c LEFT JOIN cliente cl ON c.idCliente = cl.idCliente")
    carros = cursor.fetchall()
    cursor.execute("SELECT idCliente, nome FROM cliente")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('carros.html', carros=carros, clientes=clientes)

@app.route('/cadastrar_carro', methods=['POST'])
@login_required
def cadastrar_carro():
    placa = request.form['placa']
    modelo = request.form['modelo']
    ano = request.form['ano']
    cliente_id = request.form['cliente_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO carro (placa, modelo, ano, idCliente) 
            VALUES (%s, %s, %s, %s)
        """, (placa, modelo, ano, cliente_id))
        conn.commit()
        flash("Carro cadastrado com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao cadastrar carro: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('carros'))

@app.route('/editar_carro/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_carro(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        placa = request.form['placa']
        modelo = request.form['modelo']
        ano = request.form['ano']
        idCliente = request.form['idCliente']
        
        try:
            cursor.execute("""
                UPDATE carro 
                SET placa = %s, modelo = %s, ano = %s, idCliente = %s 
                WHERE idCarro = %s
            """, (placa, modelo, ano, idCliente, id))
            conn.commit()
            flash("Carro atualizado com sucesso!", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Erro ao atualizar carro: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('carros'))
    
    cursor.execute("SELECT * FROM carro WHERE idCarro = %s", (id,))
    carro = cursor.fetchone()
    cursor.execute("SELECT * FROM cliente")
    clientes = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return render_template('editar_carro.html', carro=carro, clientes=clientes)

@app.route('/excluir_carro/<int:id>', methods=['POST'])
@login_required
def excluir_carro(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM carro WHERE idCarro = %s", (id,))
        conn.commit()
        flash("Carro excluído com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao excluir carro: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('carros'))

@app.route('/ordens_servico')
@login_required
def ordens_servico():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT os.*, c.modelo AS modelo_carro, cl.nome AS nome_cliente, m.nomeMecanico
        FROM ordemdeservico os
        JOIN carro c ON os.idCarro = c.idCarro
        JOIN cliente cl ON c.idCliente = cl.idCliente
        LEFT JOIN mecanico m ON os.idMecanico = m.idMecanico
    """)
    ordens_servico = cursor.fetchall()

    cursor.execute("""
        SELECT c.idCarro, c.modelo, cl.nome AS nome_cliente
        FROM carro c
        JOIN cliente cl ON c.idCliente = cl.idCliente
    """)
    carros = cursor.fetchall()

    cursor.execute("SELECT idMecanico, nomeMecanico FROM mecanico")
    mecanicos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template('ordens_servico.html', ordens_servico=ordens_servico, carros=carros, mecanicos=mecanicos)

@app.route('/cadastrar_ordem_servico', methods=['POST'])
@login_required
def cadastrar_ordem_servico():
    descricaoProblema = request.form['descricaoProblema']
    status = "EM ABERTO"
    carro_id = request.form['carro_id']
    mecanico_id = request.form['mecanico_id']
    pecasUtilizadas = request.form['pecasUtilizadas']
    servicosExecutados = request.form['servicosExecutados']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO ordemdeservico (descricaoProblema, status, idCarro, idMecanico, pecasUtilizadas, servicosExecutados) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (descricaoProblema, status, carro_id, mecanico_id, pecasUtilizadas, servicosExecutados))
        conn.commit()
        flash("Ordem de serviço cadastrada com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao cadastrar ordem de serviço: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('ordens_servico'))

@app.route('/editar_ordem_servico/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_ordem_servico(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        descricaoProblema = request.form['descricaoProblema']
        status = request.form['status']
        idCarro = request.form['idCarro']
        idMecanico = request.form['idMecanico']
        pecasUtilizadas = request.form['pecasUtilizadas']
        servicosExecutados = request.form['servicosExecutados']
        
        try:
            cursor.execute("""
                UPDATE ordemdeservico 
                SET descricaoProblema = %s, status = %s, idCarro = %s, idMecanico = %s, pecasUtilizadas = %s, servicosExecutados = %s 
                WHERE idOS = %s
            """, (descricaoProblema, status, idCarro, idMecanico, pecasUtilizadas, servicosExecutados, id))
            conn.commit()
            flash("Ordem de Serviço atualizada com sucesso!", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Erro ao atualizar Ordem de Serviço: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('ordens_servico'))
    
    cursor.execute("SELECT * FROM ordemdeservico WHERE idOS = %s", (id,))
    ordem_servico = cursor.fetchone()
    
    cursor.execute("""
        SELECT carro.idCarro, CONCAT(cliente.nome, ' - ', carro.modelo) AS carro_cliente
        FROM carro
        JOIN cliente ON carro.idCliente = cliente.idCliente
    """)
    carros = cursor.fetchall()
    
    cursor.execute("SELECT idMecanico, nomeMecanico FROM mecanico")
    mecanicos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('editar_ordem_servico.html', ordem_servico=ordem_servico, carros=carros, mecanicos=mecanicos)

@app.route('/finalizar_ordem_servico/<int:id>', methods=['POST'])
@login_required
def finalizar_ordem_servico(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT os.idOS, os.descricaoProblema, os.pecasUtilizadas, os.servicosExecutados,
               c.placa, c.modelo, cli.nome AS cliente_nome, m.nomeMecanico
        FROM ordemdeservico os
        JOIN carro c ON os.idCarro = c.idCarro
        JOIN cliente cli ON c.idCliente = cli.idCliente
        JOIN mecanico m ON os.idMecanico = m.idMecanico
        WHERE os.idOS = %s
    """, (id,))
    ordem_servico = cursor.fetchone()

    cursor.execute("UPDATE ordemdeservico SET status = 'FINALIZADO' WHERE idOS = %s", (id,))
    conn.commit()

    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Ordem de Serviço", 0, 1, "C")

    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"ID: {ordem_servico['idOS']}", 0, 1)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Descrição do Problema: {ordem_servico['descricaoProblema']}", 0, 1)
    pdf.cell(0, 10, f"Status: FINALIZADO", 0, 1)
    pdf.cell(0, 10, f"Peças Utilizadas: {ordem_servico['pecasUtilizadas']}", 0, 1)
    pdf.cell(0, 10, f"Serviços Executados: {ordem_servico['servicosExecutados']}", 0, 1)

    pdf.cell(0, 10, f"Carro (Cliente + Modelo): {ordem_servico['cliente_nome']} - {ordem_servico['modelo']}", 0, 1)
    pdf.cell(0, 10, f"Mecânico: {ordem_servico['nomeMecanico']}", 0, 1)
    
    pdf_buffer = BytesIO()
    pdf_buffer.write(pdf.output(dest='S').encode('latin1'))
    pdf_buffer.seek(0)

    flash("Ordem de serviço finalizada e PDF gerado com sucesso!", "success")
    
    return send_file(pdf_buffer, as_attachment=True, download_name=f"ordem_servico_{ordem_servico['idOS']}.pdf", mimetype='application/pdf')

@app.route('/mecanicos', methods=['GET', 'POST'])
@login_required
def mecanicos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM mecanico")
    mecanicos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('mecanicos.html', mecanicos=mecanicos)

@app.route('/cadastrar_mecanico', methods=['POST'])
@login_required
def cadastrar_mecanico():
    nome_mecanico = request.form['nome_mecanico']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO mecanico (nomeMecanico) VALUES (%s)", (nome_mecanico,))
        conn.commit()
        flash("Mecânico cadastrado com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao cadastrar mecânico: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('mecanicos'))

@app.route('/editar_mecanico/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_mecanico(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if request.method == 'POST':
        nome_mecanico = request.form['nome_mecanico']
        
        try:
            cursor.execute("UPDATE mecanico SET nomeMecanico = %s WHERE idMecanico = %s", (nome_mecanico, id))
            conn.commit()
            flash("Mecânico atualizado com sucesso!", "success")
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"Erro ao atualizar mecânico: {err}", "danger")
        finally:
            cursor.close()
            conn.close()
        
        return redirect(url_for('mecanicos'))
    
    cursor.execute("SELECT * FROM mecanico WHERE idMecanico = %s", (id,))
    mecanico = cursor.fetchone()
    cursor.close()
    conn.close()
    
    return render_template('editar_mecanico.html', mecanico=mecanico)

@app.route('/excluir_mecanico/<int:id>', methods=['POST'])
@login_required
def excluir_mecanico(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM mecanico WHERE idMecanico = %s", (id,))
        conn.commit()
        flash("Mecânico excluído com sucesso!", "success")
    except mysql.connector.Error as err:
        conn.rollback()
        flash(f"Erro ao excluir mecânico: {err}", "danger")
    finally:
        cursor.close()
        conn.close()
    
    return redirect(url_for('mecanicos'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Você saiu da sua conta.", "info")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)