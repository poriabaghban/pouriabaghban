(function(){
  function isAdminChangePath(path){
    // match /admin/<app>/<model>/<pk>/change/
    return /\/admin\/[\w-]+\/[\w-]+\/[0-9]+\/change\/?$/.test(path);
  }

  function buildButton(text, cls, onClick){
    var a = document.createElement('a');
    a.className = cls + ' button';
    a.style.marginRight = '6px';
    a.textContent = text;
    if(onClick) a.addEventListener('click', onClick);
    return a;
  }

  function insertButtons(){
    if(!isAdminChangePath(window.location.pathname)) return;
    var parts = window.location.pathname.split('/').filter(Boolean); // ['admin','app','model','pk','change']
    if(parts.length < 5) return;
    var app = parts[1], model = parts[2], pk = parts[3];
    var base = '/admin/' + app + '/' + model + '/';
    var editUrl = base + pk + '/change/';
    var deleteUrl = base + pk + '/delete/';

    // find top and bottom submit-row containers
    var top = document.querySelector('.submit-row');
    var bottom = document.querySelector('.submit-row:last-of-type');
    if(!top && !bottom) return;

    var makeSave = function(){
      var btn = document.createElement('button');
      btn.type = 'submit';
      btn.name = '_save';
      btn.className = 'default';
      btn.style.marginRight = '6px';
      btn.textContent = 'ذخیره';
      return btn;
    };

    var makeEdit = function(){
      var a = document.createElement('a');
      a.href = editUrl;
      a.className = 'button';
      a.style.marginRight = '6px';
      a.textContent = 'ویرایش';
      return a;
    };

    var makeDelete = function(){
      var a = document.createElement('a');
      a.href = deleteUrl;
      a.className = 'deletelink button';
      a.style.background = '#dc3545';
      a.style.borderColor = '#dc3545';
      a.style.color = '#fff';
      a.style.marginRight = '6px';
      a.textContent = 'حذف';
      a.addEventListener('click', function(e){
        if(!confirm('آیا مطمئن هستید که می‌خواهید این مورد را حذف کنید؟')){
          e.preventDefault();
        }
      });
      return a;
    };

    try{
      [top, bottom].forEach(function(container){
        if(!container) return;
        // avoid duplicate insertion
        if(container.querySelector('.admin-extra-buttons')) return;
        var wrapper = document.createElement('div');
        wrapper.className = 'admin-extra-buttons';
        wrapper.style.display = 'inline-block';
        wrapper.style.marginLeft = '12px';

        // Edit (only if not add view)
        wrapper.appendChild(makeEdit());
        wrapper.appendChild(makeDelete());
        wrapper.appendChild(makeSave());

        container.appendChild(wrapper);
      });
    }catch(e){
      // ignore
    }
  }

  if(document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', insertButtons);
  } else {
    insertButtons();
  }
})();
