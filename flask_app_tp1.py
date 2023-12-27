from flask import Flask

app = Flask(__name__)

@app.route("/")
def my_app():
    return 'Cluster 1 Instance 1 responding'

if __name__=='__main__':
    app.run("0.0.0.0:8000")