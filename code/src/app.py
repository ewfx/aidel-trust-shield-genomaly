from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os
from wtforms.validators import InputRequired
import spacy
app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

@app.route('/', methods=['GET',"POST"])
@app.route('/home', methods=['GET',"POST"])
def home():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))) # Then save the file
        filename = secure_filename(file.filename)
        file_full_path=os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename))
        file_content=get_file_text(file_full_path)
        #return "File has been uploaded."
        #return file_content
        entity=extratct_entities(file_content)
        entity_org=[item[0] for item in entity if item[1] == "ORG"]
        return entity_org
    return render_template('index.html', form=form)

def get_file_text(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content

def extratct_entities(file_content):
    texts=[file_content]
    nlp = spacy.load('en_core_web_md')
    docs=[nlp(text) for text in texts]
    for doc in docs:
        entities=[(ent.text, ent.label_) for ent in doc.ents]
        return entities
        #print("Entities: ", entities)

@app.route('/entity/')
def entity():
    return render_template('entity.html')


if __name__ == '__main__':
    app.run(debug=True)