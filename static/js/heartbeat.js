var node = document.getElementById('account_username');
var timeoutUrl = '/authenticate-user/check-token/timeout/';
const channel = new BroadcastChannel("sess_channel");
// Listen for messages from the channel
channel.onmessage = function (event) {
    switch (event.data) {
        case 'session timeout':
            setTimeout(function () { window.location.href = timeoutUrl; }, 10000);
            break;
        case 'session expired':
            window.location.href = timeoutUrl;
            break;
    }
};

function sendHeartbeat() {
    var username = node.textContent || node.innerText;

    fetch('/get_heartbeat/' + username)
        .then(response => response.json())
        .then(data => {
            if (data.session_Inactive) {
                channel.postMessage('session timeout');
                window.location.href = timeoutUrl;
                channel.postMessage('session expired');
            }
            else {
                channel.postMessage('session online');
            }
        })
        .catch(error => {
            channel.postMessage('session expired');
            window.location.href = timeoutUrl;
        });
}

setInterval(() => sendHeartbeat(), 1200000); // check session every 20 mins

function heartAttack(){
    document.getElementById('logout_currentUser').addEventListener('click', function () {
        channel.postMessage('session expired');
    });
}

