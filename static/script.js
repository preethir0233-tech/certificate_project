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

}
