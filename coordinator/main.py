from flask import Flask

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] == True


@app.route("/")
def home():
    return "Hello, World"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)