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

var API_BASE = "https://govhack.bgroberts.id.au/mock_api";
var OPTIONS = {}

var nodes = null;
var edges = null;
var network = null;

function getNode(nodeType, nodeID, nodeDest) {
    var xmlhttp = new XMLHttpRequest();
    var url = API_BASE + "/" + nodeType + "/" + nodeID + ".json";
    xmlhttp.onreadystatechange = function() {
	if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            var nodeParsed = JSON.parse(xmlhttp.responseText);
            addNode(nodeDest, nodeParsed);
	}
    };
    xmlhttp.open("GET", url, true);
    xmlhttp.send();
}

function addNode(nodeDest, nodeParsed) {
    nodes.add({label: nodeParsed['teaserTitle']});
}

function init() {
    var container = document.getElementById('network');
    nodes = new vis.DataSet();
    edges = new vis.DataSet();
    network = new vis.Network(container, {nodes: nodes, edges: edges}, OPTIONS);

    getNode("content_of", "3692950", null);
}
