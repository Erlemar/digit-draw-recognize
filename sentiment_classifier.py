__author__ = 'Artgor'
from sklearn.externals import joblib

class SentimentClassifier(object):
    def __init__(self):
        #self.model = joblib.load("LogisticRegression_default")
        #self.vectorizer = joblib.load("TfidfVectorizer_1-2_gram")
        self.classes_dict = {0: "негативным", 1: "позитивным"}
		
    def simple_calculation(self, text):
        try:
            float(text)
        except ValueError:
            return "Not a float"
        a1 = float(text)
        a2 = 6
        return str(a1 + a2)
'''
    @staticmethod
    def get_probability_words(probability):
        if probability < 0.55:
            return "небольшой"
        elif probability < 0.7:
            return "хорошей"
        elif probability < 0.95:
            return "высокой"
        elif probability > 0.95:
            return "практически полной"
        else:
            return ""

    def predict(self, text):
        vectorized = self.vectorizer.transform([text])
        return self.model.predict(vectorized)[0], self.model.predict_proba(vectorized)[0].max()

    def get_prediction_message(self, text):
        prediction = self.predict(text)
        print(prediction)
        class_prediction = prediction[0]
        prediction_probability = prediction[1]
        if self.get_probability_words(prediction_probability) == '':
            return 'Модель не смогла оценить этот отзыв. Возможно, что он слишком короткий или не содержит информацию, использованную в тренировочной выборке. Пожалуйста, введите другой отзыв.'
        else:
            return 'Модель считает этот отзыв ' + self.classes_dict[class_prediction] + ' с ' + self.get_probability_words(prediction_probability) + ' уверенностью. Вероятность - ' + str(prediction_probability) + '.'
'''
