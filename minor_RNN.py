import numpy as np
import pandas as pd
import scipy
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
import re
import logging  # Setting up the loggings to monitor gensim
from sklearn.utils import resample
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential,load_model
from keras.layers import LSTM, Dense, Dropout, Masking, Embedding,Conv1D,MaxPooling1D,GlobalMaxPooling1D,BatchNormalization

logging.basicConfig(format="%(levelname)s - %(asctime)s: %(message)s", datefmt= '%H:%M:%S', level=logging.INFO)
class RNN:

	def __init__(self):
		self.toxic_percentage=0
		self.severe_toxic_percentage=0
		self.obscene_percentage=0
		self.threat_percentage=0
		self.insut_percentage=0
		self.identity_hate_percentage=0

	def cleantxt(self,txt):
		stpw = stopwords.words('english')
		stpw.extend(['www', 'http', 'utc'])
		stpw = set(stpw)
		txt = re.sub(r"\n", " ", txt)
		txt = re.sub("[\<\[].*?[\>\]]", " ", txt)
		txt = txt.lower()
		txt = re.sub(r"[^a-z ]", " ", txt)
		txt = re.sub(r"\b\w{1,3}\b", " ", txt)
		txt = " ".join([x for x in txt.split() if x not in stpw])
		return txt

	def run_model(self):
		df = pd.read_csv('train.csv')
		df[['toxic', 'severe_toxic']]  # for selecting multiole columns we need to pass a list of the columns
		df.loc[0]  # loc operator is used to select a row,it returns a series object
		df.loc[
			[0, 1], ['toxic', 'threat']]  # for selecting multiole rows using loc,we need to pass a list of rows number
		n = len(df.index)
		df['toxicity'] = 1
		df.head()
		severe_toxic = 0
		toxic = 0
		obscene = 0
		threat = 0
		insult = 0
		identity_hate = 0
		non_toxic = 0
		for i in range(n):
			flag = 0
			if df.loc[i, 'severe_toxic'] == 1:
				severe_toxic = severe_toxic + 1
				flag = 1
			if df.loc[i, 'toxic'] == 1:
				toxic = toxic + 1
				flag = 1
			if df.loc[i, 'obscene'] == 1:
				obscene = obscene + 1
				flag = 1
			if df.loc[i, 'insult'] == 1:
				insult = insult + 1
				flag = 1
			if df.loc[i, 'threat'] == 1:
				threat = threat + 1
				flag = 1
			if df.loc[i, 'identity_hate'] == 1:
				identity_hate = identity_hate + 1
				flag = 1
			if flag == 0:
				non_toxic = non_toxic + 1
				df.at[i, 'toxicity'] = 0
		y_axis = [severe_toxic, toxic, identity_hate, insult, threat, obscene, non_toxic]
		x_axis = ['severe_toxic', 'toxic', 'identity_hate', 'insult', 'threat', 'obscene', 'non_toxic']
		total_toxic = n - y_axis[6]
		df_majority = df[df.toxicity == 0]
		df_minority = df[df.toxicity == 1]
		df_majority_downsample = resample(df_majority, replace=False, random_state=123, n_samples=5 * total_toxic)
		df_minority_upsample = resample(df_minority, replace=True, random_state=123, n_samples=5 * total_toxic)
		df = pd.concat([df_majority_downsample, df_minority_upsample])
		df.index = range(len(df.index))
		df.head()
		df['toxicity'].value_counts()
		df['comment_text'] = df.comment_text.apply(lambda x: self.cleantxt(x))
		rows = df.shape[:][0]
		for i in range(rows):
			if len(df['comment_text'][i]) == 0:
				# print(i)
				df = df.drop([i])
		df.index = range(len(df.index))
		x = df.iloc[:, 1]
		y = df.iloc[:, 2:]
		x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=123)
		sentences = list(x_train)
		for i in range(len(sentences)):
			sentences[i] = list(sentences[i].split())
		tokenizer = Tokenizer(num_words=22759,
							  filters='!"#$%&()*+,-./:;<=>?@[\\]^_`{|}~\t\n',
							  lower=True,
							  split=" ",
							  char_level=False)
		tokenizer.fit_on_texts(list(x_train))
		tokenized_train = tokenizer.texts_to_sequences(x_train)
		max_len = 100
		word_index = tokenizer.word_index
		data = pad_sequences(tokenized_train, padding='post', maxlen=max_len)
		y = np.array(y_train)
		data.shape
		# Load model
		rnn_model = load_model('minor_RNN.h5')
		dft=pd.read_csv('translate.csv')
		dft['text'] = df.comment_text.apply(lambda x: self.cleantxt(x))
		s=list(dft['text'])
		demo_data = tokenizer.texts_to_sequences(s)
		demo_data = pad_sequences(demo_data, maxlen=max_len, padding='post')
		demo_data
		predictions = rnn_model.predict(demo_data, verbose=1)
		nrows=dft.shape[:][0]
		dft['toxic_percentage']=1
		dft['severe_toxic_percentage']=1
		dft['obscene_percentage']=1
		dft['threat_percentage']=1
		dft['insut_percentage']=1
		dft['identity_hate_percentage']=1
		for i in range(nrows):
			dft.at[i,'toxic_percentage'] = 100 * predictions[i][0]
			dft.at[i,'severe_toxic_percentage'] = 100 * predictions[i][1]
			dft.at[i,'obscene_percentage'] = 100 * predictions[i][2]
			dft.at[i,'threat_percentage'] = 100 * predictions[i][3]
			dft.at[i,'insut_percentage'] = 100 * predictions[i][4]
			dft.at[i,'identity_hate_percentage']= 100 * predictions[i][5]
		dft.to_csv('translate_result.csv')


p=RNN()
p.run_model()

