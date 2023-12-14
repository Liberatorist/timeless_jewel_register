const time_formatter = new Intl.RelativeTimeFormat("en", {
  numeric: "auto",
  style: "long",
  localeMatcher: "best fit",
});

const currentDate = new Date(Date.now());

function time_diff(timestamp) {
  const minutes = (new Date(timestamp + ":00.000000Z") - currentDate) / 60000;
  if (Math.abs(minutes) < 60) {
    return time_formatter.format(Math.round(minutes), "minute");
  }
  const hours = minutes / 60;
  if (Math.abs(hours) < 24) {
    return time_formatter.format(Math.round(hours), "hour");
  }
  const days = hours / 24;
  return time_formatter.format(Math.round(days), "day");
}

function isRecent(timestamp) {
  const days =
    (currentDate - new Date(timestamp + ":00.000000Z")) / 60000 / 60 / 24;
  return days <= 2;
}

var solutions = await fetch("./solutions.json").then((res) => res.json());
var prices = await fetch("./prices.json").then((res) => res.json());

var keystone_map = {
  58556: "Divine Shield",
  31961: "Resolute Technique",
  19732: "The Agnostic",
  41970: "Ancestral Bond",
  57279: "Blood Magic",
  63425: "Zealot's Oath",
  39713: "Glancing Blows",
  44941: "Avatar of Fire",
  42343: "Runebinder",
  23090: "Call to Arms",
  24720: "Imbalanced Guard",
  21650: "Eternal Youth",
  22088: "Elemental Overload",
  34098: "Mind Over Matter",
  57257: "The Impaler",
  40907: "Unwavering Stance",
  17818: "Crimson Dance",
  50288: "Iron Will",
  10661: "Iron Reflexes",
  12926: "Iron Grip",
  45175: "Necromantic Aegis",
  60247: "Solipsism",
  56116: "Magebane",
  43988: "Hex Master",
  18663: "Minion Instability",
  50679: "Versatile Combatant",
  23540: "Conduit",
  10808: "Vaal Pact",
  23950: "Wicked Ward",
  39085: "Elemental Equilibrium",
  31703: "Pain Attunement",
  56075: "Eldritch Battery",
  49639: "Supreme Ego",
  63620: "Precise Technique",
  42178: "Point Blank",
  11239: "Wind Dancer",
  11455: "Chaos Inoculation",
  62791: "Lethe Shade",
  54922: "Arrow Dancing",
  35255: "Ghost Dance",
  24426: "Ghost Reaver",
  23407: "Perfect Agony",
  54307: "Acrobatics",
  12953: "Disciple of Kitava",
  3354: "Lone Messenger",
  30847: "Nature's Patience",
  57280: "Secrets of Suffering",
  40561: "Kineticism",
  32118: "Veteran's Awareness",
  60069: "Hollow Palm Technique",
  37081: "Pitfighter",
};
var num2slot = [
  "Cluster (Zealot's Oath)",
  "Marauder",
  "Ghost Dance",
  "Minion Instability",
  "Cluster (Call to Arms)",
  "Eternal Youth",
  "Pain Attunement",
  "Iron Will",
  "Iron Grip",
  "Runebinder",
  "Acrobatics",
  "Solipsism",
  "Cluster (Divine Shield)",
  "Unwavering Stance",
  "Mind over Matter",
  "Duelist",
];
var key2num = {
  seed: 0,
  type: 1,
  effect: 2,
  slot: 3,
  active_nodes: 4,
  aura_nodes: 5,
  cost: 6,
  anoint: 7,
  ie: 8,
};
var jewel_image_map = [
  "static/Brutal_Restraint_inventory_icon.png",
  "static/Glorious_Vanity_inventory_icon.png",
  "static/Elegant_Hubris_inventory_icon.png",
];
var jewel_map = ["Brutal Restraint", "Glorious Vanity", "Elegant Hubris"];

$(document).ready(function () {
  var table = $("#data").DataTable({
    data: solutions,
    columns: [
      { title: "Tree" },
      { title: "Jewel Type" },
      { title: "Position" },
      { title: "Seed" },
      { title: "Aura Effect" },
      { title: "Points to Allocate" },
      { title: "Effect p.p." },
      { title: "Requirements" },
      { title: "Price (div)" },
      { title: "Trade" },
    ],
    columnDefs: [
      { width: "65px", targets: [9] },
      { width: "70px", targets: [3, 4, 5, 6, 8] },
      {
        render: function (data, type, row, meta) {
          return (
            '<button onclick="buildTree(event,' +
            meta.row +
            ')" style="height:30px;width:30px"></button>'
          );
        },
        orderable: false,
        targets: 0,
      },
      {
        render: function (data, type, row) {
          return (
            '<img title="' +
            jewel_map[row[key2num["type"]]] +
            '" src=' +
            jewel_image_map[row[key2num["type"]]] +
            ' width="30" height="30"><hidden style="display:none;">' +
            row[key2num["type"]] +
            "</hidden>"
          );
        },
        targets: 1,
      },
      {
        render: function (data, type, row) {
          return num2slot[row[key2num["slot"]]];
        },
        targets: 2,
      },
      {
        render: function (data, type, row) {
          return row[key2num["seed"]];
        },
        targets: 3,
      },
      {
        render: function (data, type, row) {
          return row[key2num["effect"]];
        },
        targets: 4,
      },
      {
        render: function (data, type, row) {
          return row[key2num["cost"]];
        },
        targets: 5,
      },
      {
        render: function (data, type, row) {
          var div =
            parseFloat(row[key2num["effect"]]) /
            parseFloat(row[key2num["cost"]]);
          return Math.round(div * 100) / 100;
        },
        targets: 6,
      },
      {
        render: function (data, type, row) {
          if (row[key2num["ie"]] != "") {
            return (
              '<img title="Impossible Escape at &quot;' +
              keystone_map[row[key2num["ie"]]] +
              '&quot;" src="static/Impossible_Escape_inventory_icon.png" width="30" height="30"><hidden style="display:none;">i</hidden>'
            );
          }
          if (row[key2num["anoint"]] != "") {
            return '<img src="static/Golden_Oil_inventory_icon.png" width="30" height="30"><hidden style="display:none;">a</hidden>';
          }
          return "";
        },
        targets: 7,
      },
      {
        render: function (data, type, row) {
          if (
            prices["timeless"][row[key2num["type"]]][row[key2num["seed"]]] ==
            undefined
          ) {
            return "";
          }
          var price =
            prices["timeless"][row[key2num["type"]]][row[key2num["seed"]]][0];

          if (!price) {
            return "";
          }
          if (row[key2num["ie"]] != "") {
            price += prices["ie"][row[key2num["ie"]]][0];
          }
          var last_seen =
            prices["timeless"][row[key2num["type"]]][row[key2num["seed"]]][1];
          return (
            '<span title="Last seen ' +
            time_diff(last_seen) +
            '"> ' +
            Math.round(parseFloat(price) * 100) / 100 +
            "</span>"
          );
        },
        targets: 8,
      },
      {
        render: function (data, type, row) {
          var html =
            '<a href="javascript:buildTimelessJewelTradeString(' +
            row[key2num["type"]] +
            "," +
            row[key2num["seed"]] +
            ');"> \
                                <img title="' +
            jewel_map[row[key2num["type"]]] +
            '" src=' +
            jewel_image_map[row[key2num["type"]]] +
            ' width="30" height="30"> \
                                </a>';
          if (row[key2num["ie"]] != "") {
            html +=
              '<a href="javascript:buildImpossibleEscapeTradeString(' +
              row[key2num["ie"]] +
              ');">\
                                 <img title="Impossible Escape at &quot;' +
              keystone_map[row[key2num["ie"]]] +
              '&quot;" src="static/Impossible_Escape_inventory_icon.png" width="30" height="30" > \
                                 </a>';
          }
          return html;
        },
        orderable: false,
        targets: 9,
      },
    ],
  });
  $("#data tfoot tr").appendTo("#data thead");

  var input_effect = $("#min_effect");
  var input_effect_pp = $("#min_effect_pp");
  var input_max_points = $("#max_points");
  var input_max_price = $("#max_price");
  var input_position = $("#position");
  var input_jewel_type = $("#jewel");
  var input_requirements = $("#requirements");
  var input_seed = $("#seed");
  var input_show_recent = $("#recent");

  // Custom range filtering function
  $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
    var filter_min_effect = parseInt(input_effect.val(), 0);
    var filter_min_effect_pp = parseFloat(input_effect_pp.val(), 0);
    var filter_max_points = parseInt(input_max_points.val(), 0);
    var filter_max_price = parseFloat(input_max_price.val(), 0);
    var filter_position = String(input_position.val());
    var filter_jewel_type = parseFloat(input_jewel_type.val(), 0);
    var filter_requirements = String(input_requirements.val());
    var filter_seed = String(input_seed.val());

    var data_type = parseFloat(data[1]) || 0;
    var data_position = String(data[2]) || 0;
    var data_seed = String(data[3]) || 0;
    var data_effect = parseFloat(data[4]) || 0;
    var data_points = parseFloat(data[5]) || 0;
    var data_effect_pp = parseFloat(data[6]) || 0;
    var data_requirements = String(data[7]) || 0;
    var data_price = parseFloat(data[8]) || 0;

    if (data_effect < filter_min_effect) {
      return false;
    }
    if (data_effect_pp < filter_min_effect_pp) {
      return false;
    }
    if (data_points > filter_max_points) {
      return false;
    }
    if (
      filter_position != "null" &&
      filter_position != "Any" &&
      data_position != filter_position
    ) {
      return false;
    }
    if (!isNaN(filter_jewel_type) && data_type != filter_jewel_type) {
      return false;
    }
    if (
      (filter_requirements == "no_ie" || filter_requirements == "basic") &&
      data_requirements == "i"
    ) {
      return false;
    }
    if (
      (filter_requirements == "no_anoint" || filter_requirements == "basic") &&
      data_requirements == "a"
    ) {
      return false;
    }
    if (
      !isNaN(filter_seed) &&
      data_seed.toLowerCase().indexOf(filter_seed.toLowerCase()) === -1
    ) {
      return false;
    }
    if (data_price > filter_max_price) {
      return false;
    }
    if (
      input_show_recent.is(":checked") &&
      prices["timeless"][data_type][data_seed] != undefined &&
      (!isRecent(prices["timeless"][data_type][data_seed][1]) ||
        data_price == 0)
    ) {
      return false;
    }
    return true;
  });
  $("#divide").on("change", function () {
    table.rows().invalidate("data");
    table.draw(false);
  });
  $("#data_filter").hide();
  // Changes to the inputs will trigger a redraw to update the table
  input_effect.on("input", function () {
    table.draw();
  });
  input_effect_pp.on("input", function () {
    table.draw();
  });
  input_max_points.on("input", function () {
    table.draw();
  });
  input_position.on("input", function () {
    table.draw();
  });
  input_jewel_type.on("input", function () {
    table.draw();
  });
  input_requirements.on("input", function () {
    table.draw();
  });
  input_max_price.on("input", function () {
    table.draw();
  });
  input_seed.on("input", function () {
    table.draw();
  });
  input_show_recent.on("input", function () {
    console.log(input_show_recent.is(":checked"));
    table.draw();
  });
});
