// Language 탭 변경 이벤트 처리
const languageSelection = document.querySelector('.language-selection');
const languageButtons = languageSelection.querySelectorAll('input[type="radio"]');
const dropdownButton = document.getElementById('dropdownMenuButton');
const tableRows = document.querySelectorAll('#post-table tbody tr');

languageSelection.addEventListener('click', function(event) {
  const target = event.target;
  if (target.matches('input[type="radio"]')) {
    const language = target.getAttribute('data-language');
    showLanguageTab(language);
  }
});

function showLanguageTab(language) {
  for (let i = 0; i < languageButtons.length; i++) {
    const button = languageButtons[i];
    const buttonLanguage = button.getAttribute('data-language');

    if (buttonLanguage === language) {
      button.checked = true;
    }
  }

  for (let j = 0; j < tableRows.length; j++) {
    const row = tableRows[j];
    const rowLanguage = row.querySelector('td:last-child').textContent.trim();
    const tableHeader = document.getElementById('post-table').tHead.rows[0];

    if (language === 'none' || rowLanguage === language) {
      row.style.display = '';
      tableHeader.style.display = ''; // 테이블 헤더 표시
    } else {
      row.style.display = 'none';
      tableHeader.style.display = ''; // 테이블 헤더 숨김
    }
  }
}


// 초기 전체 탭 표시
showLanguageTab('none');

function searchTable(input) {
  const searchValue = input.value.toLowerCase();
  const table = document.getElementById('post-table');
  const rows = table.getElementsByTagName('tr');

  for (let i = 0; i < rows.length; i++) {
    const titleColumn = rows[i].getElementsByTagName('td')[1];
    const authorColumn = rows[i].getElementsByTagName('td')[2];
    if (titleColumn || authorColumn) {
      const titleText = titleColumn.textContent || titleColumn.innerText;
      const authorText = authorColumn.textContent || authorColumn.innerText;
      const foundTitle = titleText.toLowerCase().indexOf(searchValue) > -1;
      const foundAuthor = authorText.toLowerCase().indexOf(searchValue) > -1;
      const languageSelection = document.querySelector('.language-selection input:checked');
      const selectedLanguage = languageSelection.getAttribute('data-language');
      const rowLanguage = rows[i].querySelector('td:last-child').textContent.trim();
      const isLanguageMatch = selectedLanguage === 'none' || rowLanguage === selectedLanguage;
      const dropdownSelection = dropdownButton.textContent.trim();
      const isDropdownMatch = dropdownSelection === '선택' || dropdownSelection === '제목' && foundTitle || dropdownSelection === '작성자' && foundAuthor;

      if ((foundTitle || foundAuthor) && isLanguageMatch && isDropdownMatch) {
        rows[i].style.display = '';
      } else {
        rows[i].style.display = 'none';
      }
    }
  }
}

function changeDropdown(text) {
  dropdownButton.textContent = text;
}

function sortTable() {
  const table = document.getElementById('post-table');
  const rows = Array.from(table.getElementsByTagName('tr')).slice(1); // Exclude table header row
  const sortButton = document.getElementById('sort-button');
  const sortIcon = sortButton.querySelector('i');
  const isAscending = sortIcon.classList.contains('bi-caret-up-fill');

  rows.sort((a, b) => {
    const countA = parseInt(a.cells[4].textContent, 10);
    const countB = parseInt(b.cells[4].textContent, 10);
    return isAscending ? countA - countB : countB - countA;
  });

  // Remove existing rows from table
  for (let i = rows.length - 1; i >= 0; i--) {
    const row = rows[i];
    row.parentNode.removeChild(row);
  }

  // Insert sorted rows back into table
  for (let i = 0; i < rows.length; i++) {
    table.appendChild(rows[i]);
  }

  // Update sort button icon
  sortIcon.classList.toggle('bi-caret-up-fill');
  sortIcon.classList.toggle('bi-caret-down-fill');
}

