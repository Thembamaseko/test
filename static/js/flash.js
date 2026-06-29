document.addEventListener('DOMContentLoaded',()=>{
    const flash = document.querySelector('.flash-container');
    if (flash){
        setTimeout(()=>{
            flash.style.transition= "opacity 0.5s ease";
            flash.style.opacity ="0";

            setTimeout(()=>
                flash.remove(),500)
        },1000)
    }
})