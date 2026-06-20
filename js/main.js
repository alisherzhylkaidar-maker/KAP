/* ==========================================================================
   Kazakhstan Entrepreneurs Association — main.js
   Handles: header scroll state, mobile nav, scroll reveal, counters,
   department modals, AI assistant demo, member-area demo, forms.
   ========================================================================== */
(function(){
  "use strict";

  /* ---------- Header scroll state ---------- */
  var header = document.querySelector('.site-header');
  function onScroll(){
    if(window.scrollY > 30){ header.classList.add('scrolled'); }
    else{ header.classList.remove('scrolled'); }
  }
  window.addEventListener('scroll', onScroll, {passive:true});
  onScroll();

  /* ---------- Mobile nav ---------- */
  var burger = document.querySelector('.burger');
  var mobileNav = document.querySelector('.mobile-nav');
  if(burger && mobileNav){
    burger.addEventListener('click', function(){ mobileNav.classList.toggle('open'); });
    mobileNav.querySelectorAll('a').forEach(function(a){
      a.addEventListener('click', function(){ mobileNav.classList.remove('open'); });
    });
  }

  /* ---------- Scroll reveal ---------- */
  var revealEls = document.querySelectorAll('.reveal');
  if('IntersectionObserver' in window){
    var io = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          entry.target.classList.add('in');
          io.unobserve(entry.target);
        }
      });
    }, {threshold:0.15});
    revealEls.forEach(function(el, i){
      el.style.setProperty('--i', i % 8);
      io.observe(el);
    });
  } else {
    revealEls.forEach(function(el){ el.classList.add('in'); });
  }
  /* Failsafe: guarantee all content is visible shortly after load, no matter what */
  setTimeout(function(){
    document.querySelectorAll('.reveal:not(.in)').forEach(function(el){ el.classList.add('in'); });
  }, 4000);

  /* ---------- Animated counters ---------- */
  var counters = document.querySelectorAll('[data-count]');
  function animateCounter(el){
    var raw = el.getAttribute('data-count');
    var match = raw.match(/[\d.]+/);
    if(!match){ return; }
    var target = parseFloat(match[0]);
    var prefix = raw.slice(0, match.index);
    var suffix = raw.slice(match.index + match[0].length);
    var dur = 1400, start = null;
    function step(ts){
      if(!start){ start = ts; }
      var progress = Math.min((ts - start) / dur, 1);
      var eased = 1 - Math.pow(1 - progress, 3);
      var value = (target * eased);
      el.textContent = prefix + (target % 1 === 0 ? Math.round(value) : value.toFixed(1)) + suffix;
      if(progress < 1){ requestAnimationFrame(step); }
    }
    requestAnimationFrame(step);
  }
  if('IntersectionObserver' in window){
    var cio = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){ animateCounter(entry.target); cio.unobserve(entry.target); }
      });
    }, {threshold:0.5});
    counters.forEach(function(el){ cio.observe(el); });
  }

  /* ---------- Department modals ---------- */
  var deptCards = document.querySelectorAll('[data-dept-trigger]');
  deptCards.forEach(function(card){
    card.addEventListener('click', function(){
      var id = card.getAttribute('data-dept-trigger');
      var modal = document.getElementById('modal-' + id);
      if(modal){ openModal(modal); }
    });
  });
  function openModal(modal){
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeModal(modal){
    modal.classList.remove('open');
    document.body.style.overflow = '';
  }
  document.querySelectorAll('.modal-overlay').forEach(function(overlay){
    overlay.addEventListener('click', function(e){
      if(e.target === overlay){ closeModal(overlay); }
    });
    var closeBtn = overlay.querySelector('.modal-close');
    if(closeBtn){ closeBtn.addEventListener('click', function(){ closeModal(overlay); }); }
  });
  document.addEventListener('keydown', function(e){
    if(e.key === 'Escape'){
      document.querySelectorAll('.modal-overlay.open').forEach(closeModal);
    }
  });

  /* ---------- Generic toast ---------- */
  var toast = document.getElementById('toast');
  function showToast(msg){
    if(!toast){ return; }
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(function(){ toast.classList.remove('show'); }, 3200);
  }

  /* ---------- Mock form submissions (no backend wired yet) ---------- */
  document.querySelectorAll('form[data-mock-form]').forEach(function(form){
    form.addEventListener('submit', function(e){
      e.preventDefault();
      var successMsg = form.getAttribute('data-success') || 'Done';
      showToast(successMsg);
      form.reset();
    });
  });

  /* ---------- AI assistant demo chat ---------- */
  var aiForm = document.getElementById('ai-chat-form');
  if(aiForm){
    var aiInput = document.getElementById('ai-chat-input');
    var aiBody = document.getElementById('ai-chat-body');
    var demoReply = aiForm.getAttribute('data-demo-reply') || '...';
    aiForm.addEventListener('submit', function(e){
      e.preventDefault();
      var val = aiInput.value.trim();
      if(!val){ return; }
      appendBubble(val, 'user');
      aiInput.value = '';
      setTimeout(function(){ appendBubble(demoReply, 'bot'); }, 500);
    });
    function appendBubble(text, who){
      var div = document.createElement('div');
      div.className = 'chat-bubble ' + who;
      div.textContent = text;
      aiBody.appendChild(div);
      aiBody.scrollTop = aiBody.scrollHeight;
    }
  }

  /* ---------- Member area demo (localStorage-based, client only) ---------- */
  var authTabs = document.querySelectorAll('.auth-tab');
  var loginForm = document.getElementById('login-form');
  var registerForm = document.getElementById('register-form');
  authTabs.forEach(function(tab){
    tab.addEventListener('click', function(){
      authTabs.forEach(function(t){ t.classList.remove('active'); });
      tab.classList.add('active');
      var target = tab.getAttribute('data-tab');
      if(loginForm && registerForm){
        loginForm.style.display = target === 'login' ? 'flex' : 'none';
        registerForm.style.display = target === 'register' ? 'flex' : 'none';
      }
    });
  });

  var dashboard = document.getElementById('cabinet-dashboard');
  var formsPanel = document.getElementById('cabinet-forms');
  var logoutBtn = document.getElementById('cabinet-logout');
  var nameSpan = document.getElementById('cabinet-username');

  function setSession(name){
    try{ window.localStorage.setItem('kea_demo_session', name); }catch(err){}
  }
  function getSession(){
    try{ return window.localStorage.getItem('kea_demo_session'); }catch(err){ return null; }
  }
  function clearSession(){
    try{ window.localStorage.removeItem('kea_demo_session'); }catch(err){}
  }
  function showDashboard(name){
    if(dashboard && formsPanel){
      formsPanel.style.display = 'none';
      dashboard.classList.add('show');
      if(nameSpan){ nameSpan.textContent = name; }
    }
  }
  function showAuth(){
    if(dashboard && formsPanel){
      dashboard.classList.remove('show');
      formsPanel.style.display = '';
    }
  }
  var existing = getSession();
  if(existing){ showDashboard(existing); }

  if(loginForm){
    loginForm.addEventListener('submit', function(e){
      e.preventDefault();
      var email = loginForm.querySelector('input[type="email"]');
      var name = email && email.value ? email.value.split('@')[0] : 'Member';
      setSession(name);
      showDashboard(name);
    });
  }
  if(registerForm){
    registerForm.addEventListener('submit', function(e){
      e.preventDefault();
      var name = registerForm.querySelector('input[name="name"]');
      var val = name && name.value ? name.value : 'Member';
      setSession(val);
      showDashboard(val);
    });
  }
  if(logoutBtn){
    logoutBtn.addEventListener('click', function(){
      clearSession();
      showAuth();
    });
  }

  /* ---------- Language auto-detect (first visit only, root redirect handles this; here just persist choice) ---------- */
  document.querySelectorAll('[data-lang-link]').forEach(function(link){
    link.addEventListener('click', function(){
      try{ window.localStorage.setItem('kea_lang', link.getAttribute('data-lang-link')); }catch(err){}
    });
  });

})();
