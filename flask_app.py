import os
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, RadioField, SubmitField
from wtforms.validators import DataRequired

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-secreta-prova-final')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)


class Disciplina(db.Model):
    __tablename__ = 'disciplinas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    semestre = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<Disciplina {self.nome}>'


class DisciplinaForm(FlaskForm):
    nome = StringField('Cadastre a nova disciplina e o semestre associado:',
                       validators=[DataRequired()])
    semestre = RadioField('', default='1º semestre', choices=[
        (f'{i}º semestre', f'{i}º semestre') for i in range(1, 7)
    ])
    submit = SubmitField('Cadastrar')


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@app.route('/disciplinas', methods=['GET', 'POST'])
def disciplinas():
    form = DisciplinaForm()
    if form.validate_on_submit():
        nome = form.nome.data.strip()
        if Disciplina.query.filter_by(nome=nome).first():
            flash('Disciplina já cadastrada!', 'warning')
        else:
            db.session.add(Disciplina(nome=nome, semestre=form.semestre.data))
            db.session.commit()
            flash('Disciplina cadastrada com sucesso!', 'success')
        return redirect(url_for('disciplinas'))
    lista = Disciplina.query.order_by(Disciplina.id).all()
    return render_template('disciplinas.html', form=form, disciplinas=lista,
                           current_time=datetime.utcnow())


@app.errorhandler(404)
def page_not_found(e):
    # Módulos não desenvolvidos caem aqui (nenhuma outra rota é criada)
    return render_template('404.html', current_time=datetime.utcnow()), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', current_time=datetime.utcnow()), 500


if __name__ == '__main__':
    app.run(debug=True)
