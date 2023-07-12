var uploadButton = document.getElementById('uploadButton');
var downloadSubtitleButton = document.getElementById("subtitleDLButton");
var deleteButton = null; // 파일 삭제 버튼 변수
var selectedFile = null; // 선택된 파일 변수

// 파일 선택 시 버튼 활성화
document.getElementById('videoInput').addEventListener('change', function() {
  selectedFile = this.files[0];
  updateVideoPreview(selectedFile);
});

// 이벤트 리스너 등록
document.querySelector('form').addEventListener('submit', function(event) {
  event.preventDefault(); // 기본 동작 중지

  var input = document.getElementById('videoInput');
  var file = selectedFile;

  // 업로드 버튼 비활성화
  uploadButton.disabled = true;

  // 로딩 아이콘으로 텍스트 변경
  uploadButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 생성중...';

  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // AJAX 요청 생성
  var csrftoken = getCookie('csrftoken');
  var xhr = new XMLHttpRequest();
  var formData = new FormData();
  formData.append('file', file);

  xhr.open('POST', '/upload/'); // 업로드를 처리할 서버의 엔드포인트 경로
  xhr.setRequestHeader('X-CSRFToken', csrftoken);
  xhr.onload = function() {
    console.log(xhr.status)
    if (xhr.status === 200) {
      console.log("성공")
      // 파일 업로드 성공
      showCustomAlert('파일 업로드 성공');
      // 원하는 함수 실행 코드 작성
      
      // 자막 다운로드 버튼 활성화
      downloadSubtitleButton.style.display = "block";
    } else {
      // 파일 업로드 실패
      showCustomAlert('파일 업로드 실패');
    }
    // 업로드 버튼 원래 상태로 복원
    uploadButton.innerHTML = '자막 생성';
    uploadButton.disabled = false;

    // 파일 선택 상태 초기화
    input.value = '';
    document.getElementById('filePreviewText').innerText = '파일을 선택해주세요.';

    // 삭제 버튼 활성화
    if (deleteButton) {
      deleteButton.disabled = false;
    }

    // 보러가기 버튼 활성화
    var viewVideoButton = document.getElementById("viewVideoButton");
    viewVideoButton.style.display = "block";
    viewVideoButton.onclick = function() {
      showVideoContainer(file);
    };
    
  };

  // AJAX 요청 전송
  xhr.send(formData);
});

// 파일 삭제 버튼 클릭 이벤트 핸들러
function deleteUploadedVideo() {
  var videoPreview = document.getElementById('videoPreview');
  var input = document.getElementById('videoInput');

  // 동영상 프리뷰 삭제
  videoPreview.src = '';
  videoPreview.style.display = 'none';

  // 업로드 버튼 비활성화
  uploadButton.disabled = true;

  // 파일 선택 상태 초기화
  input.value = '';
  document.getElementById('filePreviewText').innerText = '파일을 선택해주세요.';

  // 파일 삭제 버튼 제거
  if (deleteButton) {
    deleteButton.parentNode.removeChild(deleteButton);
    deleteButton = null; // 파일 삭제 버튼 변수 초기화
  }
}

// 커스텀 알림 표시 함수
function showCustomAlert(message) {
  var alertContainer = document.createElement('div');
  alertContainer.className = 'custom-alert';
  alertContainer.textContent = message;

  document.body.appendChild(alertContainer);

  setTimeout(function() {
    alertContainer.remove();
  }, 3000); // 일정 시간 후 알림을 자동으로 사라지게 설정
}

var videoPreviewContainer = document.getElementById('videoPreviewContainer');

// 보러가기 함수
function showVideoContainer(file) {
  var videoModal = document.getElementById("videoModal");
  var modalVideo = document.getElementById("modalVideo");
  var modalSubtitles = document.getElementById("modalSubtitles");

  // 동영상 소스와 자막 소스 설정
  var fileURL = URL.createObjectURL(file);
  modalVideo.src = fileURL;
  
  // 자막 파일 경로 설정
  var subtitleFilename = file.name.split(".")[0];
  var subtitleSrc = "../../media/subtitle/" + subtitleFilename + ".vtt"
  modalSubtitles.src = subtitleSrc
  
  // 모달 표시
  videoModal.style.display = "block";

  // 사용자가 'X'를 클릭하면 모달을 닫음
  var closeModal = document.getElementsByClassName("close")[0];
  closeModal.onclick = function() {
    videoModal.style.display = "none";
    modalVideo.pause();
  };

  // 종 모양 아이콘 색상 변경
  var bellIcon = document.querySelector(".bi-bell-fill");
  if (bellIcon) {
    bellIcon.classList.remove("bi-bell-fill");
    bellIcon.classList.add("bi-bell-fill-red");
  }
}




// 동영상 프리뷰 업데이트 함수
function updateVideoPreview(file) {
  var videoPreview = document.getElementById('videoPreview');

  if (file) {
    var fileURL = URL.createObjectURL(file);
    console.log(fileURL)
    videoPreview.src = fileURL;
    videoPreview.style.display = 'block';
    videoPreview.play(); // 동영상 자동 재생
    videoPreview.muted = true;
    uploadButton.disabled = false;
    document.getElementById('filePreviewText').innerText = file.name;

    // 파일 삭제 버튼이 생성되지 않았을 경우에만 생성
    if (!deleteButton) {
      deleteButton = document.createElement('button');
      deleteButton.className = 'delete-button';
      deleteButton.innerHTML = '<i class="fas fa-times"></i>';
      deleteButton.addEventListener('click', deleteUploadedVideo);
      document.getElementById('filePreviewContainer').appendChild(deleteButton);
    }
  } else {
    videoPreview.src = '';
    videoPreview.style.display = 'none';
    uploadButton.disabled = true;
    document.getElementById('filePreviewText').innerText = '파일을 선택해주세요.';
  }
}
// 자막 다운로드 함수
function downloadSubtitle() {
  if (selectedFile) {
    var subtitleFilename = selectedFile.name.split(".")[0];
    var subtitleDownloadLink = "../../media/subtitle/" + subtitleFilename + ".vtt";
    window.location.href = subtitleDownloadLink;
  }
}

// 자막 다운로드 버튼 클릭 이벤트 핸들러
downloadSubtitleButton.addEventListener("click", function() {
  downloadSubtitle();
});
