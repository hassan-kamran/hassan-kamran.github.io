// Image links still work when JavaScript is unavailable.
const galleryLinks = document.querySelectorAll('.gallery-link');
if (galleryLinks.length && typeof HTMLDialogElement !== 'undefined') {
  const dialog = document.createElement('dialog');
  dialog.className = 'lightbox';
  dialog.setAttribute('aria-label', 'Gallery photograph');
  const close = document.createElement('button');
  close.type = 'button';
  close.textContent = 'Close ×';
  const photo = document.createElement('img');
  const caption = document.createElement('p');
  dialog.append(close, photo, caption);
  document.body.append(dialog);
  close.addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });
  galleryLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      photo.src = link.href;
      photo.alt = link.querySelector('img').alt;
      caption.textContent = link.closest('figure').querySelector('figcaption').innerText;
      dialog.showModal();
    });
  });
}
