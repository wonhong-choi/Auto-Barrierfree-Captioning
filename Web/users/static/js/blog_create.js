var dateField = document.getElementById('id_날짜');
dateField.value = getDate(); // Set the current date value in the date field

function getDate() {
    var date = new Date();
    var year = date.getFullYear();
    var month = String(date.getMonth() + 1).padStart(2, '0');
    var day = String(date.getDate()).padStart(2, '0');
    return year + '.' + month + '.' + day;
}
