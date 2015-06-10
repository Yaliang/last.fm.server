import os
import json
from flask import Flask, request
from flask.ext.cors import CORS

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
cors = CORS(app)
app.config.update(
    DEBUG = True,
)
# load data
pathToData = os.path.join(app.root_path, 'static','data','hetrec2011-lastfm-2k-built')
UserManager = load(os.path.join(pathToData,'user-manager.pkr'))
ArtistManager = load(os.path.join(pathToData, 'artist-manager.pkr'))
TrainUserManager = load(os.path.join(pathToData, 'train-user-manager.pkr'))
TagManager = load(os.path.join(pathToData, 'tag-manager.pkr'))

#controllers
@app.route('/')
def index():
    return 'user number:'+str(len(UserManager))+'; artist number:'+str(len(ArtistManager))

@app.route('/testUserWithID/<int:testUserID>')
def testUser(testUserID):
    if not UserManager.has_key(testUserID):
        return "don't has user with userID = "+str(testUserID)
    testUserSet, testUserIDList = splitTrainSetWithoutRemoving(TrainUserManager, 0, [testUserID])
    knn = KNN(40)
    knn.training(TrainUserManager, ArtistManager)
    favOfOne, allArtist, allTag = knn.testing(testUserSet[testUserID], UserManager, ArtistManager, True)
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

@app.route('/mockUserWithArtist/',methods=['POST'])
def buildMockUser():
    artists = request.form['artists']
    artistlist = json.loads(artists)
    testUser = User(-100)
    missingArtist = []
    for artistRecord in artistlist:
        artistID = int(artistRecord.keys()[0])
        artistWeight = artistRecord.values()[0]
        if artistWeight == 0:
            artistWeight = 0.0000001
        if ArtistManager.has_key(artistID):
            testUser.insertArt(artistID, artistWeight)
        else:
            missingArtist.append(artistID)
    knn = KNN(40)
    knn.training(UserManager, ArtistManager)
    favOfOne, allArtist, allTag = knn.testing(testUser, UserManager, ArtistManager, True)
    ret = {'artistID': favOfOne}
    if len(missingArtist) > 0:
        ret['warning'] = {'missingArtist':missingArtist}

    ret['artists'] = []
    allArtistLen = len(allArtist)-1
    maxArtistMatchWeight = allArtist[-1][1]
    for i in range(allArtistLen, max(-1, allArtistLen-10), -1):
        artistID = allArtist[i][0]
        matchWeight = allArtist[i][1] / maxArtistMatchWeight
        artistName = ArtistManager[artistID].Name
        topTag = ArtistManager[artistID].getTopTag()
        if topTag == -1:
            topTagName = ""
        else:
            topTagName = TagManager[topTag]
        ret['artists'].append({'id':artistID, 'name':artistName, 'match':matchWeight, 'tag':topTag, 'tagName':topTagName})

    ret['tags'] = []
    allTagLen = len(allTag)-1
    for i in range(allTagLen, max(-1, allTagLen-10), -1):
        tagID = allTag[i][0]
        tagWeight = allTag[i][1]
        tagName = TagManager[tagID]
        ret['tags'].append({'id':tagID, 'name':tagName, 'match':tagWeight})
    # dataObj = {'artists-num':len(artistlist)}
    return json.dumps(ret)


# launch
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
