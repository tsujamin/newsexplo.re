LICENCE = `
  Copyright © 2016 Benjamin Roberts, Andrew Donnellan

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published
  by the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.
`;

/*
  If you're reading this code, don't.

  Just... don't. You'll regret everything.
*/

var HTTP_BASE = "";
var API_BASE = "https://newsexplo.re/api";
var OPTIONS = {
  physics: {
    repulsion: {
      springLength: 500,
      nodeDistance: 300
    },
    solver: 'repulsion',
  }
}

console.log(OPTIONS)
var DOMURL = window.URL || window.webkitURL || window;
var SVG_TEMPLATE = null;

var COLOURS = {
    'Article': '#f6ffd5',
    'location': '#00ff00',
    'subject': '#99ebff',
    'watsonsubject': '#99ebff',
};
var DEFAULT_COLOUR = '#f6ffd5';

var nodes = null;
var edges = null;
var network = null;

var nodeData = {};
var nodeImageContent = {};

function loadSVGTemplate() {
    var xmlhttp = new XMLHttpRequest();
    var url = HTTP_BASE + "box_html.svg";
    xmlhttp.onreadystatechange = function() {
	if (xmlhttp.readyState == 4 && xmlhttp.responseText != null) {
	    SVG_TEMPLATE = xmlhttp.responseText;
	}
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

function apiGet(reqType, reqID, callback) {
    var xmlhttp = new XMLHttpRequest();
    var url = API_BASE + "/" + reqType + "/" + reqID;
    xmlhttp.onreadystatechange = function() {
	if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var respParsed = JSON.parse(xmlhttp.responseText);
            callback(reqID, respParsed);
	}
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

function addNode(reqID, nodeParsed) {
    if (nodeParsed['docType'] == 'Image' || nodeParsed['docType'] == 'ImageProxy')
	return;
    nodes.add({id: reqID, shape: 'image', image: nodeSVG(nodeParsed), size: 70});
    nodeData[reqID] = nodeParsed;
    apiGet('adjacency', reqID, getAdjacentImages);
}

function addAdjacent(reqID, resp) {
    for (var idx = 0; idx < resp['adjacent_nodes'].length; idx++) {
	var nodeID = resp['adjacent_nodes'][idx]['id'];
	if (!nodes.get(nodeID))
	    apiGet("content/abc", nodeID, function(nodeID, resp) {
		addNode(nodeID, resp);
		if (network.getSelectedNodes()[0] == reqID) {
		    // Refresh infobox
		    displayNodeInfo(reqID);
		}
	    });
	var existingEdges = edges.get({
	    filter: function(item) {
		return (item.from == reqID && item.to == nodeID ||
		       item.to == reqID && item.from == nodeID);
	    }});
	if (existingEdges.length == 0)
	    edges.add({from: reqID, to: nodeID});
    }
}

function ABCImageGet(reqID, callback) {
    var image = new Image();
    image.onload = function () {
	var canvas = document.createElement('canvas');
	canvas.width = this.naturalWidth;
	canvas.height = this.naturalHeight;
	canvas.getContext('2d').drawImage(this, 0, 0);
	callback(reqID, canvas.toDataURL('image/png'));
    };
    image.crossOrigin = "Anonymous";
    image.src = API_BASE + "/content/abc/imageproxy/" + reqID;
}

function setNewImage(nodeID, content) {
    var node = nodes.get(nodeID);
    nodeImageContent[nodeID] = content;
    node.image = nodeSVG(nodeData[nodeID]);
    nodes.update(node);
}

function getAdjacentImages(reqID, resp) {
    for (var idx = 0; idx < resp['adjacent_nodes'].length; idx++) {
	var nodeID = resp['adjacent_nodes'][idx]['id'];
	if (!nodes.get(nodeID)) {
	    apiGet("content/abc", nodeID, function(newNodeID, resp) {
		if (resp['docType'] == 'Image' || resp['docType'] == 'ImageProxy') {
		    ABCImageGet(newNodeID, function (newNodeID, resp) {
			setNewImage(reqID, resp);
		    });
		}
	    });
	} else {
	    if (nodeData[nodeID]['docType'] == 'Image' || nodeData[nodeID]['docType'] == 'ImageProxy') {
		ABCImageGet(nodeID, function (newNodeID, resp) {
		    setNewImage(reqID, resp);
		});
	    }
	}
    }
}

function nodeSVG(nodeParsed) {
    if (SVG_TEMPLATE == null) {
	setTimeout(function() {
	    nodeSVG(nodeParsed);
	}, 100);
	return;
    }

    var title = nodeParsed['title'].length > 30 ? nodeParsed['title'].substring(0, 27) + '...' : nodeParsed['title'];
    var nodeBody = '';
    if (nodeImageContent[nodeParsed['id']]) {
	nodeBody += '<img src="' + nodeImageContent[nodeParsed['id']] + '" style="width: 230px; height: 200px;" />';
    }
    nodeBody += '<h1 style="font-family: sans-serif; max-height: 100px;">' + title + '</h1>';
    if ('teaserTextPlain' in nodeParsed) {
	nodeBody += '<p style="font-family: sans-serif;">' + nodeParsed['teaserTextPlain'].substring(0, 50) + '...</p>';
    }
    var data = SVG_TEMPLATE;
    data = data.replace("$BODY_TEXT$", nodeBody);
    if (COLOURS[nodeParsed['docType']] != null) {
	data = data.replace("$FILL_COLOUR$", COLOURS[nodeParsed['docType']]);
    } else {
	data = data.replace("$FILL_COLOUR$", DEFAULT_COLOUR);
    }
    var svg = new Blob([data], {type: 'image/svg+xml;charset=utf-8'});
    var url = DOMURL.createObjectURL(svg);
    return url;
}

function selectNode(nodeID) {
    expandNode({nodes: [nodeID]});
}

function expandNode(params) {
    nodeID = params['nodes'][0];
    // make sure we're the only ones selected
    network.unselectAll();
    network.selectNodes([nodeID]);

    pruneNodes(nodeID);
    nodes.forEach(function(item) {
	item.size = 70;
	nodes.update(item);
    });

    apiGet("adjacency", nodeID, addAdjacent);
    node = nodes.get(nodeID);
    node.size = 150;
    nodes.update(node);

    displayNodeInfo(nodeID);
}

function shrinkNode(params) {
    nodeID = params['previousSelection']['nodes'][0];
    node = nodes.get(nodeID);
    node.size = 70;
    nodes.update(node);

    if (params['nodes'].length == 0)
	$('#infobox').hide(300);
}

// This is buggy as heck. Oh well.
function pruneNodes(selectedNode) {
    var current = selectedNode.toString();
    var distances = {};
    var visited = [current];
    var connected;
    distances[current] = 0;
    while (true) {
	connected = network.getConnectedNodes(current);
	for (var idx = 0; idx < connected.length; idx++) {
	    if (!(connected[idx] in distances) || (distances[current] + 1 < distances[connected[idx]])) {
		distances[connected[idx]] = distances[current] + 1;
	    }
	}
	visited.push(current);
	var new_current;
	var new_current_distance = 0;
	nodes.forEach(function(item) {
	    if (visited.indexOf(item.id) != -1) return;
	    if (!(item.id in distances)) return;
	    if (distances[item.id] < new_current_distance || new_current_distance == 0) {
		new_current_distance = distances[item.id];
		new_current = item.id;
	    }
	});
	if (new_current_distance == 0) break;
	current = new_current;
    }

    nodes.forEach(function(item) {
	if (distances[item.id] > 2 || !(item.id in distances))
	    nodes.remove(item.id);
    });
}

function handleSearchForm(event) {
    var data = $('#srch-term')[0].value;
    var regex = /(http:\/\/)?(www.)?abc.net.au\/news\/.*\/([0-9]+)/;
    var match = regex.exec(data);
    if (match != null) {
	nodes.clear();
	apiGet("content/abc", match[3], function(nodeID, resp) {
	    addNode(nodeID, resp);
	    selectNode(nodeID);
	});
    } else {
	$("#err_search").modal();
    }
    event.preventDefault();
}

function displayNodeInfo(nodeID) {
    var node = nodeData[nodeID];

    // Clear stuff
    $('#infobox_related').html('');

    if (node['canonicalUrl']) {
	$("#infobox_title").html('<a href="' + node['canonicalUrl'] + '" target="_blank">' + node['title'] + '<span class="glyphicon glyphicon-new-window" aria-hidden="true"></span></a>');
    } else {
	$("#infobox_title").text(node['title']);
    }
    if (node['docType'] == 'Article') {
	$('#infobox_desc').html(node['text']);
	$('#infobox_title').append(' (ABC)');
    } else if (node['docType'] == 'location') {
	$('#infobox_title').append(' (ABC, Location)');
	$('#infobox_desc').html('');
    } else if (node['docType'] == 'subject') {
	$('#infobox_title').append(' (ABC, Subject)');
	$('#infobox_desc').html('');
    } else if (node['docType'] == 'watsonsubject') {
	$('#infobox_title').append(' (Watson, Subject/Person)');
	$('#infobox_desc').html('');
    } else {
	$('#infobox_desc').html('');
    }

    if (nodeImageContent[nodeID]) {
	$('#infobox_img').attr('src', nodeImageContent[nodeID]);
	$('#infobox_img').show();
    } else {
	$('#infobox_img').hide();
    }

    related = network.getConnectedNodes(nodeID);
    for (var idx = 0; idx < related.length; idx++) {
	$("#infobox_related").append('<li><a href="#" onclick="selectNode(' + related[idx] + ')">' + nodeData[related[idx]]['title'] + '</a></li>')
    }

    if (node['docType'] == 'Article') {
	loadTroveFromABC(nodeID);
    }

    $("#infobox").show(300);
}

function loadTroveFromABC(nodeID) {
    console.log("Retrieving trove for node " + nodeID);
    apiGet("content/trove/from_abc", nodeID, function(nodeID, resp) {
	// stop if node no longer selected
	if (network.getSelectedNodes()[0] != nodeID) {
	    console.log("Aborting Trove routine - node ID " + nodeID + " no longer selected");
	    return;
	}
	// stop if we've already done this node - HACK
	if ($("#infobox_related").html().indexOf("<strong>(Trove)") != -1)
	    return;

	for (var idx = 0; idx < resp['related'].length, idx <= 2; idx++) {
	    var item = resp['related'][idx];
	    $("#infobox_related").append('<li><a href="' + item['url'] + '" target="_blank">' + item['title'] + '<span class="glyphicon glyphicon-new-window" aria-hidden="true"></span></a> <strong>(Trove)</strong></li>');
	}
    });
}

function loadABCJustInLatest() {
    apiGet("content/abc/just_in", "", function(nodeID, content) {
	apiGet("content/abc", content[0]['id'], function(nodeID, resp) {
	    addNode(nodeID, resp);
	    selectNode(nodeID);
	});
    });
}

function init() {
    console.log(">>> N E W S E X P L O . R E   V E R S I O N   0 . 0 1   I N I T I A L I S I N G <<<");
    console.log(LICENCE);
    console.log("*** RETICULATING SPLINES... ***");
    console.log("(why are you reading this? go away! don't look at our terrible JavaScript!)");
    $("#welcomedialog").modal()
    $("#search_form").submit(handleSearchForm);
    var container = document.getElementById('network');
    nodes = new vis.DataSet();
    edges = new vis.DataSet();
    network = new vis.Network(container, {nodes: nodes, edges: edges}, OPTIONS);

    loadSVGTemplate();

    network.on("selectNode", expandNode);
    network.on("deselectNode", shrinkNode);

    loadABCJustInLatest();
    console.log("*** SPLINES RETICULATED, WE'RE READY TO ROLL! ***");
}
