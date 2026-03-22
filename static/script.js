let time = 30;

function startTimer() {
    let timerDisplay = document.getElementById("timer");

    let countdown = setInterval(function () {
        time--;
        timerDisplay.innerText = "Time: " + time + "s";

        if (time <= 0) {
            clearInterval(countdown);
            alert("Time's up! Auto submitting...");
            document.querySelector("form").submit();
        }
    }, 1000);
<<<<<<< HEAD
}
=======
}
>>>>>>> 0dd5a8556395b2e3430105979f5af4582bf57e4e
