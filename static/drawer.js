var tree = await fetch("./tree.json")
  .then((res) => res.json());


// import tree from './tree.json';
var elem = document.getElementById('draw-shapes');
var two = new Two({
  width: 400,
  height: 400,
}).appendTo(elem);



function scale(coordinates, zoomed_id) {
  var s = 0.1;
  var zoom_point = tree[zoomed_id];
  return [s * (coordinates[0] - zoom_point["x"] + 2000), s * (coordinates[1] - zoom_point["y"] + 2000)];
}

function scale_val(v) {
  var s = 0.1;
  return v * s;
}

function draw_passive(passive_node, zoomed_id, active_nodes, important_nodes) {
  var size;
  var filling;
  var stroke;
  var scaled_coordinates = scale([passive_node["x"], passive_node["y"]], zoomed_id);
  if (passive_node["type"] == "keystone") {
    size = 70;
  } else if (passive_node["type"] == "notable") {
    size = 40;
  } else if (passive_node["type"] == "jewel_socket") {
    size = 80;
  } else {
    size = 20;
  }

  if (important_nodes.includes(passive_node["skill"])) {
    filling = "red";
    stroke = "red"
    size = size * 1.5;
  } else if (active_nodes.includes(passive_node["skill"])) {
    filling = "orange";
    stroke = "orange";
  } else {
    filling = "gray"
    stroke = "gray"
  }
  if (passive_node["type"] == "jewel_socket") {
    var shape = two.makeRectangle(
      scaled_coordinates[0],
      scaled_coordinates[1],
      scale_val(size),
      scale_val(size)
    )
  } else {
    var shape = two.makeCircle(scaled_coordinates[0], scaled_coordinates[1], scale_val(size));
  }

  shape.fill = filling;
  shape.stroke = stroke;
  shape.linewidth = 1;
}

function draw_connection(passive_node, tree, zoomed_id, active_nodes) {
  for (const neighbour_id of passive_node["in"]) {
    if (!(neighbour_id in tree)) {
      continue;
    }
    var neighbour = tree[neighbour_id];
    if (neighbour["cantBeConnectedTo"] == true) {
      continue
    }
   if (active_nodes.includes(passive_node["skill"]) && active_nodes.includes(neighbour["skill"])) {
      var stroke = "orange";
      var width = 2;
    } else {
      var stroke = "gray"
      var width = 1
    }
    if ((passive_node["group"] == neighbour["group"]) && (passive_node["orbit"] == neighbour["orbit"])) {
      draw_circular_connection(passive_node, neighbour, width, stroke, zoomed_id);
    } else {

      draw_linear_connection(passive_node, neighbour, width, stroke, zoomed_id);
    }
  }
}


function draw_linear_connection(passive_node, neighbour, width, stroke, zoomed_id) {
  var scaled_coordinates = scale([passive_node["x"], passive_node["y"]], zoomed_id);
  var scaled_neighbour = scale([neighbour["x"], neighbour["y"]], zoomed_id);

  var line = two.makeLine(
    scaled_coordinates[0],
    scaled_coordinates[1],
    scaled_neighbour[0],
    scaled_neighbour[1]
  )
  line.stroke = stroke;
  line.linewidth = width;
}

function draw_circular_connection(passive_node, neighbour, width, stroke, zoomed_id) {
  var scaled_coordinates = scale([passive_node["cx"], passive_node["cy"]], zoomed_id);

  var o = passive_node["angle"]
  var l = neighbour["angle"]
  var h = o < l;
  o = h ? passive_node["angle"] : neighbour["angle"];
  var c = (l = h ? neighbour["angle"] : passive_node["angle"]) - o;
  if (c > Math.PI) {
    l = (o = l) + (2 * Math.PI - c);
  }

  var arc = two.makeArcSegment(
    scaled_coordinates[0],
    scaled_coordinates[1],
    scale_val(passive_node["orbit_radius"]),
    scale_val(passive_node["orbit_radius"]),
    o,
    l,
    20
  );
  arc.stroke = stroke;
  arc.linewidth = width;

}

function draw_timeless_radius(jewel_id) {
  var jewel = tree[jewel_id];
  var scaled_coordinates = scale([jewel["x"], jewel["y"]], jewel_id);

  var shape = two.makeCircle(scaled_coordinates[0], scaled_coordinates[1], scale_val(1800));

  shape.fill = "#ebedf2";
  shape.stroke = null;
  shape.linewidth = 1;
}

function draw_keystone_radius(keystone_id, jewel_id) {
  var keystone = tree[keystone_id];
  var scaled_coordinates = scale([keystone["x"], keystone["y"]], jewel_id);

  var shape = two.makeCircle(scaled_coordinates[0], scaled_coordinates[1], scale_val(960));

  shape.stroke = "black";
  shape.fill = "#d9feff";

  shape.linewidth = 1;
}


function inradius(middle, node, radius) {
  return (middle["x"] - node["x"]) ** 2 + (middle["y"] - node["y"]) ** 2 < radius ** 2
}

function draw_all(jewel_id, keystone_id, active_nodes, important_nodes) {
  var shape = two.makeRectangle(200, 200, 400, 400);
  shape.fill = "black";
  draw_timeless_radius(jewel_id); 
  if (keystone_id != null){
    draw_keystone_radius(keystone_id, jewel_id);
  }

  for (const [node_id, node] of Object.entries(tree)) {
    if (inradius(tree[jewel_id], node, 3500)) {
      draw_connection(node, tree, jewel_id, active_nodes);
    }
  }
  for (const [node_id, node] of Object.entries(tree)) {
    if (inradius(tree[jewel_id], node, 3500)) {
      draw_passive(node, jewel_id, active_nodes, important_nodes);
    }
  }
  two.update();
}

async function buildTree(e, id) {
  const data = await fetch("/", {
    method: "POST",
    body: JSON.stringify({
      "id": id
    }),
    headers: {
      "Content-type": "application/json; charset=UTF-8"
    }
  })
  .then(resp => resp.json());
  draw_all(data.jewel_id, data.keystone_id, data.active_nodes, data.important_nodes);
  
  var div = document.getElementById("draw-shapes");
  div.style.left = e.clientX + "px";
  div.style.top = Math.min(e.clientY, window.innerHeight - 400) + "px";
  $("#draw-shapes").toggle();
  $("#draw-shapes").attr("toggled", true)
}



function buildTimelessJewelTradeString(jewel_type, seed) {
  var variants = {
    "0": ["asenath", "balbala", "nasima"],
    "1": ["xibaqua", "doryani", "ahuana"],
    "2": ["cadiro", "caspiro", "victario"]
  }

  var query = {
    "query": {
      "status": { "option": "online" },
      "stats": [
        {
          "type": "count",
          "filters": variants[jewel_type].map(function (variant) {
            return { "value": { "min": seed, "max": seed }, "id": "explicit.pseudo_timeless_jewel_" + variant };
          }),
          "value": { "min": 1 }
        }]
    },
    "sort": { "price": "asc" }
  }
  window.open("https://www.pathofexile.com/trade/search/?q=" + encodeURIComponent(JSON.stringify(query)), '_blank');
}

function buildImpossibleEscapeTradeString(ie) {
  var query = {
    "query": {
      "status": { "option": "online" },
      "stats": [
        {
          "type": "count",
          "filters": [
            {"id": "explicit.stat_2422708892", "value": {"option": ie}}
          ],
          "value": { "min": 1 }
        }]
    },
    "sort": { "price": "asc" }
  }
  window.open("https://www.pathofexile.com/trade/search/?q=" + encodeURIComponent(JSON.stringify(query)), '_blank');
}


window.buildTree = buildTree
window.buildTimelessJewelTradeString = buildTimelessJewelTradeString
window.buildImpossibleEscapeTradeString = buildImpossibleEscapeTradeString


$(function() {
  $("body").click(function() {
    if ($("#draw-shapes").attr("toggled") == "true"){
      $("#draw-shapes").toggle();
      $("#draw-shapes").attr("toggled", "false");
      return
    }
  });
});

