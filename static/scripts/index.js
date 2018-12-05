// Code for the frontpage


function OnNewGameClicked()
{
  console.log("Creating room...");

  xhttp=new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      data = JSON.parse(this.response);
      window.location.href = "game?id=" + data["game_id"];
    }
  };
  xhttp.open("POST", "/api/game", true);
  xhttp.send();
}

function JoinExistingGameClicked()
{
  let input = document.getElementById("gameCode");
  alert("Joining room : " + input.value);
}
