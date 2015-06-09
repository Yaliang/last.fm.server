import pickle
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

filepath = "static/data/hetrec2011-lastfm-2k/"
f = open(filepath+"/tags.dat",'r')

TagManager={}
# read the first line 
line = f.readline()
# read the data of file
while line:
    line = f.readline()
    linedata = line.replace('\n','').split('\t')
    if len(linedata) > 1:
        tagID = linedata[0]
        tagWord = linedata[1]
        TagManager[tagID] = tagWord

f.close()

save(TagManager, 'tag-manager.pkr')