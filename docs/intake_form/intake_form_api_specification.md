<Begin of file>
# Business Intake Form - Backend API Specification

This document details the backend API endpoints and data models required to support the Business Intake Form module of the AI Marketing System. It complements the `intake_form_ui_specification.md` and is designed to handle data from `intake_form_questions.md`.

## 1. Core Requirements

*   **Secure Data Reception:** All data must be transmitted securely (HTTPS).
*   **Data Validation:** Robust validation for all incoming data.
*   **Structured Storage:** Data must be stored in a structured manner, easily queryable and usable by the AI Adaptation Agent for blueprint generation.
*   **Support for Partial Submissions:** Allow users to save progress and resume later.
*   **User Association:** All intake data must be clearly associated with a specific user and their business entity.
*   **Versioning (Future Consideration):** While not MVP, consider how updated intake submissions might be versioned or tracked over time.

## 2. Data Model (Conceptual - to be stored in PostgreSQL)

We will use the existing `businesses` table, specifically the `intake_data` JSONB column, to store the comprehensive intake information. A new table might be needed to track the status of the intake process itself.

**Table: `businesses` (existing)**
*   `id`: SERIAL PRIMARY KEY
*   `user_id`: INTEGER REFERENCES `users(id)`
*   `business_name`: VARCHAR(255)
*   `industry`: VARCHAR(255)
*   `intake_data`: JSONB - This will store the full set of answers from the intake form. The JSON structure will mirror the sections and questions from `intake_form_questions.md`.
    *   Example structure within `intake_data`:
        ```json
        {
          "section_1_business_basics": {
            "q1_business_name": "User's Answer",
            "q2_website_url": "User's Answer",
            ...
          },
          "section_2_target_audience": {
            "q_persona_1_name": "User's Answer",
            ...
          },
          "metadata": {
            "submission_status": "partial" / "complete",
            "last_saved_step": "section_2_q3",
            "submitted_at": "timestamp",
            "updated_at": "timestamp"
          }
        }
        ```
*   `created_at`: TIMESTAMP
*   `updated_at`: TIMESTAMP

**New Table: `intake_submissions` (Optional, for more detailed status tracking if `intake_data.metadata.submission_status` is insufficient)**
*   `id`: SERIAL PRIMARY KEY
*   `business_id`: INTEGER REFERENCES `businesses(id)`
*   `status`: VARCHAR(50) (e.g., `pending_user_input`, `submitted_for_blueprint`, `blueprint_generated`)
*   `last_completed_step`: VARCHAR(255) (e.g., identifier for the last successfully saved step/question)
*   `created_at`: TIMESTAMP
*   `updated_at`: TIMESTAMP

For MVP, we will try to manage status within the `intake_data` JSONB field in the `businesses` table to keep it simpler.

## 3. API Endpoints

All endpoints will be under a base path like `/api/v1/intake`.
Authentication will be required for all endpoints (e.g., JWT Bearer token identifying the user).

### 3.1. `POST /api/v1/intake/save`

*   **Purpose:** To save partial or complete intake form data for the authenticated user's business.
*   **Request Body:**
    ```json
    {
      "business_id": "integer", // ID of the business entity this intake belongs to
      "current_step_identifier": "string", // e.g., "section_2_q5", helps track progress
      "is_final_submission": "boolean", // true if this is the complete submission, false for saving progress
      "answers": {
        // A JSON object containing answers provided so far.
        // Structure should mirror the sections/questions.
        // Example:
        "section_1_business_basics": {
          "q1_business_name": "Acme Corp",
          "q2_website_url": "https://acme.com"
        },
        "section_2_target_audience": {
          "q_persona_1_name": "Tech Savvy Tina"
        }
        // ... other sections and answers
      }
    }
    ```
*   **Response (Success - 200 OK):**
    ```json
    {
      "status": "success",
      "message": "Intake data saved successfully.",
      "business_id": "integer",
      "submission_status": "partial" / "complete", // Reflects the new status
      "last_saved_at": "timestamp"
    }
    ```
*   **Response (Error - e.g., 400 Bad Request, 401 Unauthorized, 404 Not Found, 500 Server Error):**
    ```json
    {
      "status": "error",
      "message": "Detailed error message.",
      "errors": { // Optional: field-specific validation errors
        "answers.section_1.q1_business_name": "Business name cannot be empty."
      }
    }
    ```
*   **Logic:**
    1.  Authenticate user.
    2.  Verify `business_id` belongs to the authenticated user.
    3.  Validate incoming `answers` against expected structure and types (from `intake_form_questions.md`).
    4.  Merge new answers with any existing `intake_data` for the business.
    5.  Update `intake_data` in the `businesses` table.
    6.  Update metadata within `intake_data` (e.g., `submission_status`, `last_saved_step`, `updated_at`).
    7.  If `is_final_submission` is true, potentially trigger a notification or background process for the AI Adaptation Agent to start blueprint generation (this part is out of scope for this specific API endpoint but is the next step in the flow).

### 3.2. `GET /api/v1/intake/{business_id}`

*   **Purpose:** To retrieve existing intake form data for a specific business, allowing users to resume a saved session.
*   **URL Parameters:**
    *   `business_id`: integer - The ID of the business whose intake data is being requested.
*   **Response (Success - 200 OK):**
    ```json
    {
      "status": "success",
      "business_id": "integer",
      "submission_status": "partial" / "complete" / "not_started",
      "last_saved_step_identifier": "string", // e.g., "section_2_q5" or null
      "answers": { // The stored answers, or an empty object if not started
        "section_1_business_basics": {
          "q1_business_name": "Acme Corp",
          "q2_website_url": "https://acme.com"
        }
        // ... other sections and answers
      },
      "last_saved_at": "timestamp" // or null
    }
    ```
*   **Response (Error - e.g., 401 Unauthorized, 404 Not Found):**
    ```json
    {
      "status": "error",
      "message": "Detailed error message."
    }
    ```
*   **Logic:**
    1.  Authenticate user.
    2.  Verify `business_id` belongs to the authenticated user.
    3.  Retrieve `intake_data` (and its internal metadata) from the `businesses` table.
    4.  Format and return the data.

## 4. Data Validation Rules

*   Standard validation: required fields, data types (string, number, boolean, email format, URL format).
*   Length constraints for text fields where appropriate.
*   For multiple-choice/dropdowns, ensure submitted values are within the allowed set of options.
*   The specific validation rules will be derived from the question types in `intake_form_questions.md`.

## 5. Security Considerations

*   **Authentication:** All endpoints must be protected and require user authentication.
*   **Authorization:** Users should only be able to access/modify intake data for businesses they own or have explicit permissions for.
*   **Input Sanitization:** Protect against XSS and other injection attacks, although with JSON payloads and proper ORM usage, this risk is mitigated.
*   **HTTPS:** Enforce HTTPS for all API communication.

## 6. Future Considerations

*   **Webhook for AI Agent:** Upon final submission, the API could trigger a webhook or place a message on a queue to notify the AI Adaptation Agent that new intake data is ready for processing.
*   **Intake Form Versioning:** If the intake questions evolve, a versioning system for both the questions and the submitted data might be needed.

This API specification provides the foundation for the backend services supporting the Business Intake Form. The implementation will likely use Flask, leveraging its capabilities for routing, request handling, and potentially SQLAlchemy for database interaction with PostgreSQL.
<End of file>
