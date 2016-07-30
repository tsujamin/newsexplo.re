/*
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
*/

var HTTP_BASE = "";
var API_BASE = "https://newsexplo.re/api";
var OPTIONS = {
    physics: {
	forceAtlas2Based: {
	    springLength: 500
	},
	solver: 'forceAtlas2Based'
    }
}
var DOMURL = window.URL || window.webkitURL || window;
var SVG_TEMPLATE = null;

var nodes = null;
var edges = null;
var network = null;

var nodeData = {};

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
    nodes.add({id: reqID, shape: 'image', image: nodeSVG(nodeParsed), size: 70});
    nodeData[reqID] = nodeParsed;
}

function addAdjacent(reqID, resp) {
    for (var idx = 0; idx < resp['adjacent_nodes'].length; idx++) {
	var nodeID = resp['adjacent_nodes'][idx]['id'];
	if (!nodes.get(nodeID))
	    apiGet("content/abc", nodeID, addNode);
	var existingEdges = edges.get({
	    filter: function(item) {
		return (item.from == reqID && item.to == nodeID ||
		       item.to == reqID && item.from == nodeID);
	    }});
	if (existingEdges.length == 0)
	    edges.add({from: reqID, to: nodeID});
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

    var nodeBody = '<h1 style="font-family: sans-serif; max-height: 100px;">' + title + '</h1>';
    if ('teaserTextPlain' in nodeParsed) {
	nodeBody += '<p style="font-family: sans-serif;">' + nodeParsed['teaserTextPlain'].substring(0, 50) + '...</p>';
    }

    var data = SVG_TEMPLATE;
    data = data.replace("$BODY_TEXT$", nodeBody);
    var svg = new Blob([data], {type: 'image/svg+xml;charset=utf-8'});
    var url = DOMURL.createObjectURL(svg);
    return url;
}

function expandNode(params) {
    nodeID = params['nodes'][0];
    apiGet("adjacency", nodeID, addAdjacent);

    node = nodes.get(nodeID);
    node.size = 150;
    nodes.update(node);

    pruneNodes(nodeID);
}

function shrinkNode(params) {
    nodeID = params['previousSelection']['nodes'][0];
    node = nodes.get(nodeID);
    node.size = 70;
    nodes.update(node);
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
    console.log(data);
    console.log(match);
    if (match != null) {
	nodes.clear();
	apiGet("content/abc", match[3], addNode);
    } else {
	$("#err_search").modal();
    }
    event.preventDefault();
}

function displayNodeInfo(event) {
    if (event['nodes'].length == 0)
	return;

    node = event['nodes'][0];

    $("#infobox_title").text(nodeData[node]['title']);
    $("#infobox").modal();
}

function init() {
    $("#welcomedialog").modal()
    $("#search_form").submit(handleSearchForm);
    var container = document.getElementById('network');
    nodes = new vis.DataSet();
    edges = new vis.DataSet();
    network = new vis.Network(container, {nodes: nodes, edges: edges}, OPTIONS);

    loadSVGTemplate();

    network.on("selectNode", expandNode);
    network.on("deselectNode", shrinkNode);
    network.on("doubleClick", displayNodeInfo);

    apiGet("content/abc", "3692950", addNode);
}
