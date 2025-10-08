class NotificationManager {
  constructor() {
    this.container = null;
    this.notifications = [];
    this.init();
  }

  init() {
    // Create container if it doesn't exist
    this.container = document.getElementById("notificationContainer");
    if (!this.container) {
      this.container = document.createElement("div");
      this.container.id = "notificationContainer";
      this.container.className = "notification-container";
      document.body.appendChild(this.container);
    }
  }

  /**
   * Show a notification
   * @param {string} message - The notification message
   * @param {string} type - The notification type: 'success', 'error', 'info', 'warning'
   * @param {number} duration - Duration in milliseconds (default: 5000)
   */
  show(message, type = "info", duration = 5000) {
    const notification = this.createNotification(message, type, duration);
    this.container.appendChild(notification.element);
    this.notifications.push(notification);

    // Auto-dismiss after duration
    if (duration > 0) {
      notification.timeout = setTimeout(() => {
        this.remove(notification);
      }, duration);
    }

    return notification;
  }

  /**
   * Show a success notification
   * @param {string} message - The notification message
   * @param {number} duration - Duration in milliseconds (default: 5000)
   */
  success(message, duration = 5000) {
    return this.show(message, "success", duration);
  }

  /**
   * Show an error notification
   * @param {string} message - The notification message
   * @param {number} duration - Duration in milliseconds (default: 7000)
   */
  error(message, duration = 7000) {
    return this.show(message, "error", duration);
  }

  /**
   * Show an info notification
   * @param {string} message - The notification message
   * @param {number} duration - Duration in milliseconds (default: 5000)
   */
  info(message, duration = 5000) {
    return this.show(message, "info", duration);
  }

  /**
   * Show a warning notification
   * @param {string} message - The notification message
   * @param {number} duration - Duration in milliseconds (default: 6000)
   */
  warning(message, duration = 6000) {
    return this.show(message, "warning", duration);
  }

  createNotification(message, type, duration) {
    const element = document.createElement("div");
    element.className = `notification ${type}`;

    // Get icon based on type
    const icon = this.getIcon(type);

    element.innerHTML = `
      <div class="notification-icon">${icon}</div>
      <div class="notification-content">${message}</div>
      <button class="notification-close" aria-label="Close notification">×</button>
      ${
        duration > 0
          ? `<div class="notification-progress" style="animation-duration: ${duration}ms"></div>`
          : ""
      }
    `;

    const notification = {
      element,
      type,
      message,
      timeout: null,
    };

    // Close button handler
    const closeBtn = element.querySelector(".notification-close");
    closeBtn.addEventListener("click", () => {
      this.remove(notification);
    });

    return notification;
  }

  getIcon(type) {
    const icons = {
      success: "✓",
      error: "✕",
      info: "ℹ",
      warning: "⚠",
    };
    return icons[type] || icons.info;
  }

  remove(notification) {
    // Clear timeout if exists
    if (notification.timeout) {
      clearTimeout(notification.timeout);
    }

    // Add removing class for animation
    notification.element.classList.add("removing");

    // Remove from DOM after animation
    setTimeout(() => {
      if (notification.element.parentNode) {
        notification.element.parentNode.removeChild(notification.element);
      }

      // Remove from notifications array
      const index = this.notifications.indexOf(notification);
      if (index > -1) {
        this.notifications.splice(index, 1);
      }
    }, 300); // Match animation duration
  }

  /**
   * Remove all notifications
   */
  clear() {
    this.notifications.forEach((notification) => {
      this.remove(notification);
    });
  }
}

// Create global instance
const notifications = new NotificationManager();
