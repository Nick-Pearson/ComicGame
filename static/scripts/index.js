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
  let code = document.getElementById("gameCode");
  let name = document.getElementById("playerName");

  xhttp=new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4)
    {
      if(this.status == 200)
      {
        data = JSON.parse(this.responseText);
        window.location.href = "game?id=" + data["game_id"];
      }
      else
      {
        alert("Error!");
      }
    }
  };

  xhttp.open("POST", "/api/game/" + encodeURIComponent(code.value) + "/join", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("name=" + encodeURIComponent(name.value));
}
