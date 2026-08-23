// Sem defer, de propósito: define window.enhanceMermaidDiagrams() sincronamente
// durante o parse, para já existir quando o script inline chamar
// mermaid.run(...).then(enhanceMermaidDiagrams) depois do mermaid.min.js (defer)
// terminar de renderizar os SVGs.
//
// Vanilla JS (sem Alpine) de propósito: os <div class="mermaid"> vêm brutos
// dentro do HTML da aula (apps/courses/seed_data/phaseN.py), sem nenhum
// x-data ao redor — envolver cada um em um componente Alpine exigiria editar
// as 60 aulas de novo. Um único lightbox reaproveitado, injetado em
// document.body na hora, funciona para qualquer diagrama sem tocar no HTML
// da aula.
function enhanceMermaidDiagrams() {
  var diagrams = document.querySelectorAll('.lesson-body .mermaid');
  if (!diagrams.length) return;

  var overlay = document.getElementById('mermaid-lightbox');
  if (!overlay) {
    overlay = document.createElement('div');
    overlay.id = 'mermaid-lightbox';
    overlay.className = 'mermaid-lightbox';
    overlay.innerHTML =
      '<div class="mermaid-lightbox-toolbar">' +
        '<button type="button" data-action="out" aria-label="Diminuir zoom">−</button>' +
        '<button type="button" data-action="reset" aria-label="Redefinir zoom">100%</button>' +
        '<button type="button" data-action="in" aria-label="Aumentar zoom">+</button>' +
        '<button type="button" data-action="close" class="mermaid-lightbox-close" aria-label="Fechar">×</button>' +
      '</div>' +
      '<div class="mermaid-lightbox-stage"><div class="mermaid-lightbox-inner"></div></div>';
    document.body.appendChild(overlay);
  }

  var stage = overlay.querySelector('.mermaid-lightbox-stage');
  var inner = overlay.querySelector('.mermaid-lightbox-inner');
  var resetBtn = overlay.querySelector('[data-action="reset"]');
  var scale = 1, tx = 0, ty = 0;
  var dragging = false, startX = 0, startY = 0, pinchDist = 0;

  function applyTransform() {
    inner.style.transform = 'translate(' + tx + 'px, ' + ty + 'px) scale(' + scale + ')';
    resetBtn.textContent = Math.round(scale * 100) + '%';
  }

  function openWith(svgEl) {
    inner.innerHTML = '';
    inner.appendChild(svgEl.cloneNode(true));
    scale = 1; tx = 0; ty = 0;
    applyTransform();
    overlay.classList.add('is-open');
    document.body.style.overflow = 'hidden';
  }

  function close() {
    overlay.classList.remove('is-open');
    document.body.style.overflow = '';
  }

  function zoomBy(delta) {
    scale = Math.min(4, Math.max(0.5, scale + delta));
    applyTransform();
  }

  overlay.addEventListener('click', function (e) {
    var action = e.target.getAttribute && e.target.getAttribute('data-action');
    if (action === 'close') close();
    else if (action === 'in') zoomBy(0.25);
    else if (action === 'out') zoomBy(-0.25);
    else if (action === 'reset') { scale = 1; tx = 0; ty = 0; applyTransform(); }
    else if (e.target === overlay) close();
  });

  stage.addEventListener('wheel', function (e) {
    e.preventDefault();
    zoomBy(e.deltaY > 0 ? -0.15 : 0.15);
  }, { passive: false });

  function pointFrom(e) { return e.touches ? e.touches[0] : e; }
  function dist(touches) {
    var dx = touches[0].clientX - touches[1].clientX;
    var dy = touches[0].clientY - touches[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }

  stage.addEventListener('mousedown', function (e) {
    dragging = true;
    startX = e.clientX - tx;
    startY = e.clientY - ty;
  });
  window.addEventListener('mousemove', function (e) {
    if (!dragging) return;
    tx = e.clientX - startX;
    ty = e.clientY - startY;
    applyTransform();
  });
  window.addEventListener('mouseup', function () { dragging = false; });

  stage.addEventListener('touchstart', function (e) {
    if (e.touches.length === 2) {
      pinchDist = dist(e.touches);
    } else {
      var p = pointFrom(e);
      dragging = true;
      startX = p.clientX - tx;
      startY = p.clientY - ty;
    }
  }, { passive: true });
  stage.addEventListener('touchmove', function (e) {
    if (e.touches.length === 2) {
      e.preventDefault();
      var d = dist(e.touches);
      zoomBy((d - pinchDist) * 0.01);
      pinchDist = d;
    } else if (dragging) {
      e.preventDefault();
      var p = pointFrom(e);
      tx = p.clientX - startX;
      ty = p.clientY - startY;
      applyTransform();
    }
  }, { passive: false });
  stage.addEventListener('touchend', function () { dragging = false; });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && overlay.classList.contains('is-open')) close();
  });

  diagrams.forEach(function (el) {
    if (el.dataset.zoomReady) return;
    el.dataset.zoomReady = '1';
    el.classList.add('mermaid-zoomable');
    el.setAttribute('role', 'button');
    el.setAttribute('tabindex', '0');
    el.setAttribute('aria-label', 'Ampliar diagrama');

    var hint = document.createElement('span');
    hint.className = 'mermaid-zoom-hint';
    hint.setAttribute('aria-hidden', 'true');
    hint.textContent = '🔍';
    el.appendChild(hint);

    function openThis() {
      var svg = el.querySelector('svg');
      if (svg) openWith(svg);
    }
    el.addEventListener('click', openThis);
    el.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openThis();
      }
    });
  });
}
window.enhanceMermaidDiagrams = enhanceMermaidDiagrams;
