const choiceinput = document.getElementById("choice")

const betAmount = document.getElementById("betamount")
const heads = document.getElementById("heads")
const tails = document.getElementById("tails")

const increase = document.getElementById("increase")
const decrease = document.getElementById("decrease")

const submit = document.getElementById("submit")

function updateSubmit(){
    const choice = choiceinput.value;
    const amount = betAmount.value;

    if (choice === ""){
        submit.value = "Place a bet";

    }else{
        submit.value = `${choice} at R${amount}`;
    }
}

 heads.addEventListener('click',()=>{
        choiceinput.value = "Heads";
        updateSubmit();
    })

    tails.addEventListener('click',()=>{
        choiceinput.value = "Tails";
        updateSubmit();
    })

increase.addEventListener('click',()=>{
    betAmount.value = parseInt(betAmount.value) + 1;
    updateSubmit();
})

decrease.addEventListener('click',()=>{
    let current = parseInt(betAmount.value);
    if (current > 1){
        betAmount.value = current - 1;
        updateSubmit();
    }
})

betAmount.addEventListener('input',()=>{

    let amount = parseInt(betAmount.value);

    if (isNaN(amount) || amount < 1){
        betAmount.value = 1;
    }

    updateSubmit();

})

