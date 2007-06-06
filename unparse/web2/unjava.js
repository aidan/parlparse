
function rowelinput(llvalue)
{
    var rI = document.createElement("input"); 
    rI.value = llvalue; 
    rI.readOnly = true; 
    return rI; 
}
function rowelspan(llvalue)
{
    var rI = document.createElement("span"); 
    rI.textContent = llvalue; 
    return rI; 
}
function rowelahref(lhref, ltarg)
{
    var rI = document.createElement("a"); 
    rI.textContent = ltarg; 
    rI.href = lhref; 
    return rI; 
}


function rowof2(llab, llel)
{
    var eltd1 = document.createElement("td");
    eltd1.textContent = llab;

    var eltd2 = document.createElement("td");
    eltd2.appendChild(llel);

    var eltr = document.createElement("tr");
    eltr.appendChild(eltd1);
    eltr.appendChild(eltd2);
    return eltr;
}

function GetDocAttributesBaseHref(docattributes)
{
    docattributes["href"] = location.href;
    var basehref = location.href;
    var ih = basehref.lastIndexOf("#");
    if (ih != -1)
        basehref = basehref.slice(0, ih);
    docattributes["basehref"] = basehref;
    docattributes["nhref"] = basehref;
    var ibh = basehref.indexOf("?"); 
    docattributes["bbasehref"] = (ibh != -1 ? basehref.slice(0, ibh) : basehref); 
}

var monthlist = new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");
function GetDocAttributesFromHeading(docattributes)
{
    var headsec = document.getElementById("pg000-bk00");
    for (var node = headsec.firstChild; node; node = node.nextSibling)
    {
        if (node.className == "docid")
            docattributes["docid"] = node.textContent;
        if (node.className == "date")
            docattributes["date"] = node.textContent;
        if (node.className == "longdate")
            docattributes["longdate"] = node.textContent;
        if (node.className == "wikidate")
            docattributes["wikidate"] = node.textContent;
        if (node.className == "time")
            docattributes["meetingtime"] = node.textContent;
    }
    if (!docattributes["docid"])
        alert("missing docid");
    var mga = /A-([0-9]+)-PV\.([0-9]+)/.exec(docattributes["docid"]);
    if (mga)
    {
        docattributes["body"] = "General Assembly";
        docattributes["session"] = parseInt(mga[1]);
        docattributes["meeting"] = parseInt(mga[2]);
    }

    var msc = /S-PV-([0-9]+)/.exec(docattributes["docid"]);
    if (msc)
    {
        docattributes["body"] = "Security Council";
        docattributes["meeting"] = parseInt(msc[1]);
    }
}

function GetDocAttributesFromBlock(docattributes, me)
{
    // find the id of this object
    var gidme = me;
    while (gidme && !gidme.id)
        gidme = gidme.parentNode;
    if (!gidme)
    {
        alert("can't find gid");
        return;
    }
    gid = gidme.id;
    docattributes["gid"] = gid;
    docattributes["pageno"] = parseInt(/pg0*([0-9]+)/.exec(gid)[1]);
    docattributes["nhref"] = docattributes["basehref"] + "#" + gid;

    // find the div for this object
    while (gidme && (gidme.tagName.toLowerCase() != "div"))
        gidme = gidme.parentNode;

    if (!gidme)
    {
        alert("can't find div");
        return;
    }

    docattributes["blockclass"] = gidme.className; 
    if (gidme.className == "spoken")
    {
        var h3speaker = null;
        for (h3speaker = gidme.firstChild; h3speaker; h3speaker = h3speaker.nextSibling)
        {
            if (h3speaker.className == "speaker")
                break;
        }
        for (var node = h3speaker.firstChild; node; node = node.nextSibling)
        {
            if (node.className == "name")
                docattributes["speakername"] = node.textContent;
            if (node.className == "nation")
                docattributes["speakernation"] = node.textContent;
            if (node.className == "language")
                docattributes["speakerlanguage"] = node.textContent;
        }
    }

    return gidme;
}

function blogurl(docattributes)
{
    var res = "<a href=\"" + docattributes["nhref"] + "\">";
    if (docattributes["speakername"])
        res += "said by " + docattributes["speakername"] + " ";
    if (docattributes["speakernation"])
        res += "of " + docattributes["speakernation"] + " ";
    res += "on " + docattributes["date"] + " ";
    res += "in the " + docattributes["body"];
    res += "</a>";
    return res;
}


function wikival(docattributes)
{
    var wpvalue = "{{ UN document |code=" + docattributes["docid"] + "|body=A | type=PV| page=" + docattributes["pageno"] + "}}";

    var res = "<ref>{{ UN document";
    res += " |code=" + docattributes["docid"];
    res += " |body=" + docattributes["body"];
    if (docattributes["session"])
        res += " |session=" + docattributes["session"];
    res += " |meeting=" + docattributes["meeting"];
    res += " |page=" + docattributes["pageno"];
    res += " |anchor=" + docattributes["gid"];

    res += " |date=";
    res += docattributes["wikidate"]

    res += " |time=" + docattributes["time"];

    tday = new Date();
    res += " |accessdate=";
    res += tday.getFullYear();
    res += "-";
    if (tday.getMonth() < 9)
        res += "0";
    res += (tday.getMonth() + 1);
    res += "-";
    if (tday.getDate() <= 9)
        res += "0";
    res += tday.getDate();

    res += " }}</ref>";
    return res;


}

function addlinksonparas(divnode)
{
    for (var node = divnode.firstChild; node; node = node.nextSibling)
    {
        if (node.tagName && ((node.tagName.toLowerCase() == "p") || (node.tagName.toLowerCase() == "blockquote")))
        {
            if (node.firstChild && (!node.firstChild.tagName || (node.firstChild.tagName.toLowerCase() != "div")))
            {
                //<div onclick="linkere(this);" class="unclickedlink">link to this</div>
                var nnlink = document.createElement("div");
                nnlink.className = "unclickedlink";
                nnlink.textContent = "link to this";
                nnlink.onclick = function(){ return linkere(this); };
                node.insertBefore(nnlink, node.firstChild);
            }
        }
    }
}

function linkere(me)
{
    if (me.className == "clickedlink")
        return true;

    var docattributes = new Array();

    // detect the base doc
    GetDocAttributesBaseHref(docattributes);
    GetDocAttributesFromHeading(docattributes);
    divnode = GetDocAttributesFromBlock(docattributes, me);

    location.href = docattributes["nhref"];  // set url to current position

    me.textContent = "";

    var closebutt = document.createElement("div");
    closebutt.textContent = "x";
    closebutt.className = "closebutt";
    closebutt.onclick = function(){ this.parentNode.className = "unclickedlink";  this.parentNode.textContent = "Link to this";  return true; };
    me.appendChild(closebutt);

    var eltable = document.createElement("table");
    eltable.appendChild(rowof2("date:", rowelspan(docattributes["longdate"])));
    lhref = docattributes["bbasehref"] + "?code=" + docattributes["docid"] + "&pdfpage=" + docattributes["pageno"]; 
    ltarg = docattributes["docid"] + " page " + docattributes["pageno"];
    eltable.appendChild(rowof2("pdf:", rowelahref(lhref, ltarg)));
    eltable.appendChild(rowof2("URL:", rowelinput(blogurl(docattributes))));
    eltable.appendChild(rowof2("wiki:", rowelinput(wikival(docattributes))));
    eltable.className = "linktable";
    me.appendChild(eltable);

    if (docattributes["blockclass"] == "spoken")
        addlinksonparas(divnode);
    me.className = "clickedlink";
    return true;
};




function chvotekey(me)
{
    var currvcn = me.className;
    if (currvcn.slice(currvcn.length - 2) == "ul")
        var nextvcn = currvcn.slice(0, currvcn.length - 2);
    else
        var nextvcn = currvcn + "ul";
    me.className = nextvcn;

    var vlist = me.parentNode;
    while (vlist && (vlist.className != "votekey"))
        vlist = vlist.parentNode;
    if (!vlist)
        alert("could not find votekey");
    
    while (vlist && (vlist.className != "votelist"))
        vlist = vlist.nextSibling;
    if (!vlist)
        alert("count not find votelist");

    for (var vt = vlist.firstChild; vt; vt = vt.nextSibling)
    {
        if (vt.className == nextvcn)
            vt.className = currvcn;
    }
    
        
}

