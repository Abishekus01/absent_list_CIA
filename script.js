const admins = [
  { id: "admin01", pass: "admin123" }
];

const staff = [
  { id: "staff101", pass: "staff123", slot: "9:15 - 10:45" }
];

function login() {
  const role = role.value;
  const id = loginId.value;
  const pass = loginPass.value;

  if (role === "admin") {
    const a = admins.find(x => x.id === id && x.pass === pass);
    if (a) window.location.href = "admin.html";
    else error.innerText = "Invalid Admin Login";
  }

  if (role === "staff") {
    const s = staff.find(x => x.id === id && x.pass === pass);
    if (s) {
      localStorage.setItem("slot", s.slot);
      window.location.href = "staff.html";
    } else error.innerText = "Invalid Staff Login";
  }
}
