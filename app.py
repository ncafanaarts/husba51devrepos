import os
from flask import Flask, render_template, request, redirect, url_for
import cloudinary
import cloudinary.uploader

app = Flask(__name__)

# CONFIGURAÇÃO DO CLOUDINARY (Pegue no painel do Cloudinary)
cloudinary.config( 
  cloud_name = "COLOQUE_AQUI", 
  api_key = "COLOQUE_AQUI", 
  api_secret = "COLOQUE_AQUI",
  secure = True
)

# Lista de posts (Em um site profissional usaríamos um Banco de Dados)
db_posts = []

@app.route('/')
def index():
    search_query = request.args.get('search', '').lower()
    posts = [p for p in db_posts if p['status'] == 'aprovado']
    if search_query:
        posts = [p for p in posts if search_query in p['title'].lower()]
    return render_template('index.html', posts=posts)

@app.route('/upload', methods=['POST'])
def upload():
    title = request.form.get('title')
    file = request.files['file']
    if file and title:
        # Envia para o Cloudinary em vez de salvar na pasta local
        upload_result = cloudinary.uploader.upload(file)
        img_url = upload_result['secure_url']
        
        db_posts.append({
            'id': len(db_posts),
            'title': title,
            'url': img_url,
            'comments': [],
            'status': 'pendente'
        })
    return "<h2>Enviado! Aguarde a aprovação.</h2><a href='/'>Voltar</a>"

@app.route('/admin')
def admin():
    pendentes = [p for p in db_posts if p['status'] == 'pendente']
    return render_template('admin.html', posts=pendentes)

@app.route('/aprovar/<int:post_id>')
def aprovar(post_id):
    for post in db_posts:
        if post['id'] == post_id:
            post['status'] = 'aprovado'
    return redirect(url_for('admin'))

@app.route('/comment/<int:post_id>', methods=['POST'])
def add_comment(post_id):
    comment_text = request.form.get('comment')
    for post in db_posts:
        if post['id'] == post_id and comment_text:
            post['comments'].append(comment_text)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run()
