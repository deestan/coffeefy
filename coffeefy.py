import re
import subprocess
import hashlib

def spacefudge(depth=10):
    if depth==0:
        yield b''
        yield b'\n'
        return
    for f in spacefudge(depth-1):
        yield b'\t'+f
        yield b' '+f

def timefudge(origTime):
    roof = 0
    while True:
        for i in range(roof+1):
            author = origTime+i
            committer = origTime+roof
            for mess in spacefudge():
                yield (author, committer, mess)
        roof += 1

def isCoffeeCommit(c):
    h = hashlib.sha1(b'commit %d\0'%len(c))
    h.update(c)
    return h.digest()[:3] == b'\xc0\xff\xee'
        
def getCommit():
    c = subprocess.check_output("git cat-file -p HEAD").decode('utf8')
    startTimeA = re.compile('author.* (\d+) \+').findall(c)[0]
    startTimeC = re.compile('committer.* (\d+) \+').findall(c)[0]
    splitAuthor = c.find("author")
    ca1 = c[:splitAuthor]
    ca2 = c[splitAuthor:]
    ca2 = ca2.replace(startTimeA + ' +', '%d +', 1)
    c = ca1 + ca2
    splitCommitter = c.find("committer")
    cc1 = c[:splitCommitter]
    cc2 = c[splitCommitter:]
    cc2 = cc2.replace(startTimeC + ' +', '%d +', 1)
    newC = cc1 + cc2
    return (int(startTimeA), newC.encode('utf8'))

def getCoffee(startTime, ct):
    for (x,y,z) in timefudge(startTime):
        c = (ct%(x,y)) + z
        if isCoffeeCommit(c):
            return c

def addCommit(commit):
    res = subprocess.check_output("git hash-object -w -t commit --stdin", input=commit)
    return res
    
def updateBranch(newHash):
    b = open(".git/HEAD").read()[5:][:-1]
    open(".git/"+b,"wb").write(newHash)

startTime, commitTemplate = getCommit()
coffeeCommit = getCoffee(startTime, commitTemplate)
cHash = addCommit(coffeeCommit)
updateBranch(cHash)
