class FileUploader {
  constructor() {
    this.selectedFiles = [];
    this.maxFiles = 5;

    this.fileInput = document.getElementById("fileInput");
    this.addBtn = document.getElementById("addBtn");
    this.uploadBtn = document.getElementById("uploadBtn");
    this.fileList = document.getElementById("fileList");
    this.fileCount = document.getElementById("fileCount");
    this.uploadSection = document.getElementById("uploadSection");
    this.errorMessage = document.getElementById("errorMessage");
    this.successMessage = document.getElementById("successMessage");

    this.init();
  }

  init() {
    this.addBtn.addEventListener("click", () => this.fileInput.click());
    this.fileInput.addEventListener("change", (e) => this.handleFileSelect(e));
    this.uploadBtn.addEventListener("click", () => this.uploadFiles());

    // Drag and drop functionality
    this.uploadSection.addEventListener("dragover", (e) =>
      this.handleDragOver(e)
    );
    this.uploadSection.addEventListener("drop", (e) => this.handleDrop(e));
    this.uploadSection.addEventListener("dragleave", (e) =>
      this.handleDragLeave(e)
    );
  }

  handleDragOver(e) {
    e.preventDefault();
    this.uploadSection.classList.add("dragover");
  }

  handleDragLeave(e) {
    e.preventDefault();
    this.uploadSection.classList.remove("dragover");
  }

  handleDrop(e) {
    e.preventDefault();
    this.uploadSection.classList.remove("dragover");
    const files = Array.from(e.dataTransfer.files);
    this.addFiles(files);
  }

  handleFileSelect(e) {
    const files = Array.from(e.target.files);
    this.addFiles(files);
    e.target.value = ""; // Reset input
  }

  addFiles(files) {
    this.hideMessages();

    const imageFiles = files.filter((file) => file.type.startsWith("image/"));

    if (imageFiles.length !== files.length) {
      this.showError("Only image files are allowed");
    }

    const availableSlots = this.maxFiles - this.selectedFiles.length;

    if (imageFiles.length > availableSlots) {
      this.showError(
        `Can only add ${availableSlots} more files (maximum ${this.maxFiles} files)`
      );
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
              <button class="remove-btn" onclick="uploader.removeFile(${index})">Remove</button>
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

  formatFileSize(bytes) {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  showError(message) {
    this.errorMessage.textContent = message;
    this.errorMessage.style.display = "block";
    this.successMessage.style.display = "none";
  }

  showSuccess(message) {
    this.successMessage.textContent = message;
    this.successMessage.style.display = "block";
    this.errorMessage.style.display = "none";
  }

  hideMessages() {
    this.errorMessage.style.display = "none";
    this.successMessage.style.display = "none";
  }

  async uploadFiles() {
    if (this.selectedFiles.length === 0) return;

    this.uploadBtn.disabled = true;
    this.uploadBtn.textContent = "Uploading...";

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
        this.showSuccess(
          `Successfully uploaded ${this.selectedFiles.length} files`
        );
        this.selectedFiles = [];
        this.updateUI();
      } else {
        const errorText = await response.json().then((data) => data.detail || response.statusText);
        throw new Error(errorText);
      }
    } catch (error) {
      this.showError(error || "An error occurred during upload");
      console.error("Upload error:", error);
    } finally {
      this.uploadBtn.disabled = false;
      this.uploadBtn.textContent = "Upload Files";
    }
  }
}
