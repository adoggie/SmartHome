/**
 *  blue-earth.js
 *  设备信息订阅
 */

$(function() {
    // socket = io.connect('/quotes');
    socket = io.connect('http://localhost:18808/blue-earth/device');

    socket.on('connect', function () {
        $('#status').addClass('connected');
        $('#status').text('已连接');
    });

    socket.on('error', function (e) {
        console.debug(JSON.stringify(e));

    });
    var  counter = 0
    socket.on('data', function (symbol,tick) {
        counter +=1;
        $('#device_detail').text(JSON.stringify(tick));
        // $('#counter').text(counter);
    });

    $("#device_list").change(function(){

    });

     $(function () {
        $('#btn_sub').click(function (ev) {
            var device_id = $("#device_list").val();
            socket.emit('subscribe', device_id, function (set) {
                alert('操作成功!' + JSON.stringify(set));
            });
            return false;
        });

        $('#btn_unsub').click(function (e) {
            var device_id = $("#device_list").val();
            socket.emit('unsubscribe', device_id, function (set) {
                alert('操作成功!' + JSON.stringify(set));
            });

        });

    });


});