class FileUploader {
  constructor() {
    this.selectedFiles = [];
    this.maxFiles = 5;
    this.results = [];
    this.currentImageIndex = 0;
    this.touchStartX = 0;
    this.touchEndX = 0;
    this.touchStartY = 0;
    this.touchEndY = 0;

    this.fileInput = document.getElementById("fileInput");
    this.addBtn = document.getElementById("addBtn");
    this.uploadBtn = document.getElementById("uploadBtn");
    this.infoBlocks = document.getElementById("infoBlocks");
    this.fileList = document.getElementById("fileList");
    this.fileCount = document.getElementById("fileCount");
    this.uploadSection = document.getElementById("uploadSection");
    this.uploadDropArea = this.uploadSection.querySelector(".upload-drop-area");
    this.resultsSection = document.getElementById("resultsSection");
    this.imageGrid = document.getElementById("imageGrid");
    this.modal = document.getElementById("imageModal");
    this.modalImage = document.getElementById("modalImage");
    this.modalSimilarity = document.getElementById("modalSimilarity");
    this.modalDownload = document.getElementById("modalDownload");
    this.resultsHeading = this.resultsSection.querySelector("h2");
    this.sortBy = document.getElementById("sortBy");

    this.init();
  }

  init() {
    this.addBtn.addEventListener("click", () => this.fileInput.click());
    this.fileInput.addEventListener("change", (e) => this.handleFileSelect(e));
    this.uploadBtn.addEventListener("click", () => this.uploadFiles());
    this.sortBy.addEventListener("change", () => this.sortResults());

    // Drag and drop functionality - only on uploadDropArea
    this.uploadDropArea.addEventListener("dragenter", (e) =>
      this.handleDragEnter(e)
    );
    this.uploadDropArea.addEventListener("dragover", (e) =>
      this.handleDragOver(e)
    );
    this.uploadDropArea.addEventListener("drop", (e) => this.handleDrop(e));
    this.uploadDropArea.addEventListener("dragleave", (e) =>
      this.handleDragLeave(e)
    );

    // Modal functionality
    this.initModal();
  }

  handleDragEnter(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  handleDragOver(e) {
    e.preventDefault();
    e.stopPropagation();
    this.uploadDropArea.classList.add("dragover");
  }

  handleDragLeave(e) {
    e.stopPropagation();
    // Only remove dragover class if we're leaving the drop area itself, not a child
    if (e.target === this.uploadDropArea) {
      this.uploadDropArea.classList.remove("dragover");
    }
  }

  handleDrop(e) {
    e.preventDefault();
    e.stopPropagation();
    this.uploadDropArea.classList.remove("dragover");
    const files = Array.from(e.dataTransfer.files);
    this.addFiles(files);
  }

  handleFileSelect(e) {
    const files = Array.from(e.target.files);
    this.addFiles(files);
    e.target.value = ""; // Reset input
  }

  addFiles(files) {
    const imageFiles = files.filter((file) => file.type.startsWith("image/"));

    if (imageFiles.length !== files.length) {
      notifications.error(getText("only_images_allowed"));
    }

    const availableSlots = this.maxFiles - this.selectedFiles.length;

    if (imageFiles.length > availableSlots) {
      notifications.error(getText("max_files", availableSlots, this.maxFiles));
      return;
    }

    imageFiles.forEach((file) => {
      if (
        !this.selectedFiles.some(
          (f) => f.name === file.name && f.size === file.size
        )
      ) {
        this.selectedFiles.push(file);
      }
    });

    this.updateUI();
  }

  removeFile(index) {
    this.selectedFiles.splice(index, 1);
    this.updateUI();
  }

  updateUI() {
    this.updateFileList();
    this.updateCounter();
    this.updateButtons();
    this.updateLayout();
  }

  updateFileList() {
    this.fileList.innerHTML = "";

    this.selectedFiles.forEach((file, index) => {
      const fileItem = document.createElement("div");
      fileItem.className = "file-item";
      fileItem.innerHTML = `
              <div class="file-info">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${this.formatFileSize(file.size)}</div>
              </div>
              <button class="remove-btn" onclick="uploader.removeFile(${index})"><img src="/static/images/close.svg" alt="Remove"></button>
            `;
      this.fileList.appendChild(fileItem);
    });
  }

  updateCounter() {
    this.fileCount.textContent = this.selectedFiles.length;
  }

  updateButtons() {
    this.addBtn.disabled = this.selectedFiles.length >= this.maxFiles;
    this.uploadBtn.disabled = this.selectedFiles.length === 0;
  }

  updateLayout() {
    if (this.selectedFiles.length === 0) {
      // No files: expand drop area and hide upload button
      this.uploadDropArea.classList.add("full-height");
      this.fileList.classList.add("hidden");
      this.uploadBtn.classList.add("hidden");
      this.infoBlocks.classList.remove("hidden-mobile");
    } else {
      // Files selected: normal size and show upload button
      this.uploadDropArea.classList.remove("full-height");
      this.fileList.classList.remove("hidden");
      this.uploadBtn.classList.remove("hidden");
      this.infoBlocks.classList.add("hidden-mobile");
    }
  }

  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  async uploadFiles() {
    if (this.selectedFiles.length === 0) return;

    // Clear previous results
    this.results = [];
    this.resultsSection.style.display = "none";
    this.imageGrid.innerHTML = "";

    // Show loading state
    this.uploadBtn.disabled = true;
    this.uploadBtn.classList.add("loading");
    this.uploadBtn.innerHTML = `<span class="spinner"></span>${getText(
      "loading"
    )}`;
    this.addBtn.disabled = true;

    const formData = new FormData();
    this.selectedFiles.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch("/", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        console.log("Upload successful:", result);

        // Store results and display them
        if (result.success && result.files && result.files.length > 0) {
          this.results = result.files;
          this.displayResults();

          // Scroll to results section
          this.resultsSection.scrollIntoView({
            behavior: "smooth",
            block: "start",
          });
        } else {
          // No images found
          notifications.warning(getText("no_match"));
          this.results = [];
          this.resultsSection.style.display = "none";
        }

        // Don't clear selected files - allow user to modify and re-upload
        // this.selectedFiles = [];
        // this.updateUI();
      } else {
        const errorText = await response
          .json()
          .then((data) => data.detail || response.statusText);
        throw new Error(errorText);
      }
    } catch (error) {
      notifications.error(error.message || getText("upload_error"));
      console.error("Upload error:", error);
    } finally {
      // Reset button state
      this.uploadBtn.disabled = false;
      this.uploadBtn.classList.remove("loading");
      this.uploadBtn.textContent = getText("upload_btn");
      this.addBtn.disabled = this.selectedFiles.length >= this.maxFiles;
    }
  }

  calculateSimilarity(distance) {
    return Math.round((1 - distance) * 100);
  }

  sortResults() {
    const sortValue = this.sortBy.value;

    if (sortValue === "accuracy") {
      // Sort by distance (lower distance = higher accuracy)
      this.results.sort((a, b) => a.distance - b.distance);
    } else if (sortValue === "filename") {
      // Sort by filename alphabetically
      this.results.sort((a, b) => a.filename.localeCompare(b.filename));
    }

    this.displayResults();
  }

  displayResults() {
    if (this.results.length === 0) {
      this.resultsSection.style.display = "none";
      return;
    }

    this.resultsSection.style.display = "block";
    this.resultsHeading.textContent = `${getText("found_similar")} ${
      this.results.length
    }`;
    this.imageGrid.innerHTML = "";

    this.results.forEach((item, index) => {
      const similarity = this.calculateSimilarity(item.distance);

      const card = document.createElement("div");
      card.className = "image-card";
      card.innerHTML = `
        <img src="${item.resized}" alt="Result ${
        index + 1
      }" data-index="${index}">
        <div class="image-card-info">
          <div class="similarity-score">${item.filename} (${similarity}%)</div>
          <a href="${
            item.original
          }" class="download-btn" download><img src="/static/images/download.svg" alt="Download"></a>
        </div>
      `;

      // Add click event to image for modal preview
      const img = card.querySelector("img");
      img.addEventListener("click", () => this.openModal(index));

      this.imageGrid.appendChild(card);
    });
  }

  initModal() {
    const closeBtn = this.modal.querySelector(".close");
    this.prevBtn = this.modal.querySelector(".modal-nav.prev");
    this.nextBtn = this.modal.querySelector(".modal-nav.next");

    closeBtn.addEventListener("click", () => this.closeModal());
    this.prevBtn.addEventListener("click", () => this.navigateModal(-1));
    this.nextBtn.addEventListener("click", () => this.navigateModal(1));

    // Close modal when clicking outside the image
    this.modal.addEventListener("click", (e) => {
      if (e.target === this.modal) {
        this.closeModal();
      }
    });

    // Keyboard navigation
    document.addEventListener("keydown", (e) => {
      if (this.modal.classList.contains("active")) {
        if (e.key === "ArrowLeft") {
          this.navigateModal(-1);
        } else if (e.key === "ArrowRight") {
          this.navigateModal(1);
        } else if (e.key === "Escape") {
          this.closeModal();
        }
      }
    });

    // Touch/swipe navigation
    this.modal.addEventListener("touchstart", (e) => {
      this.touchStartX = e.changedTouches[0].screenX;
      this.touchStartY = e.changedTouches[0].screenY;
    }, { passive: true });

    this.modal.addEventListener("touchmove", (e) => {
      // Prevent default scrolling behavior while touching the modal
      e.preventDefault();
    }, { passive: false });

    this.modal.addEventListener("touchend", (e) => {
      this.touchEndX = e.changedTouches[0].screenX;
      this.touchEndY = e.changedTouches[0].screenY;
      this.handleSwipe();
    }, { passive: true });
  }

  openModal(index) {
    if (this.results.length === 0) return;

    this.currentImageIndex = index;
    this.updateModalContent();
    this.modal.classList.add("active");
    document.body.classList.add("modal-open");
  }

  closeModal() {
    this.modal.classList.remove("active");
    document.body.classList.remove("modal-open");
  }

  navigateModal(direction) {
    if (this.results.length === 0) return;

    const newIndex = this.currentImageIndex + direction;

    // Stop at boundaries instead of wrapping around
    if (newIndex < 0 || newIndex >= this.results.length) {
      return;
    }

    this.currentImageIndex = newIndex;
    this.updateModalContent();
  }

  handleSwipe() {
    const swipeThreshold = 50; // minimum distance for a swipe
    const diffX = this.touchStartX - this.touchEndX;
    const diffY = this.touchStartY - this.touchEndY;

    // Determine if it's a horizontal or vertical swipe
    if (Math.abs(diffX) > Math.abs(diffY)) {
      // Horizontal swipe
      if (Math.abs(diffX) > swipeThreshold) {
        if (diffX > 0) {
          // Swiped left - go to next image
          this.navigateModal(1);
        } else {
          // Swiped right - go to previous image
          this.navigateModal(-1);
        }
      }
    } else {
      // Vertical swipe
      if (Math.abs(diffY) > swipeThreshold) {
        // Swiped up or down - close modal
        this.closeModal();
      }
    }
  }

  updateModalContent() {
    const currentResult = this.results[this.currentImageIndex];
    const similarity = this.calculateSimilarity(currentResult.distance);

    this.modalImage.src = currentResult.resized;
    this.modalSimilarity.textContent = `${currentResult.filename} (${similarity}%)`;
    this.modalDownload.href = currentResult.original;

    // Hide/show navigation buttons based on position
    if (this.currentImageIndex === 0) {
      this.prevBtn.style.display = "none";
    } else {
      this.prevBtn.style.display = "block";
    }

    if (this.currentImageIndex === this.results.length - 1) {
      this.nextBtn.style.display = "none";
    } else {
      this.nextBtn.style.display = "block";
    }
  }
}
