Folder entity analysis\dataset contains the dataset “ner_dataset.csv”. This dataset has been downloaded from Kaggle. The dataset contains both POS and Entity Tags as mentioned below. I am using LSTM, a TensorFlow model, which has been trained with this dataset. Incase the Entity is not found in Spacy, the NLP Library , I can use this model to predict the Entity type
o	# geo = Geographical Entity
o	# org = Organization
o	# per = Person
o	# gpe = Geopolitical Entity
o	# tim = Time indicator
o	# art = Artifact
o	# eve = Event
o	# nat = Natural Phenomenon
o	
The NLP Library that is being used is Spacy. 
The Web api used is Flask API.. Check app.py and Templates folder
Statis folder is where I am storing the files uploaded. I am extracting text from the file once it is uploaded
Technology Hackathon-Trust-Shield-Genomaly.pptx is the PPT file which explains the workflow of the challenge.
transaction.txt is the input file
fraud_detection_output.csv is the output file