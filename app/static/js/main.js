console.log('In main.js , invoked');


var usernameInput = document.querySelector('#username');

var btnJoin = document.querySelector('#btn-join');
var messageList = document.querySelector('#message-list');
var messageInput = document.querySelector('#msg');
var mapPeers = {};
var btnSendMsg = document.querySelector('#btn-send-msg');
var username;
var chatContainer = document.querySelector('#chat-container');
var webSocket;

function webSocketOnMessage(event){
    var parsedData = JSON.parse(event.data);
    var peerUsername  = parsedData['peer'];
    var action = parsedData['action'];

    if(username == peerUsername){
        return;
    }
    
    var receiver_channel_name = parsedData['message']['receiver_channel_name'];

    if(action == 'new-peer'){

        createOfferer(peerUsername, receiver_channel_name);

        return;
    }

    if(action == 'new-offer'){
        var offer = parsedData['message']['sdp'];

        createAnswerer(offer,peerUsername, receiver_channel_name);

        return;
    }

    if(action == 'new-answer'){
        var answer = parsedData['message']['sdp'];

        var peer = mapPeers[peerUsername][0];

        peer.setRemoteDescription(answer);

        return;
    }
}

btnSendMsg.addEventListener('click', sendMsgOnClick);

function getDataChannels(){
    var dataChannels = [];

    for(peer in mapPeers){
        var datachannel = mapPeers[peer][1];

        dataChannels.push(datachannel);
    }

    return dataChannels;
}

function sendMsgOnClick(){
    var message = messageInput.value;

    messageInput.value = '';

    var li = document.createElement('li');

    li.appendChild(document.createTextNode('Me: ' + message));

    messageList.appendChild(li);

    var datachannels = getDataChannels();

    message = username + ': ' + message;

    for(index in datachannels){
        datachannels[index].send(message);
    }

    messageInput.value = '';
}



btnJoin.addEventListener('click', () => {
    username = usernameInput.value;

    console.log('username: ',username);

    if(username == ''){
        return;
    }

    usernameInput.value = '';
    usernameInput.disabled = true;
    usernameInput.style.visibililty = 'hidden';
    
    btnJoin.disabled = true;
    btnJoin.style.visibililty = 'hidden';

    document.getElementById('label-username').innerText = username;

    // Display both the video container and the chat container
    document.getElementById('video-container').style.display = 'block';
    chatContainer.style.display = 'block';

    var loc = window.location;
    var wsStart = 'ws://';

    if(loc.protocol == 'https:'){
        wsStart = 'wss://';
    }

    var endPoint = wsStart + loc.host + loc.pathname;

    console.log('endpoint: ', endPoint);

    webSocket = new WebSocket(endPoint);

    webSocket.addEventListener('open', (e) => {
        console.log("Connection Opened");

        sendSignal('new-peer', {});
    });
    webSocket.addEventListener('close',(e) => {
        console.log("Connection Closed");
    });

    webSocket.addEventListener('error',(e) => {
        console.log("Error Occured");
    });

    webSocket.addEventListener('message', webSocketOnMessage);
});


var localStream = new MediaStream();

const constraints = {
    'video': true,
    'audio': true
};

const localVideo = document.querySelector('#local-video');

const btnToggleAudio = document.querySelector('#btn-toggle-audio');

const btnToggleVideo = document.querySelector('#btn-toggle-video');

const userMedia = navigator.mediaDevices.getUserMedia(constraints)
    .then(stream => {
        localStream = stream;
        localVideo.srcObject = localStream;
        localVideo.muted = true;

        var audioTracks = stream.getAudioTracks();

        var videoTracks = stream.getVideoTracks();

        audioTracks[0].enabled = true;

        videoTracks[0].enabled = true;

        btnToggleAudio.addEventListener('click', () => {
            audioTracks[0].enabled = !audioTracks[0].enabled;

            if(audioTracks[0].enabled){
                btnToggleAudio.innerHTML = 'Audio Mute';

                return;
            }

            btnToggleAudio.innerHTML = 'Audio Unmute';
        });

        btnToggleVideo.addEventListener('click', () => {
            videoTracks[0].enabled = !videoTracks[0].enabled;

            if(videoTracks[0].enabled){
                btnToggleVideo.innerHTML = 'Video Off';

                return;
            }

            btnToggleVideo.innerHTML = 'Video On';
        });
    })
    .catch(error => {
        console.log('Error accessing media devices.', error);
    })




function sendSignal(action, message){
    var jsonStr = JSON.stringify({
        'peer': username,
        'action': action,
        'message': message,
    });
    
    webSocket.send(jsonStr);
}


function createOfferer(peerUsername, receiver_channel_name){
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);

    var dc = peer.createDataChannel('channel');
    dc.addEventListener('open', () => {
        console.log('Connection opened!');
    });

    dc.addEventListener('message', dcOnMessage);

    var remoteVideo = createVideo(peerUsername);

    setOnTrack(peer, remoteVideo);

    mapPeers[peerUsername] = [peer, dc];

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceconnectionstate = peer.iceConnectionState;

        if(iceconnectionstate === 'failed' || iceconnectionstate === 'disconnected' || iceconnectionstate === 'closed'){
            delete mapPeers[peerUsername];

            if(iceconnectionstate != 'closed'){
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if(event.candidate){
            console.log("New ice candidate: ", JSON.stringify(peer.localDescription));

            return;
        }

        sendSignal('new-offer',{
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });
    });

    peer.createOffer()
    .then(o => peer.setLocalDescription(o))
    .then(() => {
        console.log('Local description set successfully');
    });
}

function createAnswerer(offer , peerUsername, receiver_channel_name){
    var peer = new RTCPeerConnection(null);

    addLocalTracks(peer);

    var remoteVideo = createVideo(peerUsername);

    setOnTrack(peer, remoteVideo);

    peer.addEventListener('datachannel', e => {
        peer.dc = e.channel;

        peer.dc.addEventListener('open', () => {
            console.log('Connection opened!');
        });
    
        peer.dc.addEventListener('message', dcOnMessage);

        mapPeers[peerUsername] = [peer, peer.dc];
    });
    

    peer.addEventListener('iceconnectionstatechange', () => {
        var iceconnectionstate = peer.iceConnectionState;

        if(iceconnectionstate === 'failed' || iceconnectionstate === 'disconnected' || iceconnectionstate === 'closed'){
            delete mapPeers[peerUsername];

            if(iceconnectionstate != 'closed'){
                peer.close();
            }

            removeVideo(remoteVideo);
        }
    });

    peer.addEventListener('icecandidate', (event) => {
        if(event.candidate){
            console.log("New ice candidate: ", JSON.stringify(peer.localDescription));

            return;
        }

        sendSignal('new-answer',{
            'sdp': peer.localDescription,
            'receiver_channel_name': receiver_channel_name
        });
    });

    peer.setRemoteDescription(offer)
        .then(() => {
            console.log('Remote Description set successfully for %s.', peerUsername);

            return peer.createAnswer();
        })
        .then(a => {
            console.log('Answer created');

            peer.setLocalDescription(a);
        });


}
function addLocalTracks(peer){
    localStream.getTracks().forEach(track => {
        peer.addTrack(track, localStream);
    });

    return;
}


function dcOnMessage(event){
    var message = event.data;

    var li = document.createElement('li');

    li.appendChild(document.createTextNode(message));

    messageList.appendChild(li);
}

function createVideo(peerUsername){
    var videoContainer = document.querySelector('#video-container');

    var remoteVideo = document.createElement('video');

    remoteVideo.id = peerUsername + '-video';

    remoteVideo.autoplay = true;

    remoteVideo.playsInline = true;

    var videoWrapper = document.createElement('div');

    videoContainer.appendChild(videoWrapper);

    videoWrapper.appendChild(remoteVideo);

    return remoteVideo;
}

function setOnTrack(peer, remoteVideo){
    var remoteStream = new MediaStream();

    remoteVideo.srcObject = remoteStream;

    peer.addEventListener('track', async (event) =>{
        remoteStream.addTrack(event.track, remoteStream);
    });
}

function removeVideo(video){
    var videoWrapper = video.parentNode;

    videoWrapper.parentNode.removeChild(video);
}