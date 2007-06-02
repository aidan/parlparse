
function rowof2(llab, llvalue)
{
    var eltd1 = document.createElement("td");
    eltd1.textContent = llab;

    var eltd2I = document.createElement("input");
    eltd2I.value = llvalue;
    eltd2I.readonly = true;

    var eltd2 = document.createElement("td");
    eltd2.appendChild(eltd2I);

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

}

var monthlist = new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");
function GetDocAttributesFromHeading(docattributes)
{
    var headsec = document.getElementById("pg000-bk00");
    var docid = null;
    var date = null;
    var time = null;
    for (var node = headsec.firstChild; node; node = node.nextSibling)
    {
        if (node.className == "code")
            docid = node.textContent;
        if (node.className == "date")
            date = node.textContent;
        if (node.className == "time")
            time = node.textContent;
    }
    if (!docid)
        alert("missing docid");

    docattributes["docid"] = docid;
    docattributes["date"] = date;
    docattributes["time"] = date;
    docattributes["longdate"] = parseInt(date.slice(8, 10)) + " " + monthlist[parseInt(date.slice(5, 7))] + " " + date.slice(0, 4);

    var mga = docid.match("A-([0-9]+)-PV\.([0-9]+)");
    if (mga)
    {
        docattributes["body"] = "General Assembly";
        docattributes["session"] = parseInt(mga[1]);
        docattributes["meeting"] = parseInt(mga[2]);
    }

    var msc = docid.match("S-PV-([0-9]+)");
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
    docattributes["pageno"] = parseInt(gid.match("pg([0-9]+)")[1]);
    docattributes["nhref"] = docattributes["basehref"] + "#" + gid;

    // find the div for this object
    while (gidme && (gidme.tagName.toLowerCase() != "div"))
        gidme = gidme.parentNode;

    if (!gidme)
    {
        alert("can't find div");
        return;
    }

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

    res += " |date=[[";
    res += parseInt(docattributes["date"].slice(8, 10)) + " ";
    res += monthlist[parseInt(docattributes["date"].slice(5, 7))];
    res += "]] [[";
    res += docattributes["date"].slice(0, 4);
    res += "]]";

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
    closebutt.textContent = "+";
    closebutt.className = "closebutt";
    closebutt.onclick = function(){ this.parentNode.className = "unclickedlink";  this.parentNode.textContent = "Link to this";  return true; };
    me.appendChild(closebutt);

    var eltable = document.createElement("table");
    eltable.appendChild(rowof2("date:", docattributes["longdate"]));
    eltable.appendChild(rowof2("URL:", blogurl(docattributes)));
    eltable.appendChild(rowof2("wiki:", wikival(docattributes)));
    eltable.className = "linktable";
    me.appendChild(eltable);

    addlinksonparas(divnode);
    me.className = "clickedlink";
    return true;
};


