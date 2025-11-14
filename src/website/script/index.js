function add_new_chat_box(peer_code){
    const div = document.createElement("div");
    
    // it is accessby [data-peer-code=...]
    div.dataset.peerCode = peer_code;
    
    div.innerHTML = `

            <form onsubmit="send_msg(event)">
                <p><b>PEER CODE : <span class='peer_code'>${peer_code}</span></b></p>
                
                <input type="text" name="peer_msg" required>
                
                <button type="submit"><b>SEND</b></button>
            </form>
            
            <ul>                
            </ul> 
            <hr>  
    `
    
    document.querySelector("#chat-div").prepend(div);
}

async function connect_peer(event){
            
    event.preventDefault();
    
    const peer_code = document.querySelector("[name='peer_code']").value;
    
    // document.querySelector("[name='peer_code']").value = '';

    await fetch(`/peer/connect/${peer_code}`)
    .then(response => {
        return response.json();
    })
    .then(data=>{
        console.log(data["status"]);
        
        add_new_chat_box(peer_code);
    
    })
    .catch(err=>{
        console.error(err);
    }) ;

}

// -------------------------------------------
function send_msg(event){

    event.preventDefault();

    const input_field = event.target.querySelector("[name='peer_msg']");
    const peer_code = event.target.querySelector(".peer_code").textContent;

    const msg = input_field.value;    
    input_field.value = '';
    const msg_li = document.createElement("li");
    msg_li.className = "host";
    msg_li.innerHTML = `
        <b>
            <span>${msg}</span>
        </b>
    `
    
    const div = document.querySelector(`[data-peer-code='${peer_code}']`);
    const ul = div.querySelector("ul");
    ul.prepend(msg_li);
}

function rcv_msg(peer_code , msg){

    let div = document.querySelector(`[data-peer-code='${peer_code}']`);
    
    if(div == null){
        add_new_chat_box(peer_code);
        div = document.querySelector(`[data-peer-code='${peer_code}']`);
    }
    
    const msg_li = document.createElement("li");
    msg_li.className = "peer";
    msg_li.innerHTML = `
        <b>
            <span>${msg}</span>
        </b>
    `
    
    const ul = div.querySelector("ul");
    ul.prepend(msg_li);

}

// -------------------------------------------
let host_ip = null ;
let host_port = null;
let websocket = null;

async function init_websocket(){
  
    await fetch("/host_ip")
        .then(res=>res.json())
        .then(data=>{
            host_ip = data["ip"];
            host_port = data["port"];
        })
        .catch(err=>{
            console.log("error");
            console.log(err);
        });

    const ws_url = `ws://${host_ip}:${host_port}/ws`;

     // create the WebSocket with URL
    websocket = new WebSocket(ws_url);

    // attach onmessage after websocket is created
    websocket.onmessage = function(event) {

        const receivedData = JSON.parse(event.data);
        console.log("peer code : ",receivedData.peer_code);
        console.log("msg :", receivedData.msg );
        console.log("type : ",receivedData.type);

        rcv_msg(receivedData.peer_code , receivedData.msg)
    };

    websocket.onopen = () => {
        console.log("WebSocket connected!");
    };

    websocket.onerror = (err) => {
        console.error("WebSocket error:", err);
    };
}

init_websocket();

// ---------------------------------------------
