import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Lista que simula o banco de dados
db_posts = []

@app.route('/')
def index():
    search_query = request.args.get('search', '').lower()
    # MOSTRA APENAS APROVADOS
    posts = [p for p in db_posts if p['status'] == 'aprovado']
    if search_query:
        posts = [p for p in posts if search_query in p['title'].lower()]
    return render_template('index.html', posts=posts)

@app.route('/upload', methods=['POST'])
def upload():
    title = request.form.get('title')
    file = request.files['file']
    if file and title:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        db_posts.append({
            'id': len(db_posts),
            'title': title,
            'url': f'/static/uploads/{filename}',
            'comments': [],
            'status': 'pendente' # Fica invisível até você aprovar
        })
    return "<h2>Enviado! Aguarde o administrador aprovar sua foto.</h2><a href='/'>Voltar</a>"

@app.route('/admin')
def admin():
    # Painel para você ver o que está pendente
    pendentes = [p for p in db_posts if p['status'] == 'pendente']
    return render_template('admin.html', posts=pendentes)

@app.route('/aprovar/<int:post_id>')
def aprovar(post_id):
    for post in db_posts:
        if post['id'] == post_id:
            post['status'] = 'aprovado'
    return redirect(url_for('admin'))

@app.route('/recusar/<int:post_id>')
def recusar(post_id):
    global db_posts
    db_posts = [p for p in db_posts if p['id'] != post_id]
    return redirect(url_for('admin'))

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    comment_text = request.form.get('comment')
    for post in db_posts:
        if post['id'] == post_id and comment_text:
            post['comments'].append(comment_text)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
