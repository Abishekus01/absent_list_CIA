// 1. Sample Master Sheet
const students = [
  {reg: "CS001", name: "Arun", dept: "CSE", sem: 5, sec: "A", subject: "CS301"},
  {reg: "CS002", name: "Bala", dept: "CSE", sem: 5, sec: "A", subject: "CS301"},
  {reg: "CS003", name: "Divya", dept: "CSE", sem: 5, sec: "B", subject: "CS302"},
  {reg: "CS004", name: "Karthi", dept: "CSE", sem: 5, sec: "B", subject: "CS302"}
];

let absentList = [];

function loadStudents() {
  const subject = document.getElementById("subject").value;
  const tableBody = document.querySelector("#attendanceTable tbody");
  tableBody.innerHTML = "";
  absentList = [];

  students
    .filter(s => s.subject === subject)
    .forEach(s => {
      const row = document.createElement("tr");

      row.innerHTML = `
        <td>${s.reg}</td>
        <td>${s.name}</td>
        <td>${s.dept}</td>
        <td>${s.sem}</td>
        <td>${s.sec}</td>
        <td>
          <input type="checkbox" checked
            onchange="markAbsent(this, '${s.reg}', '${s.name}')">
        </td>
      `;
      tableBody.appendChild(row);
    });
}

// 9. Absent Students List
function markAbsent(cb, reg, name) {
  if (!cb.checked) {
    absentList.push({reg, name});
  } else {
    absentList = absentList.filter(s => s.reg !== reg);
  }
}

// 10. Download CSV
function downloadAbsent() {
  let csv = "Reg No,Name\n";
  absentList.forEach(s => {
    csv += `${s.reg},${s.name}\n`;
  });

  const blob = new Blob([csv], { type: "text/csv" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "Absent_List.csv";
  link.click();
}
