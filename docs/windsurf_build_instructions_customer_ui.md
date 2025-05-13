# Build Instructions for Windsurf: Customer Matching UI

## 1. Introduction

This document provides detailed step-by-step instructions for the AI agent "Windsurf" to build the `customer_matching_ui` frontend application. This application is part of the AI Marketing System.

## 2. Target Application

-   **Application Name:** `customer_matching_ui`
-   **Framework:** Next.js
-   **Codebase Location:** Assumed to be within the `ai-marketing-system` project, specifically under the `frontend/customer_matching_ui/` directory.

## 3. Prerequisites for Windsurf

Before starting the build process, ensure the following prerequisites are met in your execution environment:

1.  **Access to Project Codebase:** You must have access to the complete `ai-marketing-system` project codebase, including the `frontend/customer_matching_ui/` directory. This can be achieved by cloning the repository from `https://github.com/kimhons/ai-marketing-system`.
2.  **Node.js and npm (or yarn):** Node.js (which includes npm) must be installed. The Long-Term Support (LTS) version is recommended. You can verify installation by running `node -v` and `npm -v` in your terminal.
3.  **Terminal/Command-Line Interface:** Access to a terminal or command-line interface to execute the necessary commands.

## 4. Build Steps

Follow these steps precisely to build the `customer_matching_ui` application:

### Step 4.1: Navigate to the Application Directory

Open your terminal and change your current directory to the `customer_matching_ui` application folder within the project.

```bash
cd /path/to/ai-marketing-system/frontend/customer_matching_ui/
```
*(Replace `/path/to/` with the actual path to the cloned project on your system.)*

### Step 4.2: Set Up Environment Variables

The application requires an environment variable `NEXT_PUBLIC_API_URL` to know the endpoint of the backend API Gateway.

1.  **Create `.env.local` file:** In the root of the `frontend/customer_matching_ui/` directory, create a new file named `.env.local`.
2.  **Add API URL to `.env.local`:** Open the `.env.local` file with a text editor and add the following line:

    ```
    NEXT_PUBLIC_API_URL=YOUR_ACTUAL_DEPLOYED_API_GATEWAY_URL
    ```

    **Crucial Note for Windsurf:** The placeholder `YOUR_ACTUAL_DEPLOYED_API_GATEWAY_URL` **MUST** be replaced with the live, deployed URL of the Google Cloud API Gateway that routes to the backend services. This URL should be provided to you or can be found by following Part 4, Step 7 of the main `deployment_guide_simple.md` document for the AI Marketing System.

### Step 4.3: Install Project Dependencies

Once in the `frontend/customer_matching_ui/` directory, install all the necessary Node.js packages defined in `package.json`.

```bash
npm install
```
*(If the project uses yarn, you would use `yarn install` instead.)*
This command will download and install all required libraries. This may take a few minutes.

### Step 4.4: Run the Build Command

After the dependencies are installed, run the build script defined in the `package.json` file. This command compiles the Next.js application and prepares it for production deployment.

```bash
npm run build
```
This command will typically generate an optimized version of the application.

## 5. Build Output

Upon successful completion of the `npm run build` command:

-   Next.js typically outputs the static assets and build artifacts. If the project is configured for static export (e.g., via `next export` in the build script), the output will usually be in an `out/` directory within `frontend/customer_matching_ui/`.
-   If it's a standard Next.js build for hybrid or server-side rendering that can also be statically hosted for many parts, the primary static assets are often found within the `.next/static/` directory, and public assets are served from the `public/` directory.
-   **For the purpose of deploying to Firebase Hosting as per the `deployment_guide_simple.md` and `firebase.json` configuration, we are interested in the files that make up the complete static version of this UI.**

## 6. Preparation for Firebase Hosting

The `firebase.json` file at the root of the `ai-marketing-system` project is configured to deploy static content from a `public_html` directory.

1.  **Identify Build Output:** Determine the exact location of the complete static build output from Step 5 (e.g., the `out/` folder or the necessary files from `.next/static/`, `public/`, and any root static files like `index.html` if generated).
2.  **Copy to `public_html`:**
    *   Navigate to the root directory of the `ai-marketing-system` project.
    *   Ensure a directory named `public_html` exists. If not, create it.
    *   Copy **all the contents** of the `customer_matching_ui` build output folder (from Step 6.1) directly into the `public_html/` directory.

    For example, if `npm run build` (and potentially `next export`) for `customer_matching_ui` places its output in `frontend/customer_matching_ui/out/`, you would copy everything from `frontend/customer_matching_ui/out/` into `ai-marketing-system/public_html/`.

## 7. Final Notes for Windsurf

-   These instructions are specifically for building the `customer_matching_ui`.
-   A separate set of instructions will be provided for building the `blueprint_generation_ui`.
-   The API Gateway URL provided in the `.env.local` file is critical for the application to function correctly by communicating with the backend services.
-   Refer to the main `deployment_guide_simple.md` for the overall deployment context and how this build fits into the Firebase Hosting deployment process.

Successfully building this application is a key step towards deploying the AI Marketing System.
