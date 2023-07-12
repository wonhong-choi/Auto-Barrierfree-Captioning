const $ = document.querySelector.bind(document);

const MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024; // 2GB

function handleFileSelect(evt) {
  evt.preventDefault();
  const files = evt.target.files || evt.dataTransfer.files;

  const allowedTypes = ["video/mp4"];
  const filteredFiles = [...files].filter(file => allowedTypes.includes(file.type));

  const oversizedFiles = filteredFiles.filter(file => file.size > MAX_FILE_SIZE);

  if (oversizedFiles.length > 0) {
    showAlert("파일 크기가 너무 큽니다. 최대 크기는 2GB입니다.");
    return;
  }

  if (filteredFiles.length === 0) {
    showAlert("올바른 형식의 영상 파일을 선택해주세요.");
    return;
  }

  showAlert("파일이 성공적으로 업로드되었습니다.");

  const template = filteredFiles.map((file, index) => `
  <link href="../static/assets/vendor/glightbox/css/glightbox.min.css" rel="stylesheet">
    <div class="file file--${index}">
      <div class="name"><span>${file.name}</span></div>
      <div class="progress active"></div>
      <div class="done">
        <a href="${URL.createObjectURL(file)}" target="glightbox">
          <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" version="1.1" x="0px" y="0px" viewBox="0 0 1000 1000">
            <g>
              <path id="path" d="M500,10C229.4,10,10,229.4,10,500c0,270.6,219.4,490,490,490c270.6,0,490-219.4,490-490C990,229.4,770.6,10,500,10z M500,967.7C241.7,967.7,32.3,758.3,32.3,500C32.3,241.7,241.7,32.3,500,32.3c258.3,0,467.7,209.4,467.7,467.7C967.7,758.3,758.3,967.7,500,967.7z M748.4,325L448,623.1L301.6,477.9c-4.4-4.3-11.4-4.3-15.8,0c-4.4,4.3-4.4,11.3,0,15.6l151.2,150c0.5,1.3,1.4,2.6,2.5,3.7c4.4,4.3,11.4,4.3,15.8,0l308.9-306.5c4.4-4.3,4.4-11.3,0-15.6C759.8,320.7,752.7,320.7,748.4,325z"/>
            </g>
          </svg>
        </a>
      </div>
      <button class="delete-btn" data-index="${index}">
        <i class="bi bi-trash"></i>
      </button>
    </div>
  `).join("");

  $("#drop").classList.add("hidden");
  $("footer").classList.add("hasFiles");
  $(".importar").classList.add("active");
  setTimeout(() => {
    $(".list-files").innerHTML = template;
    attachViewButtonListeners();
    attachDeleteButtonListeners();
  }, 1000);

  filteredFiles.forEach((file, index) => {
    const load = 2000 + index * 2000; // Fake load
    setTimeout(() => {
      $(`.file--${index}`).querySelector(".progress").classList.remove("active");
      $(`.file--${index}`).querySelector(".done").classList.add("anim");
    }, load);
  });

  oversizedFiles.forEach((file, index) => {
    $(`.file--${index}`).querySelector(`.file--${index}-alert`).textContent = "파일 크기가 너무 큽니다. 최대 크기는 2GB입니다.";
    $(`.file--${index}`).querySelector(`.file--${index}-alert`).classList.remove("hidden");
  });
}

function showAlert(message) {
  const alertDiv = document.createElement('div');
  alertDiv.classList.add('alert');
  alertDiv.classList.add('alert-danger');
  alertDiv.textContent = message;

  const uploadContainer = document.querySelector('.upload-container');
  uploadContainer.insertAdjacentElement('beforebegin', alertDiv);

  setTimeout(() => {
    alertDiv.remove();
  }, 3000);
}

function attachViewButtonListeners() {
  const viewButtons = document.querySelectorAll(".btn-watch-video");
  viewButtons.forEach(button => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      const index = parseInt(button.dataset.index);
      openVideoPopup(index);
    });
  });
}

function attachDeleteButtonListeners() {
  const deleteButtons = document.querySelectorAll(".delete-btn");
  deleteButtons.forEach(button => {
    button.addEventListener("click", (e) => {
      e.preventDefault();
      const index = parseInt(button.dataset.index);
      deleteFile(index);
    });
  });
}

function deleteFile(index) {
  $(`.file--${index}`).remove();
}

$("#triggerFile").addEventListener("click", (evt) => {
  evt.preventDefault();
  $("input[type=file]").click();
});

$("#drop").ondragleave = (evt) => {
  $("#drop").classList.remove("active");
  evt.preventDefault();
};

$("#drop").ondragover = $("#drop").ondragenter = (evt) => {
  $("#drop").classList.add("active");
  evt.preventDefault();
};

$("#drop").ondrop = (evt) => {
  evt.preventDefault();
  handleFileSelect(evt);
  $("#drop").classList.remove("active");
};

$("input[type=file]").addEventListener("change", (evt) => {
  handleFileSelect(evt);
  $("input[type=file]").value = "";
});

$(".importar").addEventListener("click", () => {
  $(".list-files").innerHTML = "";
  $("footer").classList.remove("hasFiles");
  $(".importar").classList.remove("active");
  setTimeout(() => {
    $("#drop").classList.remove("hidden");
  }, 500);
});

attachViewButtonListeners();
attachDeleteButtonListeners();
