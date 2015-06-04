import os
from flask import Flask

# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

#controllers
@app.route("/")
def index():
    pathToData = os.path.join(app.root_path, 'static','data')
    f = open(os.path.join(pathToData, 'testdata.data'),'r')
    data = f.readline()
    f.close()
    return data

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
