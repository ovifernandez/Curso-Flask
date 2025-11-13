from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, IntegerField, \
    TextAreaField, SelectField, PasswordField, HiddenField
from wtforms.fields import EmailField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, NumberRange # Esto está perfecto

class FormCategoria(FlaskForm):
    nombre = StringField("Nombre:",
                         validators=[DataRequired("Tienes que introducir el dato")] # <-- CAMBIO AQUÍ
                         )
    submit = SubmitField('Enviar')


class FormArticulo(FlaskForm):
    nombre = StringField("Nombre:",
                         validators=[DataRequired("Tienes que introducir el dato")] # <-- CAMBIO AQUÍ
                         )
    precio = DecimalField("Precio:", default=0,
                          validators=[DataRequired("Tienes que introducir el dato")] # <-- CAMBIO AQUÍ
                          )
    iva = IntegerField("IVA:", default=21,
                       validators=[DataRequired("Tienes que introducir el dato")]) # <-- CAMBIO AQUÍ
    descripcion = TextAreaField("Descripción:")
    photo = FileField('Selecciona imagen:')
    stock = IntegerField("Stock:", default=1,
                         validators=[DataRequired("Tienes que introducir el dato")] # <-- CAMBIO AQUÍ
                         )
    CategoriaId = SelectField("Categoría:", coerce=int)
    submit = SubmitField('Enviar')


class FormSINO(FlaskForm):
    si = SubmitField('Si')
    no = SubmitField('No')


class LoginForm(FlaskForm):
    username = StringField('Login', validators=[DataRequired()]) # <-- CAMBIO AQUÍ
    password = PasswordField('Password', validators=[DataRequired()]) # <-- CAMBIO AQUÍ
    submit = SubmitField('Entrar')


class FormUsuario(FlaskForm):
    username = StringField('Login', validators=[DataRequired()]) # <-- CAMBIO AQUÍ
    password = PasswordField('Password', validators=[DataRequired()]) # <-- CAMBIO AQUÍ
    nombre = StringField('Nombre completo')
    email = EmailField('Email')
    submit = SubmitField('Aceptar')


class FormChangePassword(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()]) # <-- CAMBIO AQUÍ
    submit = SubmitField('Aceptar')


class FormCarrito(FlaskForm):
    id = HiddenField()
    cantidad = IntegerField('Cantidad', default=1,
                            validators=[NumberRange(min=1,
                                                    message="Debe ser un númer"
                                                            "o positivo"),
                                        DataRequired("Tienes que introducir el " # <-- CAMBIO AQUÍ
                                                     "dato")])
    submit = SubmitField('Aceptar') # <-- CAMBIO AQUÍ (eliminé el error 'ç')