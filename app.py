import os
from flask import Flask
import pickle
from Artist import *
from User import *
from KNN import *

def save(dObj, sFilename):
    """Given an object and a file name, write the object to the file using pickle."""

    f = open(sFilename, "w")
    p = pickle.Pickler(f)
    p.dump(dObj)
    f.close()

def load(sFilename):
    """Given a file name, load and return the object stored in the file."""

    f = open(sFilename, "r")
    u = pickle.Unpickler(f)
    dObj = u.load()
    f.close()
    return dObj

# initialization
# load data
pathToData = os.path.join(app.root_path, 'static','data','hetrec2011-lastfm-2k-built')
UserManager = load(os.path.join(pathToData,'user-manager.pkr'))
ArtistManager = load(os.path.join(pathToData, 'artist-manager.pkr'))
TrainUserManager = load(os.path.join(pathToData, 'train-user-manager.pkr'))
# build app
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)

#controllers
@app.route("/")
def index():
    return 'user number:'+str(len(UserManager))+'; artist number:'+str(len(ArtistManager))

# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
