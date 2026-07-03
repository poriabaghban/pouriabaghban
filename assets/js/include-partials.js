async function includePartial(id, path){
  try{
    const res = await fetch(path, {cache: 'no-store'});
    if(!res.ok){ console.warn('Failed to load partial:', path); return; }
    const html = await res.text();
    const el = document.getElementById(id);
    if(el) el.innerHTML = html;
  } catch(err){ console.error('Error loading partial', path, err); }
}

document.addEventListener('DOMContentLoaded', function(){
  includePartial('site-header','partials/header.html');
  includePartial('site-footer','partials/footer.html');
  // Delegated handler for the up-to-top button so it works after partial injection
  document.addEventListener('click', function(e){
    const up = e.target.closest && e.target.closest('#up-to-top');
    if(!up) return;
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
});
