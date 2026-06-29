  const buttons = document.querySelectorAll('.bet-btn');
  const userInput = document.getElementById('betamout');
  const submitBtn = document.getElementById('submit');
 
 let selectedSide = "";

 const increaseBtn = document.getElementById('increase');
 const decreaseBtn = document.getElementById('decrease');


 increaseBtn.addEventListener("click", () => {
    let currentValue = parseInt(userInput.value) || 1;
    userInput.value = currentValue + 1;
    updateSubmit();
}
)

 decreaseBtn.addEventListener("click", () => {
    let currentValue = parseInt(userInput.value) || 1;
    if (currentValue > 0) {
            userInput.value = currentValue - 1;
            updateSubmit();
    }
    
}
)

    function updateSubmit(){
        const text = userInput.value;

        if(selectedSide && text){
            submitBtn.textContent = `${selectedSide} At R${text}`;
        } else {
            submitBtn.textContent = selectedSide || text || 'Submit';
    }
}
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            selectedSide = button.getAttribute('data-value');
            updateSubmit();
        });
    });

    userInput.addEventListener('input', updateSubmit);






   