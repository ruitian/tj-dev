/**
 * Created by mac on 16/6/23.
 */
// 此处的函数只是为了区分哪里是被选中的部分,js基础不好,代码很挫,以后重构的关键
var test = null;
var idName = 'dropdown';
function getDataid(e) {
    test = e.target.parentNode;
    if (e.target.parentNode.nodeName === 'LI') {
        e.target.parentNode.parentNode.parentNode.childNodes[3].innerHTML = e.target.innerText + " "
            + '<i class="fa fa-caret-down"></i>';
    }
};

function clear(el) {
    var card = el.getElementsByClassName('card');
    for (var i = 0; i < card.length; i++) {
        card[i].className = 'card';
    }
};

function changeClass(el) {
    var card = el.getElementsByClassName('card');
    for (var i = 0; i < card.length; i++) {
        card[i].onclick = function () {
            for (var j = 0; j < card.length; j++) {
                card[j].className = "card"
            }
            this.className = 'card current';
        }
    }
};

function change(el) {
    if (flag.id == el.id) {
        changeClass(el);
    } else {
        clear(flag);
        changeClass(el);
        flag = el;
    }
};

var el1 = document.getElementById('dropdown');
var el2 = document.getElementById('dropdown2');
var flag = el1;

el1.onclick = function () {
    change(el1);
};

el2.onclick = function () {
    change(el2);
};

el1.addEventListener('click', getDataid.bind(this), false);
el2.addEventListener('click', getDataid.bind(this), false);

//点击按钮开始创建项目
var form = document.getElementsByTagName('form');
function insert() {
    var inputValue = form[0][0].value;
    if (inputValue.length != 0) {
        form[0][1].disabled = false;
    } else {
        form[0][1].disabled = true;
    }
};

function createApp() {
    var el = document.getElementsByClassName('current');
    var appName = form[0][0].value;
    var code = el[0].childNodes[3].innerText;
    var data = {'proName': appName, 'code': code};
    form[0].childNodes[5].innerHTML = '<button class="btn btn-lg btn-block" aria-disabled="true"><i class="fa fa-spinner fa-spin fa-1x fa-fw"></i> 正在创建应用</button>';

    $.ajax({
        url: '/create_project',
        data: JSON.stringify(data),
        type: 'post',
        dataType: 'json',
        success: function (data) {
            window.location.href = '/build/new/' + data['verify'];
        }
    })
};