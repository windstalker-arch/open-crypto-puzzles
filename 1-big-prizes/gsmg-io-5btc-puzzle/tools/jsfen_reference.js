// Extracted verbatim from Chess-Cypher/src/App.js hashFunction + getFENString.
function getFENString(base64Object) {
    var keys = Object.keys(base64Object);
    var square = 0, fenString = "", dots = 0;
    var noSoldier = "rRnNbBqQkK";
    var all = "rRnNbBqQkKpP";
    for (var i = 0; i < keys.length; i++) {
        var currKey = keys[i]; var piece;
        if (base64Object[currKey]) {
            var sum = base64Object[currKey];
            if (square < 8 || square > 55) {
                piece = dots ? dots.toString() + noSoldier[sum % noSoldier.length] : noSoldier[sum % noSoldier.length];
            } else {
                piece = dots ? dots.toString() + all[sum % all.length] : all[sum % all.length];
            }
            dots = 0;
        } else { dots += 1; piece = ""; }
        if (square != 0 && (square + 1) % 8 == 0) {
            if (dots) { fenString += dots.toString() + "/"; dots = 0; }
            else { fenString += piece + "/"; }
        } else { fenString += piece; }
        square += 1;
    }
    return fenString.slice(0, fenString.length - 1);
}
function hashFunction(text) {
    var buff = new Buffer(text);
    var base64 = buff.toString("base64");
    var base64Object = {A:0,B:0,C:0,D:0,E:0,F:0,G:0,H:0,I:0,J:0,K:0,L:0,M:0,N:0,O:0,P:0,Q:0,R:0,S:0,T:0,U:0,V:0,W:0,X:0,Y:0,Z:0,a:0,b:0,c:0,d:0,e:0,f:0,g:0,h:0,i:0,j:0,k:0,l:0,m:0,n:0,o:0,p:0,q:0,r:0,s:0,t:0,u:0,v:0,w:0,x:0,y:0,z:0,0:0,1:0,2:0,3:0,4:0,5:0,6:0,7:0,8:0,9:0,"+":0,"/":0};
    for (var i = 0; i < base64.length; i++) {
        var currLetter = base64[i];
        if (currLetter != "=") { base64Object[currLetter] += i + 1; }
    }
    return getFENString(base64Object);
}
const tests = ["A","AB","ABC","matrixsumlist","enter","Hello, World!","shabef","0","a","z","aaaaaaaaaaaaaaaaaaaaaaaaaa","The quick brown fox jumps over the lazy dog"];
tests.forEach(t => console.log(JSON.stringify(t) + "\t" + hashFunction(t)));
