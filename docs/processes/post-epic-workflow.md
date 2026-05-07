# Post-Epic Workflow Guidelines

This document outlines the standard operating procedure (SOP) that the team must follow upon the completion of all development stories within an Epic. This ensures consistent quality, operational readiness, and continuous improvement.

## Phase 1: Manual Validation & Testing
*Trigger: The developer marks the final story of the Epic as `done`.*

1. **Generate the Test Manual:**
   - QA (or a designated developer) copies `docs/templates/manual-test-template.md`.
   - Save the copy to `docs/qa/epic-[number]-test-manual.md`.
2. **Populate Scenarios:**
   - Translate the Acceptance Criteria from the Epic's stories into concrete, step-by-step test scenarios in the manual.
3. **Execute & Record:**
   - Run the tests manually in the local terminal or UI.
   - Record `PASS` or `FAIL` for each scenario. Document any console output or errors.
4. **Resolve Blockers:**
   - If any critical path scenarios fail, the Epic is *not* done. Developers must fix the bugs and QA must re-test before moving to Phase 2.

## Phase 2: The Retrospective
*Trigger: QA signs off on the Epic Test Manual.*

1. **Schedule the Session:**
   - Convene the project team (Product Owner, Developers, QA, Project Lead).
2. **Run the Question Set:**
   - The facilitator uses `docs/templates/retrospective-questions.md` to guide the discussion.
   - Ensure the conversation remains blameless and focuses on systemic improvements.
3. **Capture Action Items:**
   - Identify process improvements, technical debt, and required preparation tasks for the next Epic. Assign clear owners to every action item.

## Phase 3: Knowledge Transfer & Comprehension Check
*Trigger: Action items are captured.*

1. **Prepare the Knowledge Check:**
   - A Senior Developer copies `docs/templates/intern-knowledge-check.md` and tailors the 15 questions to the specific architectural and product decisions made during the Epic.
2. **Conduct the Review:**
   - The Intern/Junior Developer answers the questions (verbally or in writing).
   - The Senior Developer reviews the answers, corrects any misunderstandings, and explains the "why" behind the code.
3. **Sign-off:**
   - The Senior Developer signs off on the knowledge check, ensuring the intern understands the foundation before moving to the next Epic.

## Phase 4: Documentation & Handoff
*Trigger: The Knowledge Transfer session concludes.*

1. **Publish the Summary:**
   - The facilitator saves the retrospective summary (including metrics, answers, and action items) to `_bmad-output/implementation-artifacts/epic-[number]-retro-[date].md`.
2. **Update Sprint Status:**
   - Mark the retrospective key (e.g., `epic-1-retrospective: done`) in `_bmad-output/implementation-artifacts/sprint-status.yaml`.
3. **Address Significant Discoveries:**
   - If the retrospective revealed that assumptions for the next Epic are flawed, hold a planning review session to update the Epics document or Architecture before writing code.
4. **Kickoff Next Epic:**
   - Once preparation tasks are complete, begin creating stories for the next Epic.
