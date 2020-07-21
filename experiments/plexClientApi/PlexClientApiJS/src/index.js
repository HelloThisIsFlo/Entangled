import password from "./plexPass";
import token from "./plexToken";
const username = "shockn745@gmail.com";

const SIGNIN = "https://plex.tv/users/sign_in.xml";
const RESSOURCES =
  "https://plex.tv/api/resources?includeHttps=1&includeRelay=1";
const PIPEDREAM = "https://8ae75063b87060749dbab0b02d7dd057.m.pipedream.net";

const list = (htmlCollection) => Array.from(htmlCollection);
const authHeader = `Basic ${btoa(`${username}:${password}`)}`;
console.log(authHeader);

// fetch(SIGNIN, {
//   method: "POST",
//   headers: {
//     authorization: authHeader,
//     "X-Plex-Client-Identifier": "sandboxJS",
//   },
// })
//   .then((response) => response.text())
//   .then((str) => new window.DOMParser().parseFromString(str, "text/xml"))
//   .then((data) => console.log(data))
//   .catch(e => console.log(e))

async function sandboxResources() {
  const ressourcesXml = await fetch(RESSOURCES, {
    method: "GET",
    headers: { "X-Plex-Client-Identifier": "sandboxJS", "X-Plex-Token": token },
  })
    .then((response) => response.text())
    .then((xmlString) =>
      new DOMParser().parseFromString(xmlString, "text/xml")
    );

  const devices = list(ressourcesXml.getElementsByTagName("Device"));
  console.log(devices);
  devices.forEach((device) => {
    const name = device.getAttribute("name");
    console.log(`------ ${name} --------------------------`);
    const lastSeen = new Date(device.getAttribute("lastSeenAt") * 1000);
    console.log(device);
    console.log(lastSeen);
    list(device.children).forEach((child) => console.log(child));
    console.log(`------ ${name} --------------------------`);
  });
}

async function sandboxConnection() {
  const macbookPlayerUri = "http://172.20.10.3:32433";
  // <Connection
  // protocol="http"
  // address="172.20.10.3"
  // port="32433"
  // uri="http://172.20.10.3:32433"
  // local="1">
}

sandboxResources();
