async function fetch_list(){
    try{
        const response = await fetch("/file/list");
        const data = await response.json();
        console.log(data);
        
        const ul = document.getElementById("video-list");
        data.videos.forEach(element => {
            const li = document.createElement("li"); 
            li.innerHTML = `<a href='/source/${element.id}'>${element.filename}</a>`;
            ul.append(li);
        });
    }
    catch(error){
        console.error(error);
    }
}
fetch_list();