from flask import Flask, render_template, request
from src.utils import *
from src.azure_utils import *
from werkzeug.utils import secure_filename
#import tensorflow as tf

upload_folder = os.path.join('static', 'images', 'prediction')
models_folder = os.path.join("static", "model")

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = upload_folder
app.config["MODELS_FOLDER"] = models_folder

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/start')
def insert():
    open_waste_slot()

    return render_template('insert.html')

@app.route('/picture', methods=["POST"])
def picture():
    if request.method == 'POST':
        #On vérifie que l'utilisateur a bien sélectionné une image
        if 'image' not in request.files:
            return render_template('insert.html')
        image = request.files['image']
        if image:
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            image.save(filepath)
            return render_template("insert.html", picture = filepath)
        return render_template('insert.html')
    return render_template('insert.html')

@app.route('/waste/pick-type', methods=["POST"])
def pick_type():
    if request.method == 'POST':
        close_waste_slot()
        picture = request.form['picture']
        predictions = make_a_prediction(picture)
        print(predictions)
        return render_template('type.html', predictions = predictions)
    return render_template('type.html')

@app.route('/waste/pick-type_sdk', methods=["POST"])
def pick_type_sdk():
    if request.method == 'POST':
        close_waste_slot()
        picture = request.form['picture']
        predictions = make_a_prediction_with_sdk(picture)
        print(predictions)
        return render_template('type.html', predictions = predictions)
    return render_template('type.html')

# @app.route('/waste/pick-type-dirty', methods=["POST"])
# def pick_type_dirty():
#     if request.method == 'POST':
#         close_waste_slot()
#         picture = request.form['picture']
#         pred_model = tf.keras.models.load_model(os.path.join(app.config["MODELS_FOLDER"], "model_ludo.keras"))
#         is_dirty = dirty_or_clean(pred_model, picture)
#         print(is_dirty)
#         if is_dirty:
#             return render_template("dirty.html")
#         else:
#             predictions = make_a_prediction(picture)
#             print(predictions)
#             return render_template('type.html', predictions = predictions)
#     return render_template('type.html')

@app.route('/confirmation', methods=['POST'])
def confirmation():
    waste_type = request.form['type']

    process_waste(waste_type)
    return render_template('confirmation.html')


if __name__ == "__main__":
    app.run(debug=True)
