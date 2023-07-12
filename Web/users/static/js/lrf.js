(function() {
  // Login/Signup modal
  function ModalSignin(element) {
    this.element = element;
    this.blocks = this.element.getElementsByClassName('js-signin-modal-block');
    this.switchers = this.element.getElementsByClassName('js-signin-modal-switcher')[0].getElementsByTagName('a');
    this.triggers = document.getElementsByClassName('js-signin-modal-trigger');
    this.activationButtons = document.getElementsByClassName('js-activation-button');
    this.init();
  }

  ModalSignin.prototype.init = function() {
    var self = this;
    // Open modal/switch form
    for (var i = 0; i < this.triggers.length; i++) {
      (function(i) {
        self.triggers[i].addEventListener('click', function(event) {
          if (event.target.hasAttribute('data-signin')) {
            event.preventDefault();
            self.showSigninForm(event.target.getAttribute('data-signin'));
          }
        });
      })(i);
    }

    // Close modal
    this.element.addEventListener('click', function(event) {
      if (hasClass(event.target, 'js-signin-modal') || hasClass(event.target, 'js-close')) {
        event.preventDefault();
        removeClass(self.element, 'cd-signin-modal--is-visible');
      }
    });
    // Close modal when clicking the esc keyboard button
    document.addEventListener('keydown', function(event) {
      (event.which == '27') && removeClass(self.element, 'cd-signin-modal--is-visible');
    });

    // Activation buttons
    for (var i = 0; i < this.activationButtons.length; i++) {
      (function(i) {
        self.activationButtons[i].addEventListener('click', function(event) {
          event.preventDefault();
          // Perform the same action as the 'Sign in' button
          self.showSigninForm('login');
        });
      })(i);
    }
  };

  ModalSignin.prototype.showSigninForm = function(type) {
    // Show modal if not visible
    !hasClass(this.element, 'cd-signin-modal--is-visible') && addClass(this.element, 'cd-signin-modal--is-visible');
    // Show selected form
    for (var i = 0; i < this.blocks.length; i++) {
      this.blocks[i].getAttribute('data-type') == type ? addClass(this.blocks[i], 'cd-signin-modal__block--is-selected') : removeClass(this.blocks[i], 'cd-signin-modal__block--is-selected');
    }
    // Update switcher appearance
    var switcherType = (type == 'signup') ? 'signup' : 'login';
    for (var i = 0; i < this.switchers.length; i++) {
      this.switchers[i].getAttribute('data-type') == switcherType ? addClass(this.switchers[i], 'cd-selected') : removeClass(this.switchers[i], 'cd-selected');
    }
  };

  ModalSignin.prototype.toggleError = function(input, bool) {
    // Used to show error messages in the form
    toggleClass(input, 'cd-signin-modal__input--has-error', bool);
    toggleClass(input.nextElementSibling, 'cd-signin-modal__error--is-visible', bool);
  };

  ModalSignin.prototype.validateSignupForm = function() {
    var signupForm = this.element.querySelector('.js-signin-modal-block[data-type="signup"] form');
    var usernameInput = signupForm.querySelector('#signup-username');
    var usernameErrorSpan = usernameInput.nextElementSibling;
    var passwordInput = signupForm.querySelector('#signup-password');
    var rePasswordInput = signupForm.querySelector('#signup-re-password');
    var passwordErrorSpan = passwordInput.nextElementSibling;
    var rePasswordErrorSpan = rePasswordInput.nextElementSibling;
    var emailInput = signupForm.querySelector('#signup-email');
    var emailErrorSpan = emailInput.nextElementSibling;

    if (passwordInput.value.trim() !== rePasswordInput.value.trim()) {
      toggleClass(passwordInput, 'cd-signin-modal__input--has-error', true);
      toggleClass(rePasswordInput, 'cd-signin-modal__input--has-error', true);
      toggleClass(passwordErrorSpan, 'cd-signin-modal__error--is-visible', true);
      toggleClass(rePasswordErrorSpan, 'cd-signin-modal__error--is-visible', true);
    } else {
      toggleClass(passwordInput, 'cd-signin-modal__input--has-error', false);
      toggleClass(rePasswordInput, 'cd-signin-modal__input--has-error', false);
      toggleClass(passwordErrorSpan, 'cd-signin-modal__error--is-visible', false);
      toggleClass(rePasswordErrorSpan, 'cd-signin-modal__error--is-visible', false);
    }

    var email = emailInput.value.trim();
    if (email === '') {
      toggleClass(emailInput, 'cd-signin-modal__input--has-error', true);
      toggleClass(emailErrorSpan, 'cd-signin-modal__error--is-visible', true);
      emailErrorSpan.textContent = '이메일을 입력해주세요';
    } else if (!isValidEmail(email)) {
      toggleClass(emailInput, 'cd-signin-modal__input--has-error', true);
      toggleClass(emailErrorSpan, 'cd-signin-modal__error--is-visible', true);
      emailErrorSpan.textContent = '올바른 이메일 형식이 아닙니다';
    } else {
      toggleClass(emailInput, 'cd-signin-modal__input--has-error', false);
      toggleClass(emailErrorSpan, 'cd-signin-modal__error--is-visible', false);
      emailErrorSpan.textContent = '';
    }

    var username = usernameInput.value.trim();
    if (username.length < 6) {
      toggleClass(usernameInput, 'cd-signin-modal__input--has-error', true);
      toggleClass(usernameErrorSpan, 'cd-signin-modal__error--is-visible', true);
      usernameErrorSpan.textContent = '아이디는 최소 6자 이상이어야 합니다';
    } else {
      toggleClass(usernameInput, 'cd-signin-modal__input--has-error', false);
      toggleClass(usernameErrorSpan, 'cd-signin-modal__error--is-visible', false);
      usernameErrorSpan.textContent = '';
    }
  };

  var signinModal = document.getElementsByClassName('js-signin-modal')[0];
  if (signinModal) {
    var modalInstance = new ModalSignin(signinModal);
    modalInstance.element.addEventListener('input', function(event) {
      var target = event.target;
      if (target.id === 'signup-password' || target.id === 'signup-re-password' || target.id === 'signup-email' || target.id === 'signup-username') {
        modalInstance.validateSignupForm();
      }
    });
  }

  // Class manipulations - needed if classList is not supported
  function hasClass(el, className) {
    if (el.classList) return el.classList.contains(className);
    else return !!el.className.match(new RegExp('(\\s|^)' + className + '(\\s|$)'));
  }
  function addClass(el, className) {
    var classList = className.split(' ');
    if (el.classList) el.classList.add(classList[0]);
    else if (!hasClass(el, classList[0])) el.className += ' ' + classList[0];
    if (classList.length > 1) addClass(el, classList.slice(1).join(' '));
  }
  function removeClass(el, className) {
    var classList = className.split(' ');
    if (el.classList) el.classList.remove(classList[0]);
    else if (hasClass(el, classList[0])) {
      var reg = new RegExp('(\\s|^)' + classList[0] + '(\\s|$)');
      el.className = el.className.replace(reg, ' ');
    }
    if (classList.length > 1) removeClass(el, classList.slice(1).join(' '));
  }
  function toggleClass(el, className, bool) {
    if (bool) addClass(el, className);
    else removeClass(el, className);
  }

  // 이메일 형식 검사 함수
  function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }
})();

$(document).ready(function() {
  $(".js-logout-button").click(function(e) {
    e.preventDefault();
    $("#logoutModal").show();
  });
  $(".btn-cancel").click(function() {
    $("#logoutModal").hide();
  });

  // 이메일 확인 모달 열기
  var signupButton = document.getElementById('signupButton');
  if (signupButton) {
    signupButton.addEventListener('click', function () {
      // 3초 후에 이메일 확인 모달 열기
      setTimeout(function () {
        var modal = document.getElementById('emailConfirmationModal');
        modal.style.display = 'block';
      }, 1000);
    });
  }

  // 이메일 확인 모달 확인 버튼 클릭 이벤트 처리
  var btnOk = document.querySelector('.btn-ok');
  if (btnOk) {
    btnOk.addEventListener('click', function () {
      // 이메일 확인 모달 닫기
      var modal = document.getElementById('emailConfirmationModal');
      modal.style.display = 'none';
      // 계정 만들기 버튼 작동
      var signupForm = document.getElementById('signupForm');
      signupForm.submit();
    });
  }

  // 이메일 확인 모달 닫기 버튼 클릭 이벤트 처리
  var closeBtn = document.querySelector('.close');
  if (closeBtn) {
    closeBtn.addEventListener('click', function () {
      // 이메일 확인 모달 닫기
      var modal = document.getElementById('emailConfirmationModal');
      modal.style.display = 'none';
    });
  }
});
