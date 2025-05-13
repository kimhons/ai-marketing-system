
## Part 5: Building the Website People See (Frontend on Firebase Hosting)

Now it's time to get the actual website parts online so people can use them! We have two main website parts: one for customers to find businesses (`customer_matching_ui`) and one for businesses to get their marketing blueprints (`blueprint_generation_ui`). We'll use Firebase Hosting for this – it's like a super-fast delivery service for websites!

**What you (or a grown-up helper) will do:**

1.  **Get Your API Gateway URL:** Make sure you have `YOUR_API_GATEWAY_URL` that you got at the end of Part 4. It looks something like `https://ai-marketing-gateway-YOUR_RANDOM_STUFF-YOUR_REGION.a.run.app`.

2.  **Update the `firebase.json` File (The Rulebook for Firebase):**
    *   In your project code folder on your computer, find the `firebase.json` file. It's in the main `ai-marketing-system-new` folder.
    *   Open `firebase.json` with your text editor (like VS Code).
    *   Look for this line (around line 18 or 19):
        `"destination": "https://YOUR_GCP_API_GATEWAY_URL"`
    *   Carefully replace `https://YOUR_GCP_API_GATEWAY_URL` with your actual `YOUR_API_GATEWAY_URL` that you copied in Part 4, Step 7.
    *   **Save the `firebase.json` file.**

3.  **Prepare the Frontend Code (Tell the Website Where its Brain Is):**
    *   Your website parts (`customer_matching_ui` and `blueprint_generation_ui`) need to know the address of the API Gateway to send requests to the brain.
    *   **For `customer_matching_ui`:**
        *   Navigate to its folder: `ai-marketing-system-new/frontend/customer_matching_ui/`
        *   Create a new file in this folder named `.env.local` (notice the dot at the beginning!).
        *   Open `.env.local` with your text editor and add this single line, replacing the placeholder with your actual API Gateway URL:
            `NEXT_PUBLIC_API_URL=https://YOUR_API_GATEWAY_URL`
        *   Save the `.env.local` file.
    *   **For `blueprint_generation_ui`:**
        *   Navigate to its folder: `ai-marketing-system-new/frontend/blueprint_generation_ui/`
        *   Create a new file in this folder named `.env.local`.
        *   Open `.env.local` and add this single line, replacing the placeholder with your actual API Gateway URL:
            `NEXT_PUBLIC_API_URL=https://YOUR_API_GATEWAY_URL`
        *   Save the `.env.local` file.

4.  **Build the Websites (Package Them Up for Delivery):**
    *   Open your computer's terminal.
    *   **Build `customer_matching_ui`:**
        *   In the terminal, navigate to the `customer_matching_ui` folder:
            ```bash
            cd /FULL/PATH/TO/YOUR/ai-marketing-system-new/frontend/customer_matching_ui
            ```
        *   Install its building tools (if you haven't before for this project):
            ```bash
            npm install
            ```
            (This might take a few minutes.)
        *   Now, build the website:
            ```bash
            npm run build
            ```
            (This usually creates a folder named `out` or `.next` inside `customer_matching_ui` containing the ready-to-go website files.) For Firebase Hosting with Next.js, if you are using `next export` (static HTML export), the output is typically in an `out` folder. If you are using Next.js's more advanced features that require a Node.js server, Firebase can also support that, but our `firebase.json` is set up for static hosting primarily. Let's assume `npm run build` produces static output suitable for hosting or that Firebase handles the Next.js build correctly.

    *   **Build `blueprint_generation_ui`:**
        *   In the terminal, navigate to the `blueprint_generation_ui` folder:
            ```bash
            cd /FULL/PATH/TO/YOUR/ai-marketing-system-new/frontend/blueprint_generation_ui
            ```
        *   Install its building tools:
            ```bash
            npm install
            ```
        *   Build the website:
            ```bash
            npm run build
            ```

5.  **Organize Files for Firebase Hosting (Put Them in the Delivery Truck):**
    *   The `firebase.json` file is set up to look for all website files in a single folder named `public_html` at the root of your project (`ai-marketing-system-new/public_html/`).
    *   Go to your main project folder (`ai-marketing-system-new`).
    *   If a folder named `public_html` doesn't exist there, create it.
    *   **Copy `customer_matching_ui` files:**
        *   Go into `frontend/customer_matching_ui/`. Find the build output folder (usually `out` if you used `next export`, or the relevant static assets from `.next/static` and public files if it's a standard Next.js build for static hosting). Copy *all the contents* of this output folder directly into your main `ai-marketing-system-new/public_html/` folder.
    *   **Copy `blueprint_generation_ui` files:**
        *   Go into `frontend/blueprint_generation_ui/`. Find its build output folder.
        *   Inside `ai-marketing-system-new/public_html/`, create a new folder named `blueprint-generator`.
        *   Copy *all the contents* of the `blueprint_generation_ui` build output folder into this new `ai-marketing-system-new/public_html/blueprint-generator/` folder.

    *   Your `public_html` folder should now look roughly like this:
        ```
        ai-marketing-system-new/
            public_html/
                index.html             (from customer_matching_ui)
                _next/                 (from customer_matching_ui)
                favicon.ico            (from customer_matching_ui)
                some-other-files...    (from customer_matching_ui)
                blueprint-generator/
                    index.html         (from blueprint_generation_ui)
                    _next/             (from blueprint_generation_ui)
                    favicon.ico        (from blueprint_generation_ui)
                    some-other-files... (from blueprint_generation_ui)
        ```

6.  **Deploy to Firebase Hosting (Send the Delivery Truck!):**
    *   Go back to your computer's terminal.
    *   Navigate to the main project folder (`ai-marketing-system-new`):
        ```bash
        cd /FULL/PATH/TO/YOUR/ai-marketing-system-new
        ```
    *   **Log in to Firebase (if you haven't already with the CLI):**
        ```bash
        firebase login
        ```
        (This will open a browser window for you to log in with your Google Account that has Firebase access.)
    *   **Select Your Firebase Project:**
        *   First, see if you have any Firebase projects listed:
            ```bash
            firebase projects:list
            ```
        *   If you haven't created a Firebase project for this yet, go to [https://console.firebase.google.com/](https://console.firebase.google.com/), click "Add project", and follow the steps. Give it a name like `ai-marketing-system-prod`. Note its Project ID.
        *   Tell the Firebase CLI which project to use:
            ```bash
            firebase use YOUR_FIREBASE_PROJECT_ID
            ```
            (Replace `YOUR_FIREBASE_PROJECT_ID` with the ID of your Firebase project, e.g., `ai-marketing-system-prod` or `ai-marketing-system-prod-abcdef`).
    *   **Deploy!**
        ```bash
        firebase deploy --only hosting
        ```
        (This command looks at your `firebase.json` and uploads the contents of your `public_html` folder.)

7.  **Visit Your Live Website!**
    *   After the `firebase deploy` command finishes, it will show you a **Hosting URL**. It will look something like: `https://YOUR_FIREBASE_PROJECT_ID.web.app`.
    *   Open this URL in your web browser!
        *   The Customer Matching UI should be at the main address (e.g., `https://ai-marketing-system-prod.web.app`).
        *   The Blueprint Generation UI should be at `YOUR_HOSTING_URL/blueprint-generator/` (e.g., `https://ai-marketing-system-prod.web.app/blueprint-generator/`).

Your website is now LIVE on the internet for everyone to see!

## Part 6: Final Checks! (Is the Robot Working Perfectly?)

Everything *should* be working, but a good inventor always tests their creation!

1.  **Open Your Website:** Go to the Hosting URL Firebase gave you.
2.  **Test Customer Matching UI:**
    *   Does it load correctly?
    *   Try typing a search for a customer (e.g., "delicious pizza in London") in the search box and click the search button.
    *   Do you see results? Or a message if no businesses match?
3.  **Test Blueprint Generation UI:**
    *   Navigate to the blueprint generator page (e.g., `YOUR_HOSTING_URL/blueprint-generator/`).
    *   Does it load?
    *   Try filling out the form for a business and click the button to generate a blueprint.
    *   Does it show you the generated blueprint parts (like Personas, Strategy)?
    *   (Remember, blueprint generation might require you to be logged in. Test the login first!)
4.  **Test Login/Registration (If you have a login button/page):**
    *   Try creating a new user account.
    *   Try logging in with that new account.
    *   Try logging out.
5.  **What if Something is Wrong? (Don't Panic! Be a Detective!):**
    *   **Check Your Browser's Detective Tools:**
        *   In most browsers (Chrome, Firefox, Edge), press the `F12` key on your keyboard. This opens "Developer Tools".
        *   Click on the **"Console"** tab. Are there any red error messages? These can give clues!
        *   Click on the **"Network"** tab. When you click a button on your website, you should see new lines appear here. These are requests to your API Gateway. Click on them. Do they say "200 OK" (good!) or an error like "404 Not Found" or "500 Server Error" (bad!)? If it's an error, look at the "Response" tab for that request to see if there's more info.
    *   **Check Google Cloud Logs (The Robot's Diary):**
        *   Go to `https://console.cloud.google.com`.
        *   **API Gateway Logs:** Search for "API Gateway", click on your `ai-marketing-gateway`, and look for a "Logs" tab or link. See if requests are reaching it and if it's forwarding them correctly or showing errors.
        *   **Cloud Run Logs:** Search for "Cloud Run", click on your `auth-service`, then click the "LOGS" tab. Do the same for your `ai-services-api`. These logs will show any errors happening inside the "brain" parts.
        *   **Cloud SQL Logs:** Search for "Cloud SQL", click your instance, and look for logs if you suspect database connection issues.

**YOU DID IT! AMAZING WORK!** 🚀

You have successfully deployed a very complex and smart AI Marketing System to the internet! This involved setting up secure secrets, a database, backend brain services, a traffic controller, and the user-facing websites. That's a lot of steps, and you got through them!

Remember, if you hit a snag, that's just part of being a tech explorer. Go back through the steps, check your typing, and use the logs to find clues. Every problem you solve makes you an even better tech superstar!

Enjoy your new system! 🎉

