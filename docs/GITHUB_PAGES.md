# GitHub Pages Deployment

This directory contains files for deploying a simplified demo version of the Data Analysis and Feature Engineering Platform using GitHub Pages and Shinylive.

## Files

- `index.html` - The main entry point for the GitHub Pages site, containing the Shinylive demo
- `shinylive_demo.py` - A simplified version of the application for demonstration purposes
- `app.py` and other Python files - The full application code

## How to Deploy

1. Push this repository to GitHub
2. Go to your repository settings
3. Navigate to "Pages" in the sidebar
4. Under "Source", select "Deploy from a branch"
5. Select the branch (usually "main" or "master") and set the folder to "/docs"
6. Click "Save"

Your site will be published at `https://yourusername.github.io/your-repository-name/`

## Notes

- The Shinylive demo in `index.html` is a simplified version of the full application
- For the complete application with all features, users should clone the repository and run it locally
- Shinylive has limitations and may not support all features of the full application

## Local Development

To test the GitHub Pages deployment locally:

1. Install a local HTTP server:
   ```bash
   npm install -g http-server
   ```

2. Navigate to the docs directory:
   ```bash
   cd docs
   ```

3. Start the server:
   ```bash
   http-server
   ```

4. Open your browser to `http://localhost:8080` 