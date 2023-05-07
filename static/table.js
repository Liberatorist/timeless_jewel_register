$(document).ready(function () {
    var input_effect = $('#min_effect');
    var input_effect_pp = $('#min_effect_pp');
    var input_max_points = $('#max_points');
    var input_max_price = $('#max_price');
    var input_position = $('#position');
    var input_jewel_type = $('#jewel');
    var input_ie = $('#ie');
    var input_anoint = $('#anoint');

    // Custom range filtering function
    $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
        var filter_min_effect = parseInt(input_effect.val(), 0);
        var filter_min_effect_pp = parseFloat(input_effect_pp.val(), 0);
        var filter_max_points = parseInt(input_max_points.val(), 0);
        var filter_max_price = parseFloat(input_max_price.val(), 0);
        var filter_position = String(input_position.val());
        var filter_jewel_type = String(input_jewel_type.val());
        var filter_ie = String(input_ie.val());
        var filter_anoint = String(input_anoint.val());

        var data_type = data[1] || NaN;
        var data_position = data[2] || NaN;
        var data_effect = parseFloat(data[4]) || 0;
        var data_points = parseFloat(data[5]) || 0;
        var data_effect_pp = parseFloat(data[6]) || 0;
        var data_ie = data[7] || NaN;
        var data_anoint = data[8] || NaN;
        var data_price = parseFloat(data[9]) || 0;

        if (data_effect < filter_min_effect){ return false; }
        if (data_effect_pp < filter_min_effect_pp){ return false; }
        if (data_points > filter_max_points){ return false; }
        if (filter_position != "null" && filter_position != "Any" && data_position.toLowerCase().indexOf(filter_position.toLowerCase()) === -1 ){ return false; }
        if (filter_jewel_type != "null" && filter_jewel_type != "Any" && data_type.toLowerCase().indexOf(filter_jewel_type.toLowerCase()) === -1 ){ return false; }
        if (filter_ie != "null" && filter_ie != "Any" && (data_ie != filter_ie) ){ return false; }
        if (filter_anoint != "null" && filter_anoint != "Any" && (data_anoint != filter_anoint) ){ return false; }
        if (data_price > filter_max_price){ return false; }
        return true;
    })
    
    
    $('#divide').on('change', function () {
    table.rows().invalidate('data');
    table.draw(false);
    });


    var table = $('#data').DataTable({
        retrieve: true,
        columnDefs: [
            // {   
                // render: function (data, type, row) {
                //     if (row[7]=="True"){
                //         return parseInt(row[5]) + 3;
                //     }
                //     return row[5];
                // },
                // targets:5
            // },
            {   
                render: function (data, type, row) {
                    var div = parseFloat(row[4]) / parseFloat(row[5]);
                    return Math.round(div * 100) / 100;
                },
                targets:6
            },
        ]
    });
    $('#data_filter').hide();
    // Changes to the inputs will trigger a redraw to update the table
    input_effect.on('input', function () {
        table.draw();
    });
    input_max_points.on('input', function () {
        table.draw();
    });
    input_position.on('input', function () {
        table.draw();
    });
    input_jewel_type.on('input', function () {
        table.draw();
    });
    input_ie.on('input', function () {
        table.draw();
    });
    input_anoint.on('input', function () {
        table.draw();
    });
    input_max_price.on('input', function () {
        table.draw();
    });
});