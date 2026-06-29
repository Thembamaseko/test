window.onload = function(){
    let count = 20;
const countdownElement = document.getElementById("timer");
const result = document.getElementById("result");

const timer = setInterval(() => {
  count--;
  countdownElement.innerText = count;
  let widthpercentage = (count / 20) * 100;
  countdownElement.style.width = widthpercentage + "%";

  if (widthpercentage <= 80) {
    countdownElement.style.backgroundColor = "limegreen";
  }
  
   if(widthpercentage <= 50) {
        countdownElement.style.backgroundColor = "#c3f05a";
  }

   if(widthpercentage <= 30) {
        countdownElement.style.backgroundColor = "red";

  }

  if (count ===13) {

      let i = Math.floor(Math.random() * 2);
    coin.style.animation = "none";
    if (i) {
        setTimeout(function () {
            coin.style.animation = "spin-heads 20s forwards";
        }, 100);
    } else {
        setTimeout(function () {
            coin.style.animation = "spin-tails 20s forwards";
        }, 100);
    }
    setTimeout(updateStats, 20000);

  }

  if (count <= 0) {
    clearInterval(timer);
    timer.innerText("Times Up")
  }
}, 1000);
}