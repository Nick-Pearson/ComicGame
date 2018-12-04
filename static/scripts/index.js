// Code for the frontpage


function OnNewGameClicked()
{
  alert("Creating room");
}

function JoinExistingGameClicked()
{
  let input = document.getElementById("roomCode");
  alert("Joining room : " + input.value);
}
