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

var API_BASE = "https://govhack.bgroberts.id.au/api";
var OPTIONS = {}

var nodes = null;
var edges = null;
var network = null;

function apiGet(reqType, reqID, callback) {
    var xmlhttp = new XMLHttpRequest();
    var url = API_BASE + "/" + reqType + "/" + reqID + ".json";
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
    nodes.add({id: reqID, label: nodeParsed['teaserTitle']});
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

function expandNode(params) {
    apiGet("adjacency", params['nodes'][0], addAdjacent);
}

function init() {
    var container = document.getElementById('network');
    nodes = new vis.DataSet();
    edges = new vis.DataSet();
    network = new vis.Network(container, {nodes: nodes, edges: edges}, OPTIONS);

    network.on("selectNode", expandNode);

    apiGet("content_of", "3692950", addNode);
}
