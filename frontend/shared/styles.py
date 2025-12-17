"""Shared CSS styles for the frontend application"""

# Common styles used across all pages
COMMON_STYLES = """
body {
    font-family: Arial, sans-serif;
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
    background: #f5f5f5;
}

.header {
    background: white;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* Button Styles */
.btn {
    display: inline-block;
    padding: 10px 20px;
    background: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    border: none;
    cursor: pointer;
    font-size: 14px;
    margin-right: 10px;
}

.btn:hover {
    background: #0056b3;
}

.btn-secondary {
    background: #6c757d;
}

.btn-secondary:hover {
    background: #545b62;
}

.btn-danger {
    background: #dc3545;
}

.btn-danger:hover {
    background: #c82333;
}

.btn-warning {
    background: #ffc107;
    color: #212529;
}

.btn-warning:hover {
    background: #e0a800;
}

.btn-success {
    background: #28a745;
}

.btn-success:hover {
    background: #218838;
}

/* Content Container */
.content {
    background: white;
    padding: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* Form Styles */
.form-group {
    margin-bottom: 20px;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #333;
}

.form-group input,
.form-group textarea,
.form-group select {
    width: 100%;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    box-sizing: border-box;
    font-family: Arial, sans-serif;
}

.form-group textarea {
    min-height: 100px;
    resize: vertical;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
    outline: none;
    border-color: #007bff;
}

/* Alert Messages */
.error {
    color: #dc3545;
    padding: 10px;
    background: #f8d7da;
    border-radius: 4px;
    margin-bottom: 20px;
}

.success {
    color: #155724;
    padding: 10px;
    background: #d4edda;
    border-radius: 4px;
    margin-bottom: 20px;
}

.empty-state {
    text-align: center;
    padding: 40px;
    color: #666;
}

/* Detail Views */
.detail-section {
    margin-bottom: 30px;
    padding: 20px;
    background: #f8f9fa;
    border-radius: 8px;
}

.detail-section h3 {
    color: #333;
    border-bottom: 2px solid #007bff;
    padding-bottom: 10px;
    margin-top: 0;
}

.detail-row {
    display: flex;
    padding: 10px 0;
    border-bottom: 1px solid #e9ecef;
}

.detail-label {
    font-weight: bold;
    width: 200px;
    color: #555;
}

.detail-value {
    color: #333;
    flex-grow: 1;
}

/* Badges */
.badge {
    display: inline-block;
    padding: 4px 12px;
    background: #007bff;
    color: white;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.badge-draft {
    background: #ffc107;
    color: #212529;
}

.badge-archived {
    background: #6c757d;
}
"""

# Document-specific styles
DOCUMENT_STYLES = """
.document-list {
    list-style: none;
    padding: 0;
}

.document-item {
    padding: 20px;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    transition: background 0.2s;
}

.document-item:hover {
    background: #f8f9fa;
}

.document-item:last-child {
    border-bottom: none;
}

.document-info {
    flex-grow: 1;
}

.document-info h3 {
    margin: 0 0 10px 0;
    color: #333;
}

.document-info p {
    margin: 5px 0;
    color: #666;
    font-size: 14px;
}

.document-actions {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}

.filter-bar {
    margin-bottom: 20px;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 4px;
    display: flex;
    gap: 10px;
    align-items: center;
}

.version-list {
    list-style: none;
    padding: 0;
}

.version-item {
    padding: 15px;
    border: 1px solid #e9ecef;
    border-radius: 4px;
    margin-bottom: 10px;
    background: white;
}

.version-item h4 {
    margin: 0 0 10px 0;
    color: #333;
}

.version-current {
    border-color: #007bff;
    background: #e7f3ff;
}

.markdown-content {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 4px;
    border-left: 3px solid #007bff;
    max-height: 300px;
    overflow-y: auto;
    font-family: monospace;
    font-size: 12px;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.permission-list {
    list-style: none;
    padding: 0;
}

.permission-item {
    padding: 10px;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
"""

# User-specific styles
USER_STYLES = """
.user-list {
    list-style: none;
    padding: 0;
}

.user-item {
    padding: 15px;
    border-bottom: 1px solid #e9ecef;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.user-item:last-child {
    border-bottom: none;
}

.user-info {
    flex-grow: 1;
}

.user-info h3 {
    margin: 0 0 5px 0;
    color: #333;
}

.user-info p {
    margin: 0;
    color: #666;
    font-size: 14px;
}

.user-actions {
    display: flex;
    gap: 10px;
}
"""

# Search-specific styles
SEARCH_STYLES = """
.search-section {
    margin-bottom: 30px;
}

.search-form {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.search-input {
    flex-grow: 1;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
}

.search-input:focus {
    outline: none;
    border-color: #007bff;
}

.form-row {
    display: flex;
    gap: 15px;
    margin-bottom: 15px;
    align-items: center;
    flex-wrap: wrap;
}

.form-label {
    font-weight: bold;
    color: #333;
    white-space: nowrap;
}

.user-select {
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    background: white;
    cursor: pointer;
    min-width: 250px;
}

.user-select:focus {
    outline: none;
    border-color: #007bff;
}

.results-section {
    margin-top: 30px;
}

.result-item {
    padding: 20px;
    border: 1px solid #e9ecef;
    border-radius: 8px;
    margin-bottom: 15px;
    background: white;
    transition: box-shadow 0.2s;
}

.result-item:hover {
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
}

.result-title {
    font-size: 18px;
    font-weight: bold;
    color: #333;
    margin: 0;
}

.result-score {
    background: #e7f3ff;
    color: #0056b3;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: bold;
}

.result-content {
    color: #666;
    line-height: 1.6;
    margin: 10px 0;
}

.result-meta {
    display: flex;
    gap: 15px;
    font-size: 12px;
    color: #999;
    margin-top: 10px;
}
"""

# Agent-specific styles
AGENT_STYLES = """
.agent-section {
    margin-bottom: 30px;
}

.query-form {
    margin-bottom: 30px;
}

.query-input {
    width: 100%;
    padding: 15px;
    border: 2px solid #ddd;
    border-radius: 8px;
    font-size: 16px;
    font-family: Arial, sans-serif;
    resize: vertical;
    min-height: 100px;
}

.query-input:focus {
    outline: none;
    border-color: #007bff;
}

.chat-container {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 20px;
    margin-top: 20px;
}

.chat-message {
    margin-bottom: 20px;
    padding: 15px;
    border-radius: 8px;
}

.chat-message.user {
    background: #e7f3ff;
    border-left: 4px solid #007bff;
}

.chat-message.agent {
    background: white;
    border-left: 4px solid #28a745;
}

.message-role {
    font-weight: bold;
    margin-bottom: 8px;
    color: #333;
}

.message-content {
    color: #555;
    line-height: 1.6;
    white-space: pre-wrap;
    word-wrap: break-word;
}

.example-queries {
    background: #fff3cd;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.example-queries h4 {
    margin-top: 0;
    color: #856404;
}

.example-queries ul {
    margin: 10px 0;
    padding-left: 20px;
}

.example-queries li {
    color: #856404;
    margin-bottom: 5px;
}
"""

# Upload-specific styles
UPLOAD_STYLES = """
.upload-section {
    margin-bottom: 30px;
}

.mode-selector {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
}

.mode-button {
    flex: 1;
    padding: 15px;
    background: #f8f9fa;
    border: 2px solid #ddd;
    border-radius: 8px;
    cursor: pointer;
    text-align: center;
    transition: all 0.2s;
}

.mode-button:hover {
    background: #e9ecef;
}

.mode-button.active {
    background: #007bff;
    color: white;
    border-color: #007bff;
}

.upload-form {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.file-input-wrapper {
    position: relative;
    overflow: hidden;
    display: inline-block;
    margin-bottom: 15px;
}

.file-input-label {
    display: inline-block;
    padding: 12px 20px;
    background: #007bff;
    color: white;
    border-radius: 4px;
    cursor: pointer;
    font-weight: bold;
}

.file-input-label:hover {
    background: #0056b3;
}

input[type="file"] {
    font-size: 14px;
    padding: 10px;
}

.result-box {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 8px;
    padding: 20px;
    margin-top: 20px;
}

.result-box h3 {
    color: #155724;
    margin-top: 0;
}

.result-details {
    color: #155724;
}

.result-details p {
    margin: 5px 0;
}
"""

# Permission-specific styles
PERMISSION_STYLES = """
.permission-section {
    margin-bottom: 30px;
}

.document-select-list {
    list-style: none;
    padding: 0;
}

.document-select-item {
    padding: 15px;
    border: 2px solid #e9ecef;
    border-radius: 8px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s;
    background: white;
}

.document-select-item:hover {
    background: #f8f9fa;
    border-color: #007bff;
}

.grant-form {
    background: #f8f9fa;
    padding: 20px;
    border-radius: 8px;
}

.permission-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.permission-table th,
.permission-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
}

.permission-table th {
    background: #f8f9fa;
    font-weight: bold;
    color: #333;
}

.permission-table tr:hover {
    background: #f8f9fa;
}
"""
