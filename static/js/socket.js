    const socket = io("https://game-jjad.onrender.com");

    const timer = document.getElementById('timer');
    const bets = document.getElementById('submit');
    const coin = document.getElementById('coin');
    const spinIdInput = document.getElementById('current-spin-id');
    const recentResults = document.getElementById('recent-results');


    // 1. Listen for the suspense spin trigger from the server
socket.on('spin_suspense_start', function() {
    coin.style.animation = "spin-suspense 2s infinite linear"; 
});

// 2. Listen for the final true outcome at timer tick 2
socket.on('spin_animation', function(data) {
    // Strip old animations completely to force a redraw/snapping reset
    coin.style.animation = "none";
    
    // Tiny timeout to let the browser register that the old animation stopped
    setTimeout(function () {
        if (data.result === 'Heads') {
            coin.style.animation = "settle-heads 2s forwards ease-out";
        } else if (data.result === 'Tails') {
            coin.style.animation = "settle-tails 2s forwards ease-out";
        }
    }, 50);
});
    socket.on('recent_spin_update', function(data) {
        recentResults.innerHTML = '';
        data.results.forEach(function(result) {
            let li = document.createElement('li');
            let img = document.createElement('img');
            img.className = "recent-img";
            if(result === 'Heads') {
                img.src  = "../static/images/heads.png";
            } else if(result === 'Tails') {
                img.src = "../static/images/tails.png";
            }
            li.appendChild(img);
            recentResults.appendChild(li);
        });
    });

    socket.on('balance_update',function(data){
        document.getElementById('scount').innerText = "R"+ data.coins;
    })


    window.onload = function(){
        socket.emit("start_timer");
        socket.emit('recent_spin_update')
    }

    socket.on("timer_update",function(data){

        let currentTimer = data.timer;
        let mode = data.mode;
        console.log("data")
        timer.innerText = data.timer;
        let widthpercentage = (data.timer / 10) * 100;
        timer.style.width = widthpercentage + "%";
        if(widthpercentage == 100){
        }
        if(widthpercentage == 90 && mode == "down"){
                        bets.style.visibility = "visible";

        }

        if (widthpercentage === 70) {
            timer.style.backgroundColor = "limegreen";
            //this method will execute when our timer is going down
             
        } if(widthpercentage <= 50) {
            timer.style.backgroundColor = "#c3f05a";
        }
        if(widthpercentage == 20) {
            timer.style.backgroundColor = "red";
            bets.style.visibility = "hidden";

        }
    });

    socket.on("timer_finished",function(){
        timer.innerHTML = "Done"

        
    })
   
   // Assuming 'socket' is defined globally via io() in your socket.js file
if (typeof socket !== 'undefined') {
    
    // Listen for the 'new_spin' event broadcasted by the Flask server
    socket.on('new_spin', function(data) {
        console.log("Received new spin ID from server:", data.spin_id);
        
        // Update the value of the input field
        if (spinIdInput) {
            spinIdInput.value = data.spin_id;
        }
    });
    
}

