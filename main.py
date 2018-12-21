__author__ = 'Erlemar'
# from functions import Model
from flask import Flask, render_template, request
from flask_cors import CORS, cross_origin
import base64
import os
import json
# import uuid
# import boto
# import boto3
# from boto.s3.key import Key
# from boto.s3.connection import S3Connection
import json
from flask import Flask, render_template, request, flash
from forms import ContactForm
import pandas as pd

app = Flask(__name__)
# model = Model()
CORS(app, headers=['Content-Type'])
app.config['SECRET_KEY'] = 'any secret string'


@app.route("/", methods=["POST", "GET", 'OPTIONS'])
def index_page():
    form = ContactForm()
    return render_template('index.html', form=form)


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/internals")
def internals():
    return render_template('internals.html')


@app.route("/models")
def models():
    return render_template('models.html')


@app.route('/hook2', methods=["GET", "POST", 'OPTIONS'])
def predict():
    """
	Decodes image and uses it to make prediction.
	"""
    if request.method == 'POST':
        # print(request.values)
        # image_b64 = request.values['imageBase64']
        received_text = request.values['text_data'].strip('"')

        print(received_text)

        with open('data/med.json', 'r', encoding='utf-8') as f:
            d = json.load(f)

        prediction = {}
        for k in d['740260'].keys():
            prediction[k] = ''

        found_texts1 = [(d[k], v) for k, v in d.items() if received_text in d[k]['full_text']]
        if len(found_texts1) > 0:
            id = found_texts1[0][1]
            found_texts = found_texts1[0]

        print(len(found_texts))

        prediction['found_count'] = len(found_texts1)

        if prediction['found_count'] == 0:
            prediction['found_count'] = str(prediction['found_count'])
            prediction['id'] = ''

            return json.dumps(prediction)

        else:
            prediction['found_count'] = str(prediction['found_count'])
            incident_data = found_texts[0]
            for k, v in incident_data.items():
                prediction[k] = v
                prediction['id'] = id

            df = pd.DataFrame.from_dict([i[0] for i in found_texts1])
            df.to_excel('report.xlsx', index=False)

            return json.dumps(prediction)


@app.route('/hook3', methods=["GET", "POST", 'OPTIONS'])
def train():
    """
	Decodes image and uses it to tain models.
	"""
    if request.method == 'POST':
        image_b64 = request.values['imageBase64']
        image_encoded = image_b64.split(',')[1]
        image = base64.decodebytes(image_encoded.encode('utf-8'))
        digit = request.values['digit']
    # model.train(image, digit)

    return 'Trained'


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)