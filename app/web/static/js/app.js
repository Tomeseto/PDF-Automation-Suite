/**
 * PDF Automation Suite — Frontend Application Controller
 * Inspired by iLovePDF. Full offline client handling for all 18 tools.
 */

(function () {
  'use strict';

  // --------------------------------------------------------------------------
  // Tool Definitions Registry (All 18 Features)
  // --------------------------------------------------------------------------
  const TOOLS = {
    // 1. Organize
    'merge': {
      title: 'Merge PDF',
      desc: 'Combine multiple PDFs into a single unified document.',
      category: 'organize',
      endpoint: '/api/organize/merge',
      actionText: 'Merge PDFs',
      multiple: true,
      accept: '.pdf',
      options: []
    },
    'split': {
      title: 'Split PDF',
      desc: 'Separate pages or specific ranges into independent PDF files.',
      category: 'organize',
      endpoint: '/api/organize/split',
      actionText: 'Split PDF',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'ranges',
          label: 'Page Ranges to Split (e.g. 1-2, 3-5):',
          type: 'text',
          placeholder: '1-2, 3-5',
          required: true,
          default: '1-1'
        }
      ]
    },
    'extract': {
      title: 'Extract Pages',
      desc: 'Pull specific pages from your PDF file into a new document.',
      category: 'organize',
      endpoint: '/api/organize/extract',
      actionText: 'Extract Pages',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'pages',
          label: 'Page Numbers to Extract (e.g. 1, 3, 5-7):',
          type: 'text',
          placeholder: '1, 2, 4',
          required: true,
          default: '1'
        }
      ]
    },
    'rotate': {
      title: 'Rotate Pages',
      desc: 'Rotate PDF pages clockwise by 90°, 180°, or 270°.',
      category: 'organize',
      endpoint: '/api/organize/rotate',
      actionText: 'Rotate PDF',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'angle',
          label: 'Rotation Angle:',
          type: 'select',
          options: [
            { label: '90° Clockwise', value: '90' },
            { label: '180° Half Turn', value: '180' },
            { label: '270° (90° Counter-Clockwise)', value: '270' }
          ],
          default: '90'
        },
        {
          id: 'pages',
          label: 'Specific Pages (Optional, leave blank for all pages):',
          type: 'text',
          placeholder: 'e.g. 1, 3 (or blank for all)',
          required: false,
          default: ''
        }
      ]
    },
    'reorder': {
      title: 'Reorder Pages',
      desc: 'Permute and rearrange page ordering in your PDF.',
      category: 'organize',
      endpoint: '/api/organize/reorder',
      actionText: 'Reorder Pages',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'order',
          label: 'New Page Order Permutation (1-indexed, covering all pages):',
          type: 'text',
          placeholder: 'e.g. 3, 1, 2',
          required: true,
          default: '1'
        }
      ]
    },
    'organize-pipeline': {
      title: 'Organize Pipeline',
      desc: 'Chain deletions, rotations, and reorderings in a single pass.',
      category: 'organize',
      endpoint: '/api/organize/pipeline',
      actionText: 'Run Pipeline',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'operations_json',
          label: 'Pipeline Operations (JSON array):',
          type: 'textarea',
          rows: 4,
          placeholder: '[{"action": "rotate", "angle": 90, "pages": [1]}]',
          required: true,
          default: '[{"action": "rotate", "angle": 90, "pages": [1]}]'
        }
      ]
    },

    // 2. Optimize
    'compress': {
      title: 'Compress PDF',
      desc: 'Reduce file size and streamline objects without quality loss.',
      category: 'optimize',
      endpoint: '/api/optimize/compress',
      actionText: 'Compress PDF Now',
      multiple: false,
      accept: '.pdf',
      options: []
    },

    // 3. Convert
    'pdf-to-images': {
      title: 'PDF to Images',
      desc: 'Convert each page of your PDF into high-res PNG or JPEG images.',
      category: 'convert',
      endpoint: '/api/convert/pdf-to-images',
      actionText: 'Convert to Images',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'image_format',
          label: 'Output Image Format:',
          type: 'select',
          options: [
            { label: 'PNG (Lossless High Quality)', value: 'png' },
            { label: 'JPEG (Standard Compressed)', value: 'jpeg' }
          ],
          default: 'png'
        }
      ]
    },
    'images-to-pdf': {
      title: 'Images to PDF',
      desc: 'Convert JPG, PNG, and photo files into a unified PDF document.',
      category: 'convert',
      endpoint: '/api/convert/images-to-pdf',
      actionText: 'Convert Images to PDF',
      multiple: true,
      accept: 'image/png,image/jpeg,image/webp,.png,.jpg,.jpeg',
      options: []
    },
    'scan-to-pdf': {
      title: 'Scan Images to PDF',
      desc: 'Auto-enhance contrast and assemble document photos into a clean PDF.',
      category: 'convert',
      endpoint: '/api/convert/scan-to-pdf',
      actionText: 'Generate Scanned PDF',
      multiple: true,
      accept: 'image/png,image/jpeg,image/webp,.png,.jpg,.jpeg',
      options: [
        {
          id: 'enhance',
          label: 'Enhance Document Contrast (Grayscale Autocontrast):',
          type: 'checkbox',
          default: true
        }
      ]
    },
    'extract-text': {
      title: 'Extract Text',
      desc: 'Extract all textual content from pages and download as a text file.',
      category: 'convert',
      endpoint: '/api/convert/extract-text',
      actionText: 'Extract Text Now',
      multiple: false,
      accept: '.pdf',
      options: []
    },
    'search-pdf': {
      title: 'Search PDF',
      desc: 'Search for text keywords and locate matches with page numbers.',
      category: 'convert',
      endpoint: '/api/convert/search-pdf',
      actionText: 'Search Document',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'query',
          label: 'Search Query / Keyword:',
          type: 'text',
          placeholder: 'Enter word or phrase...',
          required: true,
          default: ''
        },
        {
          id: 'case_sensitive',
          label: 'Match Case Exactly',
          type: 'checkbox',
          default: false
        }
      ]
    },

    // 4. Security
    'password-add': {
      title: 'Protect PDF with Password',
      desc: 'Encrypt your PDF with standard password encryption.',
      category: 'security',
      endpoint: '/api/security/password-add',
      actionText: 'Protect PDF',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'user_password',
          label: 'User Password (required to open document):',
          type: 'password',
          placeholder: 'Enter password...',
          required: true
        },
        {
          id: 'owner_password',
          label: 'Owner / Permission Password (optional):',
          type: 'password',
          placeholder: 'Leave blank to use user password',
          required: false
        }
      ]
    },
    'password-remove': {
      title: 'Unlock / Remove Password',
      desc: 'Decrypt a password-protected PDF to make it freely readable.',
      category: 'security',
      endpoint: '/api/security/password-remove',
      actionText: 'Unlock PDF',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'password',
          label: 'Current PDF Password:',
          type: 'password',
          placeholder: 'Enter existing password...',
          required: true
        }
      ]
    },
    'watermark-add': {
      title: 'Add Watermark',
      desc: 'Stamp custom watermark text onto your PDF pages.',
      category: 'security',
      endpoint: '/api/security/watermark-add',
      actionText: 'Apply Watermark',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'text',
          label: 'Watermark Text:',
          type: 'text',
          placeholder: 'e.g. CONFIDENTIAL',
          required: true,
          default: 'CONFIDENTIAL'
        },
        {
          id: 'position',
          label: 'Watermark Position:',
          type: 'select',
          options: [
            { label: 'Center (Diagonal)', value: 'center' },
            { label: 'Top Left', value: 'top-left' },
            { label: 'Top Right', value: 'top-right' },
            { label: 'Bottom Left', value: 'bottom-left' },
            { label: 'Bottom Right', value: 'bottom-right' }
          ],
          default: 'center'
        },
        {
          id: 'opacity',
          label: 'Opacity Transparency (0.1 - 1.0):',
          type: 'slider',
          min: 0.1,
          max: 1.0,
          step: 0.05,
          default: 0.3
        }
      ]
    },
    'watermark-remove': {
      title: 'Remove Watermark',
      desc: 'Filter and strip watermark text overlays from PDF streams.',
      category: 'security',
      endpoint: '/api/security/watermark-remove',
      actionText: 'Remove Watermark',
      multiple: false,
      accept: '.pdf',
      options: [
        {
          id: 'watermark_text',
          label: 'Specific Watermark Text to Remove (optional):',
          type: 'text',
          placeholder: 'e.g. CONFIDENTIAL (leave blank for auto)',
          required: false,
          default: ''
        }
      ]
    },
    'signature-add': {
      title: 'Add Signature Stamp',
      desc: 'Stamp an image of your signature onto any page at custom X/Y coordinates.',
      category: 'security',
      endpoint: '/api/security/signature-add',
      actionText: 'Stamp Signature',
      multiple: false,
      accept: '.pdf',
      extraFile: {
        id: 'signature_image',
        label: 'Upload Signature Image (PNG with transparency recommended):',
        accept: 'image/png,image/jpeg,.png,.jpg'
      },
      options: [
        {
          id: 'page_number',
          label: 'Target Page Number (1-indexed):',
          type: 'number',
          min: 1,
          default: 1,
          required: true
        },
        {
          id: 'x',
          label: 'X Position (points from bottom-left):',
          type: 'number',
          default: 100,
          required: true
        },
        {
          id: 'y',
          label: 'Y Position (points from bottom-left):',
          type: 'number',
          default: 100,
          required: true
        }
      ]
    },

    // 5. Batch
    'batch-process': {
      title: 'Batch Processing',
      desc: 'Execute operations in bulk across multiple documents simultaneously.',
      category: 'batch',
      endpoint: '/api/batch/process',
      actionText: 'Start Batch Process',
      multiple: true,
      accept: '.pdf',
      options: [
        {
          id: 'operation_name',
          label: 'Batch Operation to Apply:',
          type: 'select',
          options: [
            { label: 'Compress PDFs', value: 'compress' },
            { label: 'Rotate Pages (90°)', value: 'rotate' },
            { label: 'Add Watermark', value: 'watermark_add' },
            { label: 'Remove Watermark', value: 'watermark_remove' },
            { label: 'Add Password Protection', value: 'password_add' },
            { label: 'Remove Password', value: 'password_remove' }
          ],
          default: 'compress'
        },
        {
          id: 'options_json',
          label: 'Additional Options (key=value, or JSON string):',
          type: 'text',
          placeholder: 'e.g. angle=90 or text=CONFIDENTIAL',
          required: false,
          default: ''
        }
      ]
    }
  };

  // --------------------------------------------------------------------------
  // Application State
  // --------------------------------------------------------------------------
  let currentToolKey = null;
  let stagedFiles = [];
  let stagedExtraFile = null;

  // DOM Elements
  const toolCards = document.querySelectorAll('.tool-card');
  const searchInput = document.getElementById('tool-search');
  const toolsCounter = document.getElementById('tools-counter');
  const themeToggleBtn = document.getElementById('btn-theme-toggle');
  const sunIcon = document.getElementById('theme-icon-sun');
  const moonIcon = document.getElementById('theme-icon-moon');

  // Modal Workspace Elements
  const workspaceModal = document.getElementById('workspace-modal');
  const modalCloseBtn = document.getElementById('modal-close');
  const modalCancelBtn = document.getElementById('modal-cancel-btn');
  const modalTitle = document.getElementById('modal-title');
  const modalDesc = document.getElementById('modal-desc');
  const modalIcon = document.getElementById('modal-icon');
  const fileDropzone = document.getElementById('file-dropzone');
  const fileInput = document.getElementById('file-input');
  const dropzoneTitle = document.getElementById('dropzone-title');
  const dropzoneSubtitle = document.getElementById('dropzone-subtitle');
  const stagedFilesList = document.getElementById('staged-files');
  const optionsBox = document.getElementById('options-box');
  const optionsFields = document.getElementById('options-fields');
  const progressContainer = document.getElementById('progress-container');
  const btnSubmit = document.getElementById('btn-submit-action');
  const btnActionText = document.getElementById('btn-action-text');

  // Result Elements
  const modalFormView = document.getElementById('modal-form-view');
  const modalResultView = document.getElementById('modal-result-view');
  const modalFooter = document.getElementById('modal-footer');
  const resultTitle = document.getElementById('result-title');
  const resultMessage = document.getElementById('result-message');
  const btnDownload = document.getElementById('btn-download');
  const btnProcessAnother = document.getElementById('btn-process-another');
  const resultStructuredData = document.getElementById('result-structured-data');

  // Logs Modal Elements
  const logsModal = document.getElementById('logs-modal');
  const btnOpenLogs = document.getElementById('btn-open-logs');
  const logsModalClose = document.getElementById('logs-modal-close');
  const logsTerminal = document.getElementById('logs-terminal');
  const btnRefreshLogs = document.getElementById('btn-refresh-logs');
  const btnClearLogs = document.getElementById('btn-clear-logs');
  const logsCountLabel = document.getElementById('logs-count-label');

  // Toast Container
  const toastContainer = document.getElementById('toast-container');

  // --------------------------------------------------------------------------
  // Helper Utilities
  // --------------------------------------------------------------------------
  function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    let iconSvg = '';
    if (type === 'error') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
    } else if (type === 'success') {
      iconSvg = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"></polyline></svg>';
    }

    toast.innerHTML = `${iconSvg}<span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateY(10px)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4500);
  }

  // --------------------------------------------------------------------------
  // Theme Toggle (Dark / Light)
  // --------------------------------------------------------------------------
  function initTheme() {
    const savedTheme = localStorage.getItem('pdf_suite_theme') || 'dark';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcons(savedTheme);
  }

  function updateThemeIcons(theme) {
    if (theme === 'light') {
      sunIcon.style.display = 'none';
      moonIcon.style.display = 'block';
    } else {
      sunIcon.style.display = 'block';
      moonIcon.style.display = 'none';
    }
  }

  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nextTheme);
    localStorage.setItem('pdf_suite_theme', nextTheme);
    updateThemeIcons(nextTheme);
  });

  // --------------------------------------------------------------------------
  // Search Filtering
  // --------------------------------------------------------------------------
  function filterTools() {
    const query = searchInput.value.toLowerCase().trim();
    let visibleCount = 0;

    toolCards.forEach(card => {
      const toolKey = card.dataset.tool;
      const tool = TOOLS[toolKey];
      if (!tool) return;

      const titleMatch = tool.title.toLowerCase().includes(query);
      const descMatch = tool.desc.toLowerCase().includes(query);
      const keyMatch = toolKey.toLowerCase().includes(query);
      const categoryMatch = tool.category.toLowerCase().includes(query);
      const searchMatches = query === '' || titleMatch || descMatch || keyMatch || categoryMatch;

      if (searchMatches) {
        card.style.display = 'flex';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    toolsCounter.textContent = `${visibleCount} Tools`;
  }

  searchInput.addEventListener('input', filterTools);

  // --------------------------------------------------------------------------
  // Workspace Modal Controller
  // --------------------------------------------------------------------------
  function openToolWorkspace(toolKey) {
    const tool = TOOLS[toolKey];
    if (!tool) return;

    currentToolKey = toolKey;
    stagedFiles = [];
    stagedExtraFile = null;

    // Reset views
    modalFormView.style.display = 'block';
    modalResultView.style.display = 'none';
    modalFooter.style.display = 'flex';
    progressContainer.style.display = 'none';
    resultStructuredData.style.display = 'none';
    resultStructuredData.innerHTML = '';

    modalTitle.textContent = tool.title;
    modalDesc.textContent = tool.desc;
    btnActionText.textContent = tool.actionText;

    // Set Tool Icon
    const cardIconSvg = document.querySelector(`#tool-${toolKey} .card-icon svg`);
    if (cardIconSvg) {
      modalIcon.innerHTML = cardIconSvg.outerHTML;
      modalIcon.style.background = `var(--card-accent-bg, rgba(229, 50, 45, 0.12))`;
      modalIcon.style.color = `var(--card-accent, var(--brand-red))`;
    }

    // Configure Dropzone
    fileInput.multiple = tool.multiple;
    fileInput.accept = tool.accept;
    fileInput.value = '';

    if (tool.accept.includes('image')) {
      dropzoneTitle.textContent = tool.multiple ? 'Drop images here' : 'Drop your image file here';
      dropzoneSubtitle.textContent = 'or click to browse JPG, PNG, or WebP';
    } else {
      dropzoneTitle.textContent = tool.multiple ? 'Drop multiple PDF files here' : 'Drop your PDF file here';
      dropzoneSubtitle.textContent = 'or click to browse from your device';
    }

    renderStagedFiles();
    renderOptions(tool);
    checkSubmitState();

    workspaceModal.classList.add('open');
  }

  function closeWorkspace() {
    workspaceModal.classList.remove('open');
    currentToolKey = null;
    stagedFiles = [];
    stagedExtraFile = null;
  }

  modalCloseBtn.addEventListener('click', closeWorkspace);
  modalCancelBtn.addEventListener('click', closeWorkspace);
  btnProcessAnother.addEventListener('click', () => {
    if (currentToolKey) {
      openToolWorkspace(currentToolKey);
    }
  });

  // Clicking outside modal container closes it
  workspaceModal.addEventListener('click', (e) => {
    if (e.target === workspaceModal) closeWorkspace();
  });

  // Tool Card Click triggers Workspace
  toolCards.forEach(card => {
    card.addEventListener('click', () => {
      openToolWorkspace(card.dataset.tool);
    });
  });

  // --------------------------------------------------------------------------
  // File Staging & Drag and Drop
  // --------------------------------------------------------------------------
  fileDropzone.addEventListener('click', () => fileInput.click());

  fileInput.addEventListener('change', (e) => {
    handleIncomingFiles(e.target.files);
  });

  ['dragenter', 'dragover'].forEach(evt => {
    fileDropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      fileDropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(evt => {
    fileDropzone.addEventListener(evt, (e) => {
      e.preventDefault();
      e.stopPropagation();
      fileDropzone.classList.remove('dragover');
    });
  });

  fileDropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    if (dt && dt.files && dt.files.length) {
      handleIncomingFiles(dt.files);
    }
  });

  function handleIncomingFiles(fileList) {
    const tool = TOOLS[currentToolKey];
    if (!tool) return;

    const filesArray = Array.from(fileList);
    if (!tool.multiple) {
      // Single file mode replaces any previously selected file
      stagedFiles = [filesArray[0]];
    } else {
      // Multi file mode appends
      stagedFiles.push(...filesArray);
    }

    renderStagedFiles();
    checkSubmitState();
  }

  function renderStagedFiles() {
    stagedFilesList.innerHTML = '';
    if (stagedFiles.length === 0) return;

    stagedFiles.forEach((file, idx) => {
      const chip = document.createElement('div');
      chip.className = 'file-chip';
      chip.innerHTML = `
        <div class="file-chip-left">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
          </svg>
          <div>
            <div class="file-name" title="${file.name}">${file.name}</div>
            <div class="file-size">${formatBytes(file.size)}</div>
          </div>
        </div>
        <button class="file-remove-btn" data-index="${idx}" title="Remove file">&times;</button>
      `;

      chip.querySelector('.file-remove-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        stagedFiles.splice(idx, 1);
        renderStagedFiles();
        checkSubmitState();
      });

      stagedFilesList.appendChild(chip);
    });
  }

  // --------------------------------------------------------------------------
  // Options Renderer
  // --------------------------------------------------------------------------
  function renderOptions(tool) {
    optionsFields.innerHTML = '';
    const hasOptions = (tool.options && tool.options.length > 0) || tool.extraFile;

    if (!hasOptions) {
      optionsBox.style.display = 'none';
      return;
    }

    optionsBox.style.display = 'block';

    // Render extra file picker if tool requires it (e.g. signature image)
    if (tool.extraFile) {
      const grp = document.createElement('div');
      grp.className = 'form-group';
      grp.innerHTML = `
        <label class="form-label">${tool.extraFile.label}</label>
        <input type="file" id="extra-file-input" class="form-input" accept="${tool.extraFile.accept}">
        <div id="extra-file-status" style="font-size: 0.8rem; color: var(--text-muted); margin-top: 0.3rem;"></div>
      `;
      const extraInput = grp.querySelector('#extra-file-input');
      const extraStatus = grp.querySelector('#extra-file-status');
      extraInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files.length) {
          stagedExtraFile = e.target.files[0];
          extraStatus.textContent = `Selected: ${stagedExtraFile.name} (${formatBytes(stagedExtraFile.size)})`;
        } else {
          stagedExtraFile = null;
          extraStatus.textContent = '';
        }
        checkSubmitState();
      });
      optionsFields.appendChild(grp);
    }

    // Render tool options
    tool.options.forEach(opt => {
      const grp = document.createElement('div');
      grp.className = 'form-group';

      if (opt.type === 'text' || opt.type === 'number') {
        grp.innerHTML = `
          <label class="form-label" for="opt-${opt.id}">${opt.label}</label>
          <input type="${opt.type}" id="opt-${opt.id}" class="form-input" placeholder="${opt.placeholder || ''}" value="${opt.default || ''}" ${opt.min !== undefined ? `min="${opt.min}"` : ''}>
        `;
      } else if (opt.type === 'password') {
        grp.innerHTML = `
          <label class="form-label" for="opt-${opt.id}">${opt.label}</label>
          <div class="password-field-wrapper">
            <input type="password" id="opt-${opt.id}" class="form-input" placeholder="${opt.placeholder || ''}">
            <button type="button" class="password-toggle-btn" data-target="opt-${opt.id}" title="Toggle Password Visibility">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
              </svg>
            </button>
          </div>
        `;
        const toggleBtn = grp.querySelector('.password-toggle-btn');
        toggleBtn.addEventListener('click', () => {
          const inputEl = document.getElementById(toggleBtn.dataset.target);
          if (inputEl.type === 'password') {
            inputEl.type = 'text';
            toggleBtn.style.color = 'var(--brand-red)';
          } else {
            inputEl.type = 'password';
            toggleBtn.style.color = 'var(--text-muted)';
          }
        });
      } else if (opt.type === 'select') {
        const optionsHtml = opt.options.map(o => `<option value="${o.value}" ${o.value === opt.default ? 'selected' : ''}>${o.label}</option>`).join('');
        grp.innerHTML = `
          <label class="form-label" for="opt-${opt.id}">${opt.label}</label>
          <select id="opt-${opt.id}" class="form-select">${optionsHtml}</select>
        `;
      } else if (opt.type === 'slider') {
        grp.innerHTML = `
          <label class="form-label">${opt.label}</label>
          <div class="slider-container">
            <input type="range" id="opt-${opt.id}" class="slider-input" min="${opt.min}" max="${opt.max}" step="${opt.step}" value="${opt.default}">
            <span class="slider-val" id="val-${opt.id}">${opt.default}</span>
          </div>
        `;
        const slider = grp.querySelector(`#opt-${opt.id}`);
        const valSpan = grp.querySelector(`#val-${opt.id}`);
        slider.addEventListener('input', () => { valSpan.textContent = slider.value; });
      } else if (opt.type === 'checkbox') {
        grp.innerHTML = `
          <label style="display: flex; align-items: center; gap: 0.6rem; cursor: pointer; font-size: 0.88rem; font-weight: 600;">
            <input type="checkbox" id="opt-${opt.id}" ${opt.default ? 'checked' : ''} style="width: 18px; height: 18px; accent-color: var(--brand-red);">
            <span>${opt.label}</span>
          </label>
        `;
      } else if (opt.type === 'textarea') {
        grp.innerHTML = `
          <label class="form-label" for="opt-${opt.id}">${opt.label}</label>
          <textarea id="opt-${opt.id}" class="form-textarea" rows="${opt.rows || 3}" placeholder="${opt.placeholder || ''}">${opt.default || ''}</textarea>
        `;
      }

      optionsFields.appendChild(grp);
    });
  }

  function checkSubmitState() {
    const tool = TOOLS[currentToolKey];
    if (!tool) {
      btnSubmit.disabled = true;
      return;
    }

    let valid = true;
    if (tool.multiple) {
      if (currentToolKey === 'merge' && stagedFiles.length < 2) valid = false;
      else if (stagedFiles.length === 0) valid = false;
    } else {
      if (stagedFiles.length === 0) valid = false;
    }

    if (tool.extraFile && !stagedExtraFile) {
      valid = false;
    }

    btnSubmit.disabled = !valid;
  }

  // --------------------------------------------------------------------------
  // Execute Operation (Submitting to FastAPI)
  // --------------------------------------------------------------------------
  btnSubmit.addEventListener('click', async () => {
    const tool = TOOLS[currentToolKey];
    if (!tool || stagedFiles.length === 0) return;

    const formData = new FormData();

    // Attach Files
    if (tool.multiple) {
      stagedFiles.forEach(f => formData.append('files', f));
    } else {
      formData.append('file', stagedFiles[0]);
    }

    // Attach Extra File if needed
    if (tool.extraFile && stagedExtraFile) {
      formData.append(tool.extraFile.id, stagedExtraFile);
    }

    // Attach Options
    if (tool.options) {
      for (const opt of tool.options) {
        const inputEl = document.getElementById(`opt-${opt.id}`);
        if (inputEl) {
          if (opt.type === 'checkbox') {
            formData.append(opt.id, inputEl.checked ? 'true' : 'false');
          } else {
            const val = inputEl.value.trim();
            if (opt.required && !val) {
              showToast(`Please fill in "${opt.label}"`, 'error');
              inputEl.focus();
              return;
            }
            formData.append(opt.id, val);
          }
        }
      }
    }

    // UI Loading State
    btnSubmit.disabled = true;
    progressContainer.style.display = 'block';
    btnActionText.textContent = 'Processing Document...';

    try {
      const response = await fetch(tool.endpoint, {
        method: 'POST',
        body: formData
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.message || 'Operation failed');
      }

      // Success Display
      showToast(data.message || 'Operation succeeded!', 'success');

      modalFormView.style.display = 'none';
      modalFooter.style.display = 'none';
      modalResultView.style.display = 'block';

      resultTitle.textContent = 'Processing Completed!';
      resultMessage.textContent = data.message || 'Your file is ready for download.';

      if (data.download_url) {
        btnDownload.href = data.download_url;
        btnDownload.download = data.filename || 'download.pdf';
        btnDownload.style.display = 'inline-flex';
      } else {
        btnDownload.style.display = 'none';
      }

      // Render structured preview for text extraction / search results
      if (data.pages) {
        // Extract Text preview
        renderExtractedTextPreview(data.pages);
      } else if (data.results) {
        // Search PDF preview
        renderSearchResultsPreview(data.results, data.total_matches);
      }

    } catch (err) {
      showToast(err.message, 'error');
      btnSubmit.disabled = false;
      progressContainer.style.display = 'none';
      btnActionText.textContent = tool.actionText;
    }
  });

  function renderExtractedTextPreview(pagesDict) {
    resultStructuredData.style.display = 'block';
    let html = `<div style="background: var(--bg-surface-elevated); padding: 1rem; border-radius: var(--radius-md); max-height: 250px; overflow-y: auto; font-family: var(--font-mono); font-size: 0.85rem; border: 1px solid var(--border-color);">`;
    for (const [pg, txt] of Object.entries(pagesDict)) {
      html += `<div style="margin-bottom: 0.75rem;"><strong style="color: var(--brand-red);">Page ${parseInt(pg) + 1}:</strong><div style="white-space: pre-wrap; margin-top: 0.25rem; color: var(--text-secondary);">${txt || '<i>(No text detected)</i>'}</div></div>`;
    }
    html += `</div>`;
    resultStructuredData.innerHTML = html;
  }

  function renderSearchResultsPreview(results, totalMatches) {
    resultStructuredData.style.display = 'block';
    let html = `<div style="background: var(--bg-surface-elevated); padding: 1rem; border-radius: var(--radius-md); max-height: 250px; overflow-y: auto; border: 1px solid var(--border-color);">`;
    html += `<h4 style="margin-bottom: 0.5rem; font-size: 0.95rem;">Search Matches (${totalMatches}):</h4>`;
    results.forEach(r => {
      html += `<div style="padding: 0.4rem 0; border-bottom: 1px solid var(--border-color); font-size: 0.85rem;"><strong>Page ${r.page + 1}:</strong> ${r.count} match(es)</div>`;
    });
    html += `</div>`;
    resultStructuredData.innerHTML = html;
  }

  // --------------------------------------------------------------------------
  // Logs Viewer Modal
  // --------------------------------------------------------------------------
  async function loadLogs() {
    logsTerminal.innerHTML = '<div style="color: var(--text-muted);">Fetching recent events...</div>';
    try {
      const res = await fetch('/api/logs?limit=50');
      const data = await res.json();
      const events = data.events || [];

      if (events.length === 0) {
        logsTerminal.innerHTML = '<div style="color: var(--text-muted); text-align: center; padding: 2rem;">No runtime log events recorded yet.</div>';
        logsCountLabel.textContent = '0 events';
        return;
      }

      logsCountLabel.textContent = `Showing ${events.length} event(s)`;
      logsTerminal.innerHTML = '';

      events.reverse().forEach(ev => {
        const item = document.createElement('div');
        const statusClass = (ev.status || '').toLowerCase();
        item.className = `log-entry ${statusClass}`;

        const timeStr = ev.timestamp ? new Date(ev.timestamp).toLocaleTimeString() : '';
        item.innerHTML = `
          <span class="log-timestamp">[${timeStr}]</span>
          <strong>[${ev.module || 'SYSTEM'}]</strong>
          <span>${ev.action || ''}</span> &bull; 
          <span style="font-weight:700;">${ev.status}</span>
          <div style="font-size: 0.78rem; opacity: 0.85; margin-top: 0.2rem;">${ev.details || ''}</div>
        `;
        logsTerminal.appendChild(item);
      });
    } catch (err) {
      logsTerminal.innerHTML = `<div style="color: var(--brand-red);">Failed to load logs: ${err.message}</div>`;
    }
  }

  btnOpenLogs.addEventListener('click', () => {
    logsModal.classList.add('open');
    loadLogs();
  });

  logsModalClose.addEventListener('click', () => {
    logsModal.classList.remove('open');
  });

  btnRefreshLogs.addEventListener('click', loadLogs);

  btnClearLogs.addEventListener('click', async () => {
    if (confirm('Are you sure you want to clear all processing logs?')) {
      try {
        await fetch('/api/logs/clear', { method: 'POST' });
        showToast('Logs cleared', 'info');
        loadLogs();
      } catch (err) {
        showToast(err.message, 'error');
      }
    }
  });

  // Escape key closes modals
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeWorkspace();
      logsModal.classList.remove('open');
    }
  });

  // --------------------------------------------------------------------------
  // Initialization
  // --------------------------------------------------------------------------
  initTheme();
  filterTools();

})();
