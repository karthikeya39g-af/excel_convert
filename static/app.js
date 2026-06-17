/**
 * UNIVERSITY EXCEL CONVERTER - FRONTEND ENGINE
 */

document.addEventListener('DOMContentLoaded', () => {
    // Mode State
    let currentMode = null; // 'regular' or 'supply'
    let selectedFile = null;

    // DOM Elements - Sections
    const secModeSelection = document.getElementById('mode-selection');
    const secUpload = document.getElementById('upload-section');
    const secLoading = document.getElementById('loading-section');
    const secSuccess = document.getElementById('success-section');

    // DOM Elements - Mode Selection Buttons
    const btnModeRegular = document.getElementById('btn-mode-regular');
    const btnModeSupply = document.getElementById('btn-mode-supply');

    // DOM Elements - Upload & Dropzone
    const btnBackToModes = document.getElementById('btn-back-to-modes');
    const badgeText = document.getElementById('badge-text');
    const badgeIcon = document.getElementById('badge-icon');
    const uploadForm = document.getElementById('upload-form');
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('file-input');
    const fileDetails = document.getElementById('file-details');
    const fileNameDisp = document.getElementById('file-name');
    const fileSizeDisp = document.getElementById('file-size');
    const btnRemoveFile = document.getElementById('btn-remove-file');
    const btnConvert = document.getElementById('btn-convert');
    const promptDetails = document.querySelector('.dropzone-prompt');

    // DOM Elements - Loading
    const loadingStatusText = document.getElementById('loading-status-text');

    // DOM Elements - Success Details
    const summaryStudentsCount = document.getElementById('summary-students-count');
    const summaryOutputType = document.getElementById('summary-output-type');
    const btnDownload = document.getElementById('btn-download');
    const btnReset = document.getElementById('btn-reset');

    // DOM Elements - Error Toast
    const errorToast = document.getElementById('error-toast');
    const errorMessageText = document.getElementById('error-message-text');
    const btnCloseToast = document.getElementById('btn-close-toast');

    // ==========================================
    // UTILITY FUNCTIONS
    // ==========================================

    // Format file sizes into human-readable strings
    function formatBytes(bytes, decimals = 2) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const dm = decimals < 0 ? 0 : decimals;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
    }

    // Toggle active section card
    function showSection(sectionToShow) {
        const sections = [secModeSelection, secUpload, secLoading, secSuccess];
        sections.forEach(sec => {
            if (sec === sectionToShow) {
                sec.classList.remove('hidden');
                sec.classList.add('active');
            } else {
                sec.classList.add('hidden');
                sec.classList.remove('active');
            }
        });
    }

    // Apply specific theme variables depending on mode
    function applyTheme(element, mode) {
        element.classList.remove('regular-theme', 'supply-theme');
        if (mode === 'regular') {
            element.classList.add('regular-theme');
        } else if (mode === 'supply') {
            element.classList.add('supply-theme');
        }
    }

    // Show error toast notification
    function showError(message) {
        errorMessageText.textContent = message || 'An unexpected error occurred while processing the file.';
        errorToast.classList.remove('hidden');
        
        // Auto-close after 8 seconds
        setTimeout(() => {
            errorToast.classList.add('hidden');
        }, 8000);
    }

    // ==========================================
    // SELECTION MODE EVENTS
    // ==========================================

    btnModeRegular.addEventListener('click', () => {
        currentMode = 'regular';
        setupUploadSection();
    });

    btnModeSupply.addEventListener('click', () => {
        currentMode = 'supply';
        setupUploadSection();
    });

    function setupUploadSection() {
        applyTheme(secUpload, currentMode);
        
        // Update header badge details
        if (currentMode === 'regular') {
            badgeText.textContent = 'Regular Mode';
            badgeIcon.innerHTML = '<i data-lucide="graduation-cap"></i>';
        } else {
            badgeText.textContent = 'Supply Mode';
            badgeIcon.innerHTML = '<i data-lucide="rotate-ccw"></i>';
        }
        
        // Refresh icons inside dynamically updated badge
        lucide.createIcons();

        // Clear previous files if any
        clearSelectedFile();
        
        showSection(secUpload);
    }

    btnBackToModes.addEventListener('click', () => {
        currentMode = null;
        clearSelectedFile();
        showSection(secModeSelection);
    });

    // ==========================================
    // DROPZONE & FILE INPUT HANDLERS
    // ==========================================

    // Click dropzone to open input dialog
    dropzone.addEventListener('click', (e) => {
        // Prevent trigger loop when clicking the file details container elements
        if (e.target.closest('#btn-remove-file')) return;
        fileInput.click();
    });

    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    // Add drag highlight classes
    ['dragenter', 'dragover'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.add('dragover');
        }, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropzone.addEventListener(eventName, () => {
            dropzone.classList.remove('dragover');
        }, false);
    });

    // Handle dropped file
    dropzone.addEventListener('drop', (e) => {
        const dt = e.dataTransfer;
        const files = dt.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });

    // Handle file selection from browse dialog
    fileInput.addEventListener('change', (e) => {
        if (fileInput.files.length > 0) {
            handleFileSelect(fileInput.files[0]);
        }
    });

    function handleFileSelect(file) {
        // Validate extension
        const allowedExtensions = ['.xlsx', '.xls', '.csv'];
        const name = file.name.toLowerCase();
        const isValid = allowedExtensions.some(ext => name.endsWith(ext));

        if (!isValid) {
            showError('Invalid file format. Please upload an Excel (.xlsx, .xls) or CSV file.');
            clearSelectedFile();
            return;
        }

        selectedFile = file;
        fileNameDisp.textContent = file.name;
        fileSizeDisp.textContent = formatBytes(file.size);

        // UI toggles
        promptDetails.classList.add('hidden');
        fileDetails.classList.remove('hidden');
        btnConvert.removeAttribute('disabled');

        // Let the icon reflect sheet file details
        const fileIcon = fileDetails.querySelector('.file-type-icon');
        if (fileIcon) {
            fileIcon.setAttribute('data-lucide', 'file-spreadsheet');
            lucide.createIcons();
        }
    }

    btnRemoveFile.addEventListener('click', (e) => {
        e.preventDefault();
        clearSelectedFile();
    });

    function clearSelectedFile() {
        selectedFile = null;
        fileInput.value = '';
        promptDetails.classList.remove('hidden');
        fileDetails.classList.add('hidden');
        btnConvert.setAttribute('disabled', 'true');
    }

    // ==========================================
    // CONVERSION API TRIGGER
    // ==========================================

    uploadForm.addEventListener('submit', (e) => {
        e.preventDefault();
        if (!selectedFile || !currentMode) return;

        // Prepare FormData
        const formData = new FormData();
        formData.append('file', selectedFile);
        formData.append('mode', currentMode);

        // Prep Loading Screen Theme & Text
        applyTheme(secLoading, currentMode);
        if (currentMode === 'regular') {
            loadingStatusText.textContent = 'Formatting columns and mapping grades for Regular TSheet...';
        } else {
            loadingStatusText.textContent = 'Filtering Data Science failed students & subjects for Supply TSheet...';
        }
        
        showSection(secLoading);

        // Call Flask API Endpoint
        fetch('/api/convert', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                // If response status is not 200, parse JSON to find specific error
                return response.json().then(errData => {
                    throw new Error(errData.error || 'Server error occurred during processing.');
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Update Success UI Elements
                summaryStudentsCount.textContent = data.students_count;
                summaryOutputType.textContent = currentMode === 'regular' ? 'Regular Format CSV' : 'Supply DS Format CSV';
                
                // Configure Download Button
                btnDownload.setAttribute('href', `/api/download/${data.filename}`);
                applyTheme(secSuccess, currentMode);
                
                // Show Success Panel
                showSection(secSuccess);
            } else {
                throw new Error(data.error || 'Failed to complete conversion.');
            }
        })
        .catch(err => {
            console.error('Error during conversion API request:', err);
            
            // Re-enable and show upload section
            showSection(secUpload);
            showError(err.message);
        });
    });

    // ==========================================
    // RESTART & TOAST LOGIC
    // ==========================================

    btnReset.addEventListener('click', () => {
        currentMode = null;
        clearSelectedFile();
        showSection(secModeSelection);
    });

    btnCloseToast.addEventListener('click', () => {
        errorToast.classList.add('hidden');
    });
});
