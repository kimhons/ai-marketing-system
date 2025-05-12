# Customer Matching UI - Specification

## 1. Overview

This document outlines the specification for the frontend User Interface (UI) for the Customer Matching feature of the AI Marketing System. The UI will allow users (e.g., internal team members or potentially customers themselves) to input their service needs and view a list of businesses matched by the `CustomerMatcherService`.

## 2. Technology Stack

- **Framework:** Next.js (React)
- **Styling:** Tailwind CSS (consistent with potential existing UI components)
- **State Management:** React Context API or a lightweight state management library (e.g., Zustand) if complexity grows.

## 3. Key Features & Components

### 3.1. Customer Query Input Form

-   **Purpose:** Allow users to describe their needs.
-   **Components:**
    -   **Query Text Input:** A multi-line text area for the user to describe their problem or what they are looking for (e.g., "I need a plumber for a leaky faucet in downtown.").
        -   Label: "Describe your needs:"
        -   Placeholder: "e.g., I need a reliable accountant for my small retail business."
    -   **Service Category Input (Optional but Recommended):** A text input or dropdown to specify the general category of service.
        -   Label: "Service Category (e.g., Home Services, Financial, IT Support):"
        -   Placeholder: "e.g., Marketing Services"
    -   **Keywords Input:** A text input field where users can enter comma-separated keywords relevant to their query.
        -   Label: "Keywords (comma-separated):"
        -   Placeholder: "e.g., SEO, social media, content creation"
    -   **Location Input:** A text input field for the user to specify their location or the desired service location.
        -   Label: "Location (City/Region):"
        -   Placeholder: "e.g., San Francisco, CA"
    -   **Submit Button:** A button labeled "Find Businesses" or "Get Matches".

### 3.2. Matched Businesses Display Area

-   **Purpose:** Display the list of businesses returned by the `CustomerMatcherService`.
-   **Layout:** A card-based or list-based layout for displaying multiple businesses.
-   **Information per Business Card/Item:**
    -   Business Name
    -   Tagline (if available from `MatchedBusinessProfile`)
    -   Location
    -   Relevant Services (list or tags)
    -   Relevance Score (formatted, e.g., "Relevance: 85%")
    -   Match Reason (brief explanation of why this business was matched)
    -   (Optional) A "View Details" button/link if more extensive business profiles are available elsewhere.
-   **States:**
    -   **Loading State:** Display a spinner or loading message while the API call is in progress.
    -   **No Results State:** Display a message like "No businesses found matching your criteria. Please try refining your search."
    -   **Error State:** Display a user-friendly error message if the API call fails (e.g., "Sorry, we couldn't process your request right now. Please try again later.").

## 4. User Flow

1.  User navigates to the Customer Matching page.
2.  User fills in the query input form with their requirements.
3.  User clicks the "Find Businesses" button.
4.  The UI displays a loading state.
5.  The UI sends the query data to a backend API endpoint that interfaces with the `CustomerMatcherService`.
6.  The backend processes the request and returns a list of matched business profiles (or an empty list/error).
7.  The UI receives the response:
    -   If successful and matches are found, it displays them in the Matched Businesses Display Area.
    -   If successful but no matches, it displays the "No Results" state.
    -   If an error occurs, it displays the "Error State".

## 5. API Interaction

-   The frontend will make an asynchronous request (e.g., POST) to a backend API endpoint (e.g., `/api/match-customers`).
-   **Request Payload (JSON):**
    ```json
    {
      "query_text": "User's detailed query",
      "service_category": "Optional category",
      "keywords": ["keyword1", "keyword2"],
      "location": "User's location"
    }
    ```
-   **Response Payload (JSON - Success with matches):**
    ```json
    {
      "success": true,
      "matches": [
        {
          "business_id": "biz123",
          "business_name": "Example Business Inc.",
          "tagline": "Your trusted partner for X.",
          "location": "Cityville",
          "relevant_services": ["Service A", "Service B"],
          "relevance_score": 0.85,
          "match_reason": "Matches based on keywords and location."
        }
        // ... more matches
      ]
    }
    ```
-   **Response Payload (JSON - Success with no matches):**
    ```json
    {
      "success": true,
      "matches": []
    }
    ```
-   **Response Payload (JSON - Error):**
    ```json
    {
      "success": false,
      "error": "A description of the error."
    }
    ```

## 6. Directory Structure (Proposed)

```
/home/ubuntu/ai-marketing-system-new/
└── frontend/
    └── customer_matching_ui/
        ├── public/
        ├── src/
        │   ├── app/                 # Next.js App Router
        │   │   └── page.tsx         # Main page for customer matching
        │   ├── components/
        │   │   ├── CustomerQueryForm.tsx
        │   │   ├── MatchedBusinessCard.tsx
        │   │   └── MatchedBusinessList.tsx
        │   ├── services/            # API call functions
        │   │   └── matchingService.ts
        │   └── lib/                 # Utility functions, types
        │       └── types.ts         # TypeScript interfaces for API data
        ├── next.config.js
        ├── package.json
        ├── tsconfig.json
        └── tailwind.config.js
```

This specification provides a starting point. Details can be refined during development.

