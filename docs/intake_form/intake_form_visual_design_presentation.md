# Business Intake Form - Visual Design Presentation (v2 - Incorporating MCQs)

This document outlines the Figma-style visual design for the multi-step Business Intake Form. It incorporates both Multiple Choice Questions (MCQs) for baseline data and in-depth open-ended questions for qualitative insights, as per the finalized `intake_form_questions_v3.md`.

## I. Overall Design Philosophy & Goals

*   **Clarity & Simplicity:** The design will prioritize ease of understanding and use, minimizing cognitive load despite the comprehensive nature of the form.
*   **Professional & Trustworthy:** The aesthetic will be clean, modern, and professional, instilling confidence in the user.
*   **Guided Experience:** Users will be guided through the process step-by-step, with clear progress indicators and sectioning.
*   **Encouraging Completion:** Design elements will aim to motivate users to complete the form thoroughly (e.g., positive reinforcement, clear value proposition).
*   **Responsive Design:** The form will be designed to be accessible and usable across desktop and mobile devices.

## II. Key Screens & Components

### 1. Welcome / Introduction Screen

*   **Purpose:** To welcome the user, briefly explain the purpose of the intake form, highlight the value of completing it (i.e., a personalized AI-generated marketing blueprint), and set expectations regarding length/time (e.g., "This comprehensive form will take approximately 30-45 minutes to complete. Your detailed input is crucial for us to build you an effective blueprint.").
*   **Key Elements:**
    *   **Headline:** Engaging and welcoming (e.g., "Let's Build Your Business Blueprint").
    *   **Brief Introduction:** 2-3 sentences explaining the purpose and benefit.
    *   **Time Expectation:** Clearly stated.
    *   **Call to Action Button:** Prominent button (e.g., "Start Building My Blueprint" or "Begin Intake").
    *   **Visual:** A subtle, professional background image or graphic related to strategy/growth.

### 2. Main Intake Form Interface (Repeated for each of the 5 Sections)

*   **Layout:**
    *   **Header:** Consistent across all steps.
        *   Logo (Subtle, top left or right).
        *   Main Form Title (e.g., "AI Marketing System - Business Intake").
    *   **Progress Indicator:** Highly visible progress bar (e.g., "Section X of 5: [Section Name]") and potentially a step-within-section counter if sections are long.
    *   **Section Title:** Clearly displayed (e.g., "Section 1: The Heart of Your Business - Identity & Purpose").
    *   **Question Area:**
        *   **MCQ Subsection:** The 5 baseline MCQs for the current section will be presented first.
            *   Clear question numbering (e.g., 1.1, 1.2).
            *   Standard radio buttons or checkboxes for selection.
            *   Concise answer options.
        *   **Open-Ended Subsection:** Following the MCQs, the in-depth open-ended questions for the section will be presented.
            *   Clear question numbering (e.g., 1.6, 1.7).
            *   Larger text input areas (textarea) for detailed responses.
            *   Subtle prompts or guidance text within or below the input field if helpful (e.g., "Be as detailed as you like...").
            *   Consideration for rich text formatting if complex answers are expected (though simplicity is preferred).
    *   **Navigation:**
        *   "Next Section" or "Continue to Section X" button.
        *   "Previous Section" button (if applicable, allowing users to go back and edit).
        *   "Save and Exit" button: Allows users to save their progress and return later. This is crucial for a longer form.
*   **Styling:**
    *   **Typography:** Clean, readable sans-serif fonts.
    *   **Color Palette:** Professional and calm. Primary action buttons in a distinct, accessible color.
    *   **Spacing:** Ample white space to avoid a cluttered feel.

### 3. AI Assist Feature (Conceptual - for specific open-ended questions if implemented)

*   **Visual Cue:** A small, unobtrusive icon (e.g., a lightbulb or brain icon) next to certain open-ended questions where AI assistance might be offered (e.g., to help brainstorm or rephrase).
*   **Interaction:** Clicking the icon could open a modal or a small pop-up where the user can interact with an AI to refine their thoughts before committing to an answer. (This is a more advanced feature, initial implementation might omit this for simplicity).

### 4. Review & Interactive Summary Page (After all sections are completed)

*   **Purpose:** To allow the user to review all their answers before final submission and make any necessary edits.
*   **Layout:**
    *   **Title:** "Review Your Intake Information".
    *   **Organized Sections:** Answers clearly grouped by section, matching the intake form structure.
    *   **Question & Answer Display:** Each question shown with the user's provided answer below it.
        *   MCQ answers clearly displayed.
        *   Open-ended answers displayed in readable blocks.
    *   **Edit Functionality:** An "Edit" button or icon next to each question/section, allowing the user to jump back to that specific point in the form to make changes.
    *   **Call to Action Button:** Prominent button (e.g., "Submit for Blueprint Analysis" or "Finalize and Submit").

### 5. Submission Confirmation & Value Teaser Screen

*   **Purpose:** To confirm successful submission and reinforce the value of the upcoming blueprint.
*   **Key Elements:**
    *   **Confirmation Message:** Clear and positive (e.g., "Thank You! Your Business Intake is Complete.").
    *   **Next Steps:** Briefly explain what happens next (e.g., "Our AI Adaptation Agent is now analyzing your information to build your personalized marketing blueprint. You will be notified once it's ready.").
    *   **Value Teaser (Optional but Recommended):** A brief, exciting glimpse of what they can expect from the blueprint (e.g., "Get ready for actionable insights and strategies tailored to your unique business!").
    *   **Call to Action (Optional):** Link to a relevant resource, their account dashboard (if applicable), or a "Return to Homepage" button.

## III. Interaction & User Experience Notes

*   **Autosave:** Implement autosave functionality for open-ended fields as the user types, or at least when they navigate away from a field, to prevent data loss.
*   **Error Handling:** Clear, inline validation messages for required fields or incorrect data formats (though most fields will be text or selections).
*   **Loading States:** Visual feedback for any loading processes (e.g., saving, submitting).
*   **Accessibility:** Adherence to WCAG guidelines for colors, contrasts, keyboard navigation, and screen reader compatibility.

This textual description will guide the generation of AI image mockups for the key screens outlined above. The combination will provide a comprehensive Figma-style visual design for user approval before coding begins.

<End of file>
