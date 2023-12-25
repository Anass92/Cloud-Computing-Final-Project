from flask import Flask,jsonify
from transformers import DistilBertTokenizer,DistilBertForSequenceClassification
import torch
import random
import string

app=Flask(__name__)

tokenizer=DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model=DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased',num_labels=2)

def generate_random_text(length=50):
    letters=string.ascii_lowercase + ' '
    return ''.join(random.choice(letters) for i in range(length))

@app.route('/run_model',methods=['POST'])
def run_model():
    input_text=generate_random_text()
    inputs=tokenizer(input_text,return_tensors='pt',padding=True,truncation=True)
    outputs=model(**inputs)

    probabilities=torch.softmax(outputs.logits,dim=-1)

    probabilities_list=probabilities.tolist()[0]

    return jsonify({"input_text": input_text,"probabilities":probabilities_list})

if __name__=='__main__':
    # TO BE ADJUST FOR ADEQUATE 
    app.run(host='0.0.0.0',port=5000)