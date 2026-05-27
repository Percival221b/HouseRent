"use strict";

document.addEventListener("DOMContentLoaded", () => {
  initFlashClose();
  initSortSelect();
  initImagePreviews();
  initGalleryThumbs();
});

// --- Flash message dismiss ---
function initFlashClose() {
  document.querySelectorAll(".flash-close").forEach((btn) => {
    btn.addEventListener("click", () => {
      btn.parentElement.remove();
    });
  });
}

// --- Sort select: auto-navigate on change ---
function initSortSelect() {
  const select = document.getElementById("sort-select");
  if (!select) return;

  select.addEventListener("change", () => {
    const url = new URL(window.location.href);
    url.searchParams.set("sort_by", select.value);
    url.searchParams.delete("page");
    window.location.href = url.toString();
  });
}

// --- Image upload previews ---
function initImagePreviews() {
  const coverInput = document.getElementById("cover-image-input");
  const coverPreview = document.getElementById("cover-preview");

  if (coverInput && coverPreview) {
    coverInput.addEventListener("change", () => {
      coverPreview.innerHTML = "";
      const file = coverInput.files[0];
      if (file) {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.onload = () => URL.revokeObjectURL(img.src);
        coverPreview.appendChild(img);
      }
    });
  }

  const imagesInput = document.getElementById("images-input");
  const imagesPreview = document.getElementById("images-preview");

  if (imagesInput && imagesPreview) {
    imagesInput.addEventListener("change", () => {
      imagesPreview.innerHTML = "";
      Array.from(imagesInput.files).forEach((file) => {
        const img = document.createElement("img");
        img.src = URL.createObjectURL(file);
        img.onload = () => URL.revokeObjectURL(img.src);
        imagesPreview.appendChild(img);
      });
    });
  }
}

// --- Gallery thumbnail switcher on detail page ---
function initGalleryThumbs() {
  const mainImg = document.getElementById("gallery-main-img");
  if (!mainImg) return;

  const thumbs = document.querySelectorAll(".gallery-thumb");
  thumbs.forEach((btn) => {
    btn.addEventListener("click", () => {
      thumbs.forEach((t) => t.classList.remove("active"));
      btn.classList.add("active");
      mainImg.src = btn.dataset.src;
    });
  });
}
