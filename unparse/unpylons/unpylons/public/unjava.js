
// now depends on jQuery instead of bloated YAHOO.util.Dom

function initUNDemocracy()
{
    // put link to this everywhere
    $(".agendaitem").add(".subheading").add(".italicline").add(".recvote").add(".speech").each(function() 
    {  
        var linkhere = document.createElement('div');
        $(linkhere).addClass('unclickedlink');
        var linkheretext = document.createTextNode('Link to this');
        linkhere.appendChild(linkheretext);
        linkhere.onclick = function() { linkere(this); }
        this.insertBefore(linkhere, this.childNodes[0]);
    });
}

//YAHOO.util.Event.onDOMReady(initUNDemocracy);
$(document).ready(function() {
   initUNDemocracy(); 
 });


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
    rI.innerText = rI.textContent = llvalue; 
    return rI; 
}
function rowelahref(lhref, ltarg)
{
    var rI = document.createElement("a"); 
    rI.innerText = rI.textContent = ltarg; 
    rI.href = lhref; 
    return rI; 
}


function rowof2nontab(llab, llel)
{
    var eltd1 = document.createElement("span");
    $(eltd1).addClass("linktabfleft");
    eltd1.innerText = eltd1.textContent = llab;
    var eltd2 = document.createElement("span");
    $(eltd2).addClass("linktabfright");
    eltd2.appendChild(llel);
    var eltr = document.createElement("div");
    eltr.appendChild(eltd1);
    eltr.appendChild(eltd2);
    return eltr;
}

function rowof2(llab, llel)
{
return rowof2nontab(llab, llel); // simplification so that IE will work
    var eltd1 = document.createElement("td");
    eltd1.innerText = eltd1.textContent = llab;

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

function HrefImgReport(lhref)
{
    res = lhref.replace(/http:\/\/[^\/]*\//, "/imghrefrep/", lhref);
    res = res.replace(/#/, '__HASH__', res);
    if (res.search(/imghrefrep/))
        return res;
    return "";
}

var monthlist = new Array("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December");

function SetDocAttributePrez(docattributes, classname, vclassname, node)
{
    if ($(node).hasClass(classname))
    {
        if (node.innerText)
            docattributes[vclassname] = node.innerText;
        else if (node.textContent)
            docattributes[vclassname] = node.textContent;
    }
}


function GetDocAttributesFromHeading(docattributes)
{
    //alert("hii theree");
    
    $("#pg000-bk00").children().each(function() 
    {
        node = this; 
        SetDocAttributePrez(docattributes, "docid", "docid", node);
        SetDocAttributePrez(docattributes, "longdate", "longdate", node);
        SetDocAttributePrez(docattributes, "wikidate", "wikidate", node);
        SetDocAttributePrez(docattributes, "meetingtime", "meetingtime", node);
        SetDocAttributePrez(docattributes, "basehref", "bbasehref", node);
    })

    if (!docattributes["docid"])
        alert("missing docid");
    var mga = /A-([0-9]+)-PV\.([0-9]+)/.exec(docattributes["docid"]);
    var msc = /S-PV-([0-9]+.*)/.exec(docattributes["docid"]);
    
    // other types don't get in here
    //var mgares = /A-RES-([0-9]+)-(.+)/.exec(docattributes["docid"]);
    if (mga)
    {
        docattributes["body"] = "General Assembly";
        docattributes["session"] = parseInt(mga[1]);
        docattributes["meeting"] = parseInt(mga[2]);
        docattributes["type"] = "Verbatim Report";
    }

    else if (msc)
    {
        docattributes["body"] = "Security Council";
        docattributes["meeting"] = msc[1];
        docattributes["type"] = "Verbatim Report";
    }
    else
    {
        docattributes["type"] = "unrecognized docid";
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
    if (gidme.className == "speech")
    {
        var citetag = null;
        for (citetag = gidme.firstChild; citetag; citetag = citetag.nextSibling)
        {
            if (citetag.tagName && (citetag.tagName.toLowerCase() == "cite"))
                break;
        }
        if (citetag)
        $(citetag).children().each(function() 
        //for (var node = getFirstChild(citetag); node; node = getNextSibling(node))
        {
            node = this; 
            SetDocAttributePrez(docattributes, "name", "speakername", node);
            SetDocAttributePrez(docattributes, "nation", "speakernation", node);
            SetDocAttributePrez(docattributes, "language", "speakerlanguage", node);
        }); 
        if (docattributes["speakernation"])
            docattributes["speakernation"] = docattributes["speakernation"].replace(/[()]/g, "");
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
    res += "on " + docattributes["longdate"] + " ";
    res += "in the " + docattributes["body"];
    res += "</a>";
    return res;
}


function wikival(docattributes)
{
    var res = "<ref>{{ UN document";
    res += " |docid=" + docattributes["docid"];
    res += " |body=" + docattributes["body"];
    if (docattributes["type"])
        res += " |type=" + docattributes["type"];
    if (docattributes["resolution_number"])
        res += " |resolution_number=" + docattributes["resolution_number"];
    if (docattributes["session"])
        res += " |session=" + docattributes["session"];
    if (docattributes["meeting"])
        res += " |meeting=" + docattributes["meeting"];
    if (docattributes["pageno"])
        res += " |page=" + docattributes["pageno"];
    if (docattributes["gid"])
        res += " |anchor=" + docattributes["gid"];

    if (docattributes["wikidate"])
        res += " |date=" + docattributes["wikidate"];

    if (docattributes["meetingtime"])
        res += " |meetingtime=" + docattributes["meetingtime"];

    if (docattributes["speakername"])
        res += " |speakername=" + docattributes["speakername"];
    if (docattributes["speakernation"])
        res += " | speakernation=" + docattributes["speakernation"]; 

    
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
                $(nnlink).addClass("unclickedlink");
                nnlink.innerText = nnlink.textContent = "Link to this";
                nnlink.onclick = function(){ return linkere(this); };
                node.insertBefore(nnlink, node.firstChild);
            }
        }
    }
}


function closebuttclick(me)
{
// overwriting the div seems to allow for infinite loops or for the onclick button not to take hold
    //var replaceClass = YAHOO.util.Dom.replaceClass;
    //    replaceClass(me, "clickedlink", "unclickedlink");  
    //    me.onclick = function(){ alert("jijij"); return linkere(this); };
    //    me.innerText = me.textContent = "Link to this";  
    var nnlink = document.createElement("div");
    $(nnlink).addClass("unclickedlink");
    nnlink.innerText = nnlink.textContent = "Link to this";
    nnlink.onclick = function(){ return linkere(this); };
    me.parentNode.insertBefore(nnlink, me);
    me.parentNode.removeChild(me); 
    return true; 
};

function linkere(me)
{
    // avoid coming in here if already open
    if ($(me).hasClass("clickedlink"))
        return true;
    me.onclick = function(){ return true; } // the above stopped working 

    var docattributes = new Array();

    // detect the base doc
    GetDocAttributesBaseHref(docattributes);
    GetDocAttributesFromHeading(docattributes);
    divnode = GetDocAttributesFromBlock(docattributes, me);

    location.href = docattributes["nhref"];  // set url to current position

    me.innerText = me.textContent = "";

    var closebutt = document.createElement("div");
    closebutt.innerText = closebutt.textContent = "x";
    $(closebutt).addClass("closebutt");
    closebutt.onclick = function(){ return closebuttclick(this.parentNode); };
    me.appendChild(closebutt);

    var eltable = document.createElement("div");// should be table
    eltable.appendChild(rowof2("date:", rowelspan(docattributes["longdate"])));
    lhref = "/document/" + docattributes["docid"] + "/page_" + docattributes["pageno"]; 
    ltarg = docattributes["docid"] + " page " + docattributes["pageno"];
    eltable.appendChild(rowof2("pdf:", rowelahref(lhref, ltarg)));
    eltable.appendChild(rowof2("URL:", rowelinput(blogurl(docattributes))));
    eltable.appendChild(rowof2("wiki:", rowelinput(wikival(docattributes))));
    $(eltable).addClass("linktable");
    me.appendChild(eltable);

    if (docattributes["blockclass"] == "speech")
        addlinksonparas(divnode);
    $(me).removeClass("unclickedlink").addClass("clickedlink");

    document.getElementById("hrefimg").src = HrefImgReport(location.href);  // this doesn't appear effective
    //document.getElementById("hrefimgi").value = HrefImgReport(location.href);
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

