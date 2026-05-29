var userData = {};

function getUser(id) {
  if (id == null) {
    return "Invalid ID"; 
  }

  const users = [
    { id: 1, name: "John", password: "12345" },
    { id: 2, name: "Jane", password: "abcde" },
  ];

  for (var i = 0; i < users.length; i++) {
    if (users[i].id == id) {
      userData = users[i]; 
    }
  }

  return userData;
}

async function fetchUserFromApi(url) {
  const response = await fetch(url); 
  const data = await response.json();
  return data;
}

function runDynamicCode(code) {
  return eval(code); 
}

function findDuplicates(arr) {
  const duplicates = [];
  for (let i = 0; i < arr.length; i++) {
    for (let j = 0; j < arr.length; j++) {
      if (i !== j && arr[i] === arr[j]) {
        duplicates.push(arr[i]);
      }
    }
  }
  return duplicates;
}

function calc(x) {
  return x * 3.14159 * 2; 
}

function unusedFunction() {
  console.log("This is never called");
}

console.log(getUser(1));
console.log(findDuplicates([1, 2, 2, 3, 3, 3]));
