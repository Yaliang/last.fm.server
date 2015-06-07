import os
import json
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

def splitTrainSetWithoutRemoving(userManager, percentage, userList = []):
    """split the train set by percentage, to """
    if len(userList) == 0:
        testUserIDList = random.sample(userManager, int(len(userManager)*percentage))
    else:
        testUserIDList = userList
    testUserSet = {}
    for userID in testUserIDList:
        testUser = userManager.pop(userID)
        testUserSet[userID] = testUser

    return testUserSet, testUserIDList

# initialization
# build app
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)
# load data
pathToData = os.path.join(app.root_path, 'static','data','hetrec2011-lastfm-2k-built')
UserManager = load(os.path.join(pathToData,'user-manager.pkr'))
ArtistManager = load(os.path.join(pathToData, 'artist-manager.pkr'))
TrainUserManager = load(os.path.join(pathToData, 'train-user-manager.pkr'))

#controllers
@app.route('/')
def index():
    return 'user number:'+str(len(UserManager))+'; artist number:'+str(len(ArtistManager))

@app.route('/testUserWithID/<int:testUserID>')
def testUser(testUserID):
    if not UserManager.has_key(testUserID):
        return "don't has user with userID = "+str(testUserID)
    testUserSet, testUserIDList = splitTrainSetWithoutRemoving(TrainUserManager, 0, [testUserID])
    knn = KNN(2)
    knn.training(TrainUserManager, ArtistManager)
    favOfOne = knn.testing(testUserSet[testUserID], UserManager, ArtistManager, True)
    realfavOfOne = UserManager[testUserID].getMostFav().keys()[0]
    ret = "The most listen artist:\n"+str(ArtistManager[realfavOfOne])+"\n"
    ret += "The artist we predict:\n"+str(ArtistManager[favOfOne])
    ret = ret.replace("\n","</br>")
    # recovery modified TrainUserManager
    TrainUserManager[testUserID]=testUserSet[testUserID]

    return ret
    
@app.route('/getArtist/<int:artistID>')
def getArtistName(artistID):
    maxArtistID = max(ArtistManager.keys())
    minArtistID = min(ArtistManager.keys())
    ret={}
    if artistID > maxArtistID or artistID < minArtistID:
        ret['error'] = 101
        ret = json.dumps(ret)
        return ret
    if not ArtistManager.has_key(artistID):
        ret['error'] = 102
        ret = json.dumps(ret)
        return ret
    
    ret['error'] = 0
    ret['id'] = artistID
    ret['name'] = ArtistManager[artistID].Name
    ret = json.dumps(ret)
    return ret


# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
